"""
知识点图谱集成测试（Phase 2.2 - US4 - T044）

TDD Phase: Green - 测试知识点图谱的完整流程
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from app.models.database import (
    Base, LearningRecord, KnowledgePoint, KnowledgePointMastery,
    Student, User, get_db, SessionLocal
)
from app.main import app


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_knowledge_graph.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    """测试数据库会话"""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session):
    """创建测试用户（家长）"""
    user = User(
        username="knowledge_test_parent",
        email="knowledge_parent@test.com",
        hashed_password="test_hash"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_student(db_session: Session, test_user: User):
    """创建测试学生"""
    student = Student(
        parent_id=test_user.id,
        name="知识点图谱测试学生",
        age=7,
        grade="一年级"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestKnowledgeGraphStructure:
    """测试知识点图谱结构"""

    def test_create_knowledge_points_with_dag(
        self, client: TestClient, db_session: Session
    ):
        """
        测试创建知识点 DAG 结构

        验收场景：
        1. 创建多个知识点，建立父子关系
        2. 获取知识点图谱
        3. 验证节点和边的关系正确
        """
        # 创建知识点：加法基础（无前置）
        kp1 = KnowledgePoint(
            name="加法基础",
            subject="math",
            difficulty_level=1,
            description="10 以内的加法运算",
            parent_id=None
        )
        db_session.add(kp1)

        # 创建知识点：减法基础（无前置）
        kp2 = KnowledgePoint(
            name="减法基础",
            subject="math",
            difficulty_level=1,
            description="10 以内的减法运算",
            parent_id=None
        )
        db_session.add(kp2)

        db_session.commit()

        # 获取知识点图谱
        response = client.get("/api/v1/knowledge-points/graph?subject=math")
        assert response.status_code == 200
        data = response.json()

        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 0  # 无前置关系，所以没有边

    def test_knowledge_points_with_prerequisites(
        self, client: TestClient, db_session: Session
    ):
        """
        测试知识点的前置依赖关系

        验收场景：
        1. 创建有前置依赖的知识点
        2. 获取知识点详情
        3. 验证前置知识点列表正确
        """
        # 创建前置知识点
        kp1 = KnowledgePoint(
            name="加法基础",
            subject="math",
            difficulty_level=1,
            description="10 以内的加法运算"
        )
        db_session.add(kp1)
        db_session.commit()

        # 创建依赖前知识点
        kp2 = KnowledgePoint(
            name="进位加法",
            subject="math",
            difficulty_level=2,
            description="20 以内的进位加法"
        )
        db_session.add(kp2)
        db_session.commit()

        # 设置前置关系（通过 relationship）
        kp2.prerequisites.append(kp1)
        db_session.commit()

        # 获取详情
        response = client.get(f"/api/v1/knowledge-points/{kp2.id}")
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "进位加法"
        assert len(data["prerequisites"]) == 1
        assert data["prerequisites"][0]["name"] == "加法基础"


class TestMasteryCalculation:
    """测试掌握度计算"""

    def test_calculate_mastery_from_learning_records(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试从学习记录计算掌握度

        验收场景：
        1. 创建知识点
        2. 创建多条学习记录（正确和错误）
        3. 计算掌握度
        4. 验证掌握度计算公式正确
        """
        # 创建知识点
        kp = KnowledgePoint(
            name="加法基础",
            subject="math",
            difficulty_level=1,
            description="10 以内的加法运算"
        )
        db_session.add(kp)
        db_session.commit()

        # 创建学习记录（5 正确，2 错误）
        for i in range(5):
            record = LearningRecord(
                student_id=test_student.id,
                question_content=f"{i} + {i+1} = ?",
                question_type="addition",
                subject="math",
                difficulty_level=1,
                student_answer=str(i + i + 1),
                correct_answer=str(i + i + 1),
                is_correct=True,
                answer_result="correct",
                time_spent_seconds=10,
                knowledge_point_id=kp.id
            )
            db_session.add(record)

        for i in range(2):
            record = LearningRecord(
                student_id=test_student.id,
                question_content=f"{i} + {i+2} = ?",
                question_type="addition",
                subject="math",
                difficulty_level=1,
                student_answer="99",
                correct_answer=str(i + i + 2),
                is_correct=False,
                answer_result="incorrect",
                time_spent_seconds=10,
                knowledge_point_id=kp.id
            )
            db_session.add(record)

        db_session.commit()

        # 计算掌握度
        from app.services.knowledge_tracker import KnowledgeTrackerService
        tracker = KnowledgeTrackerService()
        mastery = tracker.calculate_mastery_percentage(
            db=db_session,
            student_id=test_student.id,
            knowledge_point_id=kp.id
        )

        # 7 条记录，5 正确，正确率约 71.4%，加权计算约 57%
        assert 55 <= mastery <= 75  # 允许一定误差


class TestPrerequisitesCheck:
    """测试前置知识点检查"""

    def test_check_prerequisites_met(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试前置知识点是否满足

        验收场景：
        1. 创建知识点和前置知识点
        2. 学生掌握前置知识点
        3. 生成学习路径
        4. 验证前置检查正确
        """
        # 创建前置知识点
        kp1 = KnowledgePoint(
            name="加法基础",
            subject="math",
            difficulty_level=1,
            description="10 以内的加法运算"
        )
        db_session.add(kp1)
        db_session.commit()

        # 创建依赖前知识点
        kp2 = KnowledgePoint(
            name="进位加法",
            subject="math",
            difficulty_level=2,
            description="20 以内的进位加法"
        )
        db_session.add(kp2)
        db_session.commit()

        # 设置前置关系（通过 relationship）
        kp2.prerequisites.append(kp1)
        db_session.commit()

        # 学生掌握前置知识点
        mastery = KnowledgePointMastery(
            student_id=test_student.id,
            knowledge_point_id=kp1.id,
            mastery_percentage=85.0,
            status="mastered"
        )
        db_session.add(mastery)
        db_session.commit()

        # 生成学习路径
        response = client.get(
            f"/api/v1/knowledge-mastery/recommendations?student_id={test_student.id}"
        )
        assert response.status_code == 200
        data = response.json()

        # 验证学习路径包含两个知识点
        assert len(data["recommended_path"]) == 2

        # 进位加法应该标记为前置满足
        advanced_kp = next(
            (item for item in data["recommended_path"]
             if item["knowledge_point"]["name"] == "进位加法"),
            None
        )
        assert advanced_kp is not None
        assert advanced_kp["prerequisites_met"] is True


class TestLearningPathGeneration:
    """测试学习路径生成"""

    def test_generate_learning_path_by_difficulty(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试按难度生成学习路径

        验收场景：
        1. 创建不同难度的知识点
        2. 生成学习路径
        3. 验证路径按难度排序
        """
        # 创建不同难度的知识点
        for level in range(1, 4):
            kp = KnowledgePoint(
                name=f"知识点_{level}",
                subject="math",
                difficulty_level=level,
                description=f"难度 {level} 的知识点"
            )
            db_session.add(kp)

        db_session.commit()

        # 生成学习路径
        response = client.get(
            f"/api/v1/knowledge-mastery/recommendations?student_id={test_student.id}"
        )
        assert response.status_code == 200
        data = response.json()

        # 验证按难度排序
        difficulties = [item["order"] for item in data["recommended_path"]]
        assert difficulties == sorted(difficulties)


class TestMasteryUpdate:
    """测试掌握度更新"""

    def test_update_mastery_changes_status(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试更新掌握度改变状态

        验收场景：
        1. 创建知识点和掌握记录
        2. 更新掌握度
        3. 验证状态正确更新
        """
        # 创建知识点
        kp = KnowledgePoint(
            name="加法基础",
            subject="math",
            difficulty_level=1,
            description="10 以内的加法运算"
        )
        db_session.add(kp)
        db_session.commit()

        # 创建初始掌握记录
        mastery = KnowledgePointMastery(
            student_id=test_student.id,
            knowledge_point_id=kp.id,
            mastery_percentage=50.0,
            status="in_progress"
        )
        db_session.add(mastery)
        db_session.commit()

        # 更新掌握度为已掌握
        update_request = {
            "mastery_percentage": 85.0
        }
        response = client.patch(
            f"/api/v1/knowledge-mastery/{mastery.id}",
            json=update_request
        )
        assert response.status_code == 200
        data = response.json()

        assert data["mastery_percentage"] == 85.0
        assert data["status"] == "mastered"

        # 验证数据库已更新
        db_session.refresh(mastery)
        assert mastery.mastery_percentage == 85.0
        assert mastery.status == "mastered"
