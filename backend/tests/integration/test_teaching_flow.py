"""
引导教学集成测试（Phase 2.2 - US2 - T026）

TDD Phase: Green - 测试完整的引导教学流程
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from app.models.database import (
    Base, LearningRecord, WrongAnswerRecord,
    Student, User, get_db, SessionLocal
)
from app.main import app


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_teaching_flow.db"
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
        username="teaching_test_parent",
        email="teaching_parent@test.com",
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
        name="引导教学测试学生",
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


class TestTeachingFlow:
    """测试完整的引导教学流程"""

    def test_complete_guidance_flow(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试完整的引导教学流程

        验收场景：
        1. 学生答错题目
        2. 系统自动分类错误类型
        3. 系统生成引导式反馈
        4. 验证引导式反馈不包含答案
        5. 学生再次尝试
        """
        # Step 1: 创建错误答案的学习记录
        request_data = {
            "student_id": test_student.id,
            "question_content": "3 + 5 = ?",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "7",
            "correct_answer": "8",
            "time_spent_seconds": 15
        }
        response = client.post("/api/v1/learning/records", json=request_data)
        assert response.status_code == 201
        data = response.json()
        assert data["is_correct"] is False

        learning_record_id = data["id"]

        # Step 2: 生成引导式反馈
        guidance_request = {
            "question": "3 + 5 = ?",
            "student_answer": "7",
            "correct_answer": "8",
            "attempts": 1
        }
        guidance_response = client.post("/api/v1/teaching/guidance", json=guidance_request)
        assert guidance_response.status_code == 200
        guidance_data = guidance_response.json()

        assert guidance_data["guidance_type"] in ["hint", "check_work"]
        assert len(guidance_data["content"]) > 0
        assert guidance_data["metadata"]["error_type"] == "calculation"

        guidance_content = guidance_data["content"]

        # Step 3: 验证引导式反馈不包含答案
        validate_request = {
            "response": guidance_content,
            "question": "3 + 5 = ?",
            "correct_answer": "8"
        }
        validate_response = client.post("/api/v1/teaching/guidance/validate", json=validate_request)
        assert validate_response.status_code == 200
        validate_data = validate_response.json()

        assert validate_data["valid"] is True
        assert validate_data["layer"] == 3

        # Step 4: 学生第二次尝试（仍然错误）
        request_data_2 = {
            "student_id": test_student.id,
            "question_content": "3 + 5 = ?",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "6",
            "correct_answer": "8",
            "time_spent_seconds": 10
        }
        response_2 = client.post("/api/v1/learning/records", json=request_data_2)
        assert response_2.status_code == 201

        # Step 5: 生成更强的引导（多次尝试后）
        guidance_request_2 = {
            "question": "3 + 5 = ?",
            "student_answer": "6",
            "correct_answer": "8",
            "attempts": 2
        }
        guidance_response_2 = client.post("/api/v1/teaching/guidance", json=guidance_request_2)
        assert guidance_response_2.status_code == 200
        guidance_data_2 = guidance_response_2.json()

        # 第二次尝试可能仍然使用 hint，但第三次应该使用更强的引导
        assert guidance_data_2["guidance_type"] in ["hint", "check_work", "break_down"]

        # Step 6: 学生第三次尝试（使用更直接的引导）
        guidance_request_3 = {
            "question": "3 + 5 = ?",
            "student_answer": "9",
            "correct_answer": "8",
            "attempts": 3
        }
        guidance_response_3 = client.post("/api/v1/teaching/guidance", json=guidance_request_3)
        assert guidance_response_3.status_code == 200
        guidance_data_3 = guidance_response_3.json()

        # 多次尝试后应使用更直接的引导
        assert guidance_data_3["guidance_type"] in ["break_down", "visualize"]

    def test_concept_error_guidance_flow(
        self, client: TestClient, test_student: Student
    ):
        """
        测试概念错误的引导教学流程

        验收场景：
        给定学生混淆减法为加法（5-3=8）
        那么系统应识别为概念错误并生成澄清型引导
        """
        guidance_request = {
            "question": "你有 5 个苹果，吃掉 3 个，还剩几个？",
            "student_answer": "8",
            "correct_answer": "2",
            "attempts": 1
        }
        response = client.post("/api/v1/teaching/guidance", json=guidance_request)

        assert response.status_code == 200
        data = response.json()

        assert data["metadata"]["error_type"] == "concept"
        assert data["guidance_type"] in ["clarify", "break_down"]

        # 验证引导不包含答案
        validate_request = {
            "response": data["content"],
            "question": guidance_request["question"],
            "correct_answer": guidance_request["correct_answer"]
        }
        validate_response = client.post("/api/v1/teaching/guidance/validate", json=validate_request)

        assert validate_response.status_code == 200
        validate_data = validate_response.json()
        assert validate_data["valid"] is True

    def test_understanding_error_guidance_flow(
        self, client: TestClient, test_student: Student
    ):
        """
        测试理解错误的引导教学流程

        验收场景：
        给定"一共"问题用减法（一共有几个答2）
        那么系统应识别为理解错误并生成澄清型引导
        """
        guidance_request = {
            "question": "小明有 5 个苹果，小红有 3 个苹果，他们一共有多少个？",
            "student_answer": "2",
            "correct_answer": "8",
            "attempts": 1
        }
        response = client.post("/api/v1/teaching/guidance", json=guidance_request)

        assert response.status_code == 200
        data = response.json()

        # "一共"问题用减法应分类为 understanding 错误
        assert data["metadata"]["error_type"] == "understanding"
        assert data["guidance_type"] == "clarify"

        # 验证引导不包含答案
        validate_request = {
            "response": data["content"],
            "question": guidance_request["question"],
            "correct_answer": guidance_request["correct_answer"]
        }
        validate_response = client.post("/api/v1/teaching/guidance/validate", json=validate_request)

        assert validate_response.status_code == 200
        validate_data = validate_response.json()
        assert validate_data["valid"] is True

    def test_guidance_validation_fallback(
        self, client: TestClient, test_student: Student
    ):
        """
        测试引导验证失败时的后备处理

        验收场景：
        给定引导式响应包含直接答案
        那么系统应使用安全的后备引导
        """
        # 模拟包含答案的响应
        malicious_response = "让我来帮你。答案是 8，你应该记住这个。"

        validate_request = {
            "response": malicious_response,
            "question": "3 + 5 = ?",
            "correct_answer": "8"
        }
        response = client.post("/api/v1/teaching/guidance/validate", json=validate_request)

        assert response.status_code == 200
        data = response.json()

        assert data["valid"] is False
        assert "contains_answer" in data["reason"] or "keyword" in data["reason"]

    def test_get_all_guidance_types(
        self, client: TestClient
    ):
        """
        测试获取所有引导类型

        验收场景：
        当请求获取引导类型列表
        那么系统应返回所有 7 种引导类型及其说明
        """
        response = client.get("/api/v1/teaching/guidance/types")

        assert response.status_code == 200
        data = response.json()

        assert "guidance_types" in data
        guidance_types = data["guidance_types"]
        assert len(guidance_types) == 7

        # 验证包含所有 7 种类型
        type_codes = [gt["type"] for gt in guidance_types]
        expected_types = [
            "clarify",
            "hint",
            "break_down",
            "visualize",
            "check_work",
            "alternative_method",
            "encourage"
        ]
        for expected in expected_types:
            assert expected in type_codes


class TestGuidanceStrategyAdjustment:
    """测试引导策略调整"""

    def test_multiple_attempts_strategy_change(
        self, client: TestClient, test_student: Student
    ):
        """
        测试多次尝试后的策略调整

        验收场景：
        给定学生连续答错 3 次
        那么系统应使用更直接的引导类型（break_down 或 visualize）
        """
        # 第一次尝试
        guidance_1 = client.post("/api/v1/teaching/guidance", json={
            "question": "15 - 7 = ?",
            "student_answer": "9",
            "correct_answer": "8",
            "attempts": 1
        })
        assert guidance_1.status_code == 200
        data_1 = guidance_1.json()
        # 首次尝试使用 hint 或 check_work
        assert data_1["guidance_type"] in ["hint", "check_work"]

        # 第三次尝试
        guidance_3 = client.post("/api/v1/teaching/guidance", json={
            "question": "15 - 7 = ?",
            "student_answer": "9",
            "correct_answer": "8",
            "attempts": 3
        })
        assert guidance_3.status_code == 200
        data_3 = guidance_3.json()
        # 多次尝试后使用 break_down 或 visualize
        assert data_3["guidance_type"] in ["break_down", "visualize"]

    def test_careless_error_encouragement(
        self, client: TestClient, test_student: Student
    ):
        """
        测试粗心错误的鼓励策略

        验收场景：
        给定学生答案与正确答案非常接近（差 1）
        那么系统应使用鼓励型或检查型引导
        """
        guidance_request = {
            "question": "100 - 1 = ?",
            "student_answer": "99",
            "correct_answer": "98",
            "attempts": 1
        }
        response = client.post("/api/v1/teaching/guidance", json=guidance_request)

        assert response.status_code == 200
        data = response.json()

        # 相差 1 且正确答案 >= 10 应分类为 careless
        assert data["metadata"]["error_type"] == "careless"
        assert data["guidance_type"] in ["check_work", "encourage"]
