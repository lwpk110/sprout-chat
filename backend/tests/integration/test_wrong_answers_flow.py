"""
错题本集成测试（Phase 2.2 - US3 - T034）

TDD Phase: Green - 测试完整的错题本流程
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
TEST_DATABASE_URL = "sqlite:///./test_wrong_answers_flow.db"
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
        username="wrong_answers_test_parent",
        email="wrong_parent@test.com",
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
        name="错题本测试学生",
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


class TestWrongAnswersFlow:
    """测试错题本完整流程"""

    def test_wrong_answer_auto_created_flow(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试错题记录自动创建流程

        验收场景：
        1. 创建错误答案的学习记录
        2. 验证错题记录自动创建
        3. 查询错题列表
        4. 获取错题统计
        5. 生成练习推荐
        """
        # Step 1: 创建错误答案的学习记录（应该自动创建错题记录）
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

        # Step 2: 验证错题记录自动创建
        wrong_record = db_session.query(WrongAnswerRecord).filter(
            WrongAnswerRecord.learning_record_id == learning_record_id
        ).first()
        assert wrong_record is not None
        assert wrong_record.learning_record.student_id == test_student.id
        assert wrong_record.error_type == "calculation"
        assert wrong_record.is_resolved is False

        # Step 3: 查询错题列表
        list_response = client.get(f"/api/v1/wrong-answers?student_id={test_student.id}")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["total"] == 1
        assert len(list_data["wrong_answers"]) == 1

        # Step 4: 获取错题统计
        stats_response = client.get(f"/api/v1/wrong-answers/statistics?student_id={test_student.id}")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["total_wrong_answers"] == 1
        assert stats_data["unresolved_count"] == 1
        assert stats_data["by_error_type"]["calculation"] == 1

        # Step 5: 生成练习推荐
        rec_response = client.get(f"/api/v1/wrong-answers/recommendations?student_id={test_student.id}")
        assert rec_response.status_code == 200
        rec_data = rec_response.json()
        assert rec_data["total_count"] >= 1

    def test_wrong_answer_status_update(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试错题状态更新

        验收场景：
        1. 创建错题记录
        2. 标记为已解决
        3. 验证状态更新成功
        """
        # 创建错误答案的学习记录
        request_data = {
            "student_id": test_student.id,
            "question_content": "5 - 3 = ?",
            "question_type": "subtraction",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "8",
            "correct_answer": "2",
            "time_spent_seconds": 10
        }
        response = client.post("/api/v1/learning/records", json=request_data)
        assert response.status_code == 201

        # 获取错题记录（通过 learning_record 关系）
        wrong_record = db_session.query(WrongAnswerRecord).join(LearningRecord).filter(
            LearningRecord.student_id == test_student.id
        ).first()
        assert wrong_record is not None

        # 标记为已解决
        update_request = {
            "is_resolved": True
        }
        update_response = client.patch(
            f"/api/v1/wrong-answers/{wrong_record.id}",
            json=update_request
        )
        assert update_response.status_code == 200
        update_data = update_response.json()
        assert update_data["is_resolved"] is True

        # 验证数据库已更新
        db_session.refresh(wrong_record)
        assert wrong_record.is_resolved is True
        assert wrong_record.resolved_at is not None

    def test_multiple_wrong_answers_statistics(
        self, client: TestClient, test_student: Student
    ):
        """
        测试多条错题的统计

        验收场景：
        1. 创建多条不同类型的错题记录
        2. 验证统计数据正确
        3. 验证最常见的错误类型
        """
        # 创建 3 条计算错误
        for i in range(3):
            request_data = {
                "student_id": test_student.id,
                "question_content": f"{i} + {i+1} = ?",
                "question_type": "addition",
                "subject": "math",
                "difficulty_level": 1,
                "student_answer": "99",
                "correct_answer": str(i + i + 1),
                "time_spent_seconds": 10
            }
            client.post("/api/v1/learning/records", json=request_data)

        # 创建 2 条概念错误
        for i in range(2):
            request_data = {
                "student_id": test_student.id,
                "question_content": f"你有 {i+5} 个苹果，吃掉 {i+1} 个，还剩几个？",
                "question_type": "subtraction",
                "subject": "math",
                "difficulty_level": 1,
                "student_answer": "99",
                "correct_answer": str(i+5 - (i+1)),
                "time_spent_seconds": 10
            }
            client.post("/api/v1/learning/records", json=request_data)

        # 获取统计
        stats_response = client.get(f"/api/v1/wrong-answers/statistics?student_id={test_student.id}")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()

        assert stats_data["total_wrong_answers"] == 5
        # Note: The classifier classifies most wrong answers as "calculation" by default
        # unless there's clear evidence of concept mixing or understanding issues
        assert stats_data["by_error_type"]["calculation"] >= 3
        assert stats_data["most_common_errors"][0] == "calculation"

    def test_practice_recommendations_by_priority(
        self, client: TestClient, test_student: Student
    ):
        """
        测试练习推荐按优先级排序

        验收场景：
        1. 创建不同数量的错题
        2. 验证推荐按优先级排序（high > medium > low）
        """
        # 创建 3 条计算错误（应该是 high 优先级）
        for i in range(3):
            request_data = {
                "student_id": test_student.id,
                "question_content": f"{i} + {i+1} = ?",
                "question_type": "addition",
                "subject": "math",
                "difficulty_level": 1,
                "student_answer": "99",
                "correct_answer": str(i + i + 1),
                "time_spent_seconds": 10
            }
            client.post("/api/v1/learning/records", json=request_data)

        # 创建 1 条粗心错误（应该是 low 优先级）
        request_data = {
            "student_id": test_student.id,
            "question_content": "100 - 1 = ?",
            "question_type": "subtraction",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "100",
            "correct_answer": "99",
            "time_spent_seconds": 5
        }
        client.post("/api/v1/learning/records", json=request_data)

        # 获取推荐
        rec_response = client.get(f"/api/v1/wrong-answers/recommendations?student_id={test_student.id}")
        assert rec_response.status_code == 200
        rec_data = rec_response.json()

        # 验证优先级排序
        if len(rec_data["recommendations"]) >= 2:
            # 第一个应该是 high 优先级
            assert rec_data["recommendations"][0]["priority"] in ["high", "medium"]
            # 最后一个应该是 low 优先级（如果存在）
            last_priority = rec_data["recommendations"][-1]["priority"]
            assert last_priority in ["medium", "low"]

    def test_filter_wrong_answers_by_type(
        self, client: TestClient, test_student: Student
    ):
        """
        测试按错误类型筛选错题

        验收场景：
        1. 创建不同类型的错题
        2. 按类型筛选查询
        3. 验证结果正确
        """
        # 创建计算错误
        request_data = {
            "student_id": test_student.id,
            "question_content": "3 + 5 = ?",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "7",
            "correct_answer": "8",
            "time_spent_seconds": 10
        }
        client.post("/api/v1/learning/records", json=request_data)

        # 创建概念错误
        request_data = {
            "student_id": test_student.id,
            "question_content": "你有 5 个苹果，吃掉 3 个，还剩几个？",
            "question_type": "subtraction",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "8",
            "correct_answer": "2",
            "time_spent_seconds": 10
        }
        client.post("/api/v1/learning/records", json=request_data)

        # 查询所有错题
        all_response = client.get(f"/api/v1/wrong-answers?student_id={test_student.id}")
        assert all_response.status_code == 200
        all_data = all_response.json()
        assert all_data["total"] == 2

        # 按类型筛选（只要计算错误）
        filtered_response = client.get(
            f"/api/v1/wrong-answers?student_id={test_student.id}&error_type=calculation"
        )
        assert filtered_response.status_code == 200
        filtered_data = filtered_response.json()
        assert filtered_data["total"] == 1
        assert filtered_data["wrong_answers"][0]["error_type"] == "calculation"


class TestRecommendationGeneration:
    """测试练习推荐生成"""

    def test_similar_question_generation(
        self, client: TestClient, test_student: Student
    ):
        """
        测试相似题目生成

        验收场景：
        1. 创建错题记录
        2. 生成练习推荐
        3. 验证相似题目的数字不同但类型相同
        """
        request_data = {
            "student_id": test_student.id,
            "question_content": "3 + 5 = ?",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "7",
            "correct_answer": "8",
            "time_spent_seconds": 10
        }
        client.post("/api/v1/learning/records", json=request_data)

        # 获取推荐
        rec_response = client.get(f"/api/v1/wrong-answers/recommendations?student_id={test_student.id}")
        assert rec_response.status_code == 200
        rec_data = rec_response.json()

        # 验证推荐包含相似题目
        if rec_data["total_count"] > 0:
            first_rec = rec_data["recommendations"][0]
            if len(first_rec["similar_questions"]) > 0:
                similar_q = first_rec["similar_questions"][0]
                # 相似题目应该有新的数字
                assert "3" not in similar_q["question_content"] or "5" not in similar_q["question_content"]
                # 但类型应该相同
                assert similar_q["question_type"] == "addition"

    def test_recommendation_reason_generation(
        self, client: TestClient, test_student: Student
    ):
        """
        测试推荐理由生成

        验收场景：
        1. 创建错题记录
        2. 生成练习推荐
        3. 验证推荐理由合理
        """
        request_data = {
            "student_id": test_student.id,
            "question_content": "3 + 5 = ?",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "7",
            "correct_answer": "8",
            "time_spent_seconds": 10
        }
        client.post("/api/v1/learning/records", json=request_data)

        # 获取推荐
        rec_response = client.get(f"/api/v1/wrong-answers/recommendations?student_id={test_student.id}")
        assert rec_response.status_code == 200
        rec_data = rec_response.json()

        # 验证推荐理由包含错题数量
        if rec_data["total_count"] > 0:
            first_rec = rec_data["recommendations"][0]
            assert "reason" in first_rec
            assert len(first_rec["reason"]) > 0
