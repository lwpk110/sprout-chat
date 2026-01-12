"""
学习记录 API 单元测试（Phase 2.2 - US1）

TDD Phase: Red - 先写失败的测试
测试学习记录的创建、查询、统计和报告功能
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.database import Base, LearningRecord, Student, User
from app.main import app


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_sprout_chat.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session: Session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from app.models.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session):
    """创建测试用户（家长）"""
    user = User(
        username="test_parent",
        email="parent@test.com",
        hashed_password="hashed_password",
        full_name="测试家长",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_student(db_session: Session, test_user: User):
    """创建测试学生"""
    student = Student(
        parent_id=test_user.id,
        name="测试学生",
        age=7,
        grade="一年级",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


class TestLearningRecordAPI:
    """学习记录 API 测试"""

    def test_create_learning_record_correct_answer(
        self, client: TestClient, test_student: Student
    ):
        """
        测试创建学习记录（正确答案）

        验收场景 1：
        给定学生完成"3 + 5 = ?"，提交答案"8"
        那么系统应记录：问题、答案"8"、是否正确=true、耗时=15秒
        """
        request_data = {
            "student_id": test_student.id,
            "question_content": "3 + 5 = ?",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "8",
            "correct_answer": "8",
            "time_spent_seconds": 15,
        }

        response = client.post("/api/v1/learning/records", json=request_data)

        # 验证响应
        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == test_student.id
        assert data["question_content"] == "3 + 5 = ?"
        assert data["student_answer"] == "8"
        assert data["correct_answer"] == "8"
        assert data["is_correct"] is True
        assert data["time_spent_seconds"] == 15
        assert "id" in data

    def test_create_learning_record_wrong_answer(
        self, client: TestClient, test_student: Student
    ):
        """
        测试创建学习记录（错误答案）

        验收场景 2：
        给定学生提交错误答案"7"
        那么系统应记录错误答案，并创建错题记录
        """
        request_data = {
            "student_id": test_student.id,
            "question_content": "3 + 5 = ?",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "7",
            "correct_answer": "8",
            "time_spent_seconds": 20,
        }

        response = client.post("/api/v1/learning/records", json=request_data)

        # 验证响应
        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == test_student.id
        assert data["student_answer"] == "7"
        assert data["is_correct"] is False
        # 错题记录应该在详情中返回
        # TODO: 验证错题记录创建

    def test_list_learning_records(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试查询学习记录列表

        验证：
        - 可以按学生 ID 查询
        - 支持按时间范围筛选
        - 支持按题型筛选
        """
        # 创建测试数据
        record1 = LearningRecord(
            student_id=test_student.id,
            question_content="3 + 5 = ?",
            question_type="addition",
            subject="math",
            difficulty_level=1,
            student_answer="8",
            correct_answer="8",
            is_correct=True,
            answer_result="correct",
            time_spent_seconds=15,
            created_at=datetime(2025, 1, 10, 10, 0, 0),
        )
        record2 = LearningRecord(
            student_id=test_student.id,
            question_content="10 - 3 = ?",
            question_type="subtraction",
            subject="math",
            difficulty_level=1,
            student_answer="7",
            correct_answer="7",
            is_correct=True,
            answer_result="correct",
            time_spent_seconds=20,
            created_at=datetime(2025, 1, 12, 10, 0, 0),
        )
        db_session.add(record1)
        db_session.add(record2)
        db_session.commit()

        # 查询所有记录
        response = client.get(f"/api/v1/learning/records?student_id={test_student.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["records"]) == 2

        # 按题型筛选
        response = client.get(
            f"/api/v1/learning/records?student_id={test_student.id}&question_type=addition"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["records"][0]["question_type"] == "addition"

    def test_get_learning_progress(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试获取学习进度统计

        验收场景 3：
        给定系统记录了 50 道题目
        那么系统应生成包含：总题数、正确率、连续答对次数等的报告
        """
        # 创建测试数据：40 正确，10 错误
        for i in range(40):
            db_session.add(
                LearningRecord(
                    student_id=test_student.id,
                    question_content=f"Question {i}",
                    question_type="addition",
                    subject="math",
                    difficulty_level=1,
                    student_answer="correct",
                    correct_answer="correct",
                    is_correct=True,
                    answer_result="correct",
                    time_spent_seconds=15 + i,
                )
            )
        for i in range(10):
            db_session.add(
                LearningRecord(
                    student_id=test_student.id,
                    question_content=f"Wrong Question {i}",
                    question_type="subtraction",
                    subject="math",
                    difficulty_level=1,
                    student_answer="wrong",
                    correct_answer="correct",
                    is_correct=False,
                    answer_result="incorrect",
                    time_spent_seconds=20 + i,
                )
            )
        db_session.commit()

        # 查询学习进度
        response = client.get(f"/api/v1/learning/progress?student_id={test_student.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == test_student.id
        assert data["total_questions"] == 50
        assert data["correct_count"] == 40
        assert data["wrong_count"] == 10
        assert data["accuracy_rate"] == 80.0

    def test_generate_learning_report(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试生成学习进度报告

        验收场景 3：
        给定系统记录了学习数据
        那么系统应生成包含：按题型分布、按难度分布等指标的报告
        """
        # 创建测试数据
        for i in range(20):
            db_session.add(
                LearningRecord(
                    student_id=test_student.id,
                    question_content=f"Addition {i}",
                    question_type="addition",
                    subject="math",
                    difficulty_level=1,
                    student_answer="correct",
                    correct_answer="correct",
                    is_correct=True,
                    answer_result="correct",
                    time_spent_seconds=15,
                    created_at=datetime(2025, 1, 10, 10, 0, 0),
                )
            )
        for i in range(10):
            db_session.add(
                LearningRecord(
                    student_id=test_student.id,
                    question_content=f"Subtraction {i}",
                    question_type="subtraction",
                    subject="math",
                    difficulty_level=2,
                    student_answer="correct",
                    correct_answer="correct",
                    is_correct=True,
                    answer_result="correct",
                    time_spent_seconds=20,
                    created_at=datetime(2025, 1, 12, 10, 0, 0),
                )
            )
        db_session.commit()

        # 生成报告
        response = client.get(
            f"/api/v1/learning/report?student_id={test_student.id}"
            f"&start_date=2025-01-01&end_date=2025-01-15"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == test_student.id
        assert data["summary"]["total_questions"] == 30
        assert "by_question_type" in data
        assert "by_difficulty_level" in data

    def test_get_learning_record_detail(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """测试获取学习记录详情"""
        # 创建测试记录
        record = LearningRecord(
            student_id=test_student.id,
            question_content="3 + 5 = ?",
            question_type="addition",
            subject="math",
            difficulty_level=1,
            student_answer="8",
            correct_answer="8",
            is_correct=True,
            answer_result="correct",
            time_spent_seconds=15,
        )
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        # 查询详情
        response = client.get(f"/api/v1/learning/records/{record.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == record.id
        assert data["question_content"] == "3 + 5 = ?"
