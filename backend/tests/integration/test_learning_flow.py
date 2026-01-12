"""
学习记录集成测试（Phase 2.2 - US1）

测试完整的学习记录流程、错题记录自动创建、数据加密等功能
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from app.models.database import (
    Base, LearningRecord, WrongAnswerRecord,
    Student, User, get_db, SessionLocal
)
from app.main import app
from app.core.security import EncryptionService


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_integration_sprout_chat.db"
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
        username="integration_test_parent",
        email="integration_parent@test.com",
        hashed_password="hashed_password",
        full_name="集成测试家长",
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
        name="集成测试学生",
        age=7,
        grade="一年级",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


class TestLearningFlowIntegration:
    """学习记录集成测试"""

    def test_complete_learning_flow(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试完整的学习记录流程

        验收场景：
        1. 创建学习记录（正确答案）
        2. 创建学习记录（错误答案，自动创建错题记录）
        3. 查询学习记录列表
        4. 获取学习进度统计
        5. 生成学习报告
        """
        # Step 1: 创建正确答案的学习记录
        request_data_correct = {
            "student_id": test_student.id,
            "question_content": "3 + 5 = ?",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "8",
            "correct_answer": "8",
            "time_spent_seconds": 15,
        }
        response = client.post("/api/v1/learning/records", json=request_data_correct)
        assert response.status_code == 201
        correct_record_id = response.json()["id"]

        # Step 2: 创建错误答案的学习记录（应自动创建错题记录）
        request_data_wrong = {
            "student_id": test_student.id,
            "question_content": "10 - 3 = ?",
            "question_type": "subtraction",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "6",
            "correct_answer": "7",
            "time_spent_seconds": 20,
        }
        response = client.post("/api/v1/learning/records", json=request_data_wrong)
        assert response.status_code == 201
        wrong_record_id = response.json()["id"]
        assert response.json()["is_correct"] is False

        # 验证错题记录已自动创建
        wrong_record = db_session.query(WrongAnswerRecord).filter(
            WrongAnswerRecord.learning_record_id == wrong_record_id
        ).first()
        assert wrong_record is not None
        assert wrong_record.error_type == "calculation"
        assert wrong_record.guidance_type == "hint"
        assert wrong_record.is_resolved is False

        # Step 3: 查询学习记录列表
        response = client.get(f"/api/v1/learning/records?student_id={test_student.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["records"]) == 2

        # Step 4: 获取学习进度统计
        response = client.get(f"/api/v1/learning/progress?student_id={test_student.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total_questions"] == 2
        assert data["correct_count"] == 1
        assert data["wrong_count"] == 1
        assert data["accuracy_rate"] == 50.0

        # Step 5: 生成学习报告
        # 注意：当前日期是 2026-01-12，所以使用 2026 年的日期范围
        response = client.get(
            f"/api/v1/learning/report?student_id={test_student.id}"
            f"&start_date=2026-01-01&end_date=2026-12-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == test_student.id
        assert data["summary"]["total_questions"] == 2
        assert "by_question_type" in data
        assert "by_difficulty_level" in data

    def test_wrong_answer_record_auto_creation(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试错题记录自动创建逻辑

        验收场景：
        - 创建错误答案的学习记录
        - 验证错题记录自动创建
        - 验证错题记录字段正确
        """
        # 创建错误答案的学习记录
        request_data = {
            "student_id": test_student.id,
            "question_content": "2 × 3 = ?",
            "question_type": "multiplication",
            "subject": "math",
            "difficulty_level": 2,
            "student_answer": "5",
            "correct_answer": "6",
            "time_spent_seconds": 25,
        }
        response = client.post("/api/v1/learning/records", json=request_data)
        assert response.status_code == 201
        record_id = response.json()["id"]

        # 查询关联的错题记录
        wrong_record = db_session.query(WrongAnswerRecord).filter(
            WrongAnswerRecord.learning_record_id == record_id
        ).first()

        assert wrong_record is not None
        assert wrong_record.learning_record_id == record_id
        assert wrong_record.error_type == "calculation"  # 默认错误类型
        assert wrong_record.guidance_type == "hint"  # 默认引导类型
        assert len(wrong_record.guidance_content) > 0  # 引导内容不为空
        assert wrong_record.is_resolved is False

    def test_data_encryption_decryption(
        self, client: TestClient, test_student: Student, db_session: Session
    ):
        """
        测试数据加密解密正确性

        验收场景：
        - 学生答案应被加密存储
        - 可以正确解密学生答案
        """
        # EncryptionService 需要 32 字节的原始密钥
        # 使用 os.urandom(32) 生成符合要求的密钥
        import os
        raw_key = os.urandom(32)  # 生成 32 字节随机密钥
        encryption_service = EncryptionService(key=raw_key)

        # 测试加密解密
        original_answer = "我的秘密答案"
        encrypted = encryption_service.encrypt(original_answer)
        decrypted = encryption_service.decrypt(encrypted)

        assert encrypted != original_answer  # 加密后不同
        assert decrypted == original_answer  # 解密后相同

        # 创建学习记录（学生答案会被加密存储）
        # TODO: 实际实现中需要应用加密
        request_data = {
            "student_id": test_student.id,
            "question_content": "测试加密题目",
            "question_type": "addition",
            "subject": "math",
            "difficulty_level": 1,
            "student_answer": "42",
            "correct_answer": "42",
            "time_spent_seconds": 10,
        }
        response = client.post("/api/v1/learning/records", json=request_data)
        assert response.status_code == 201

        # 验证记录已创建（加密部分待实现）
        record = db_session.query(LearningRecord).filter(
            LearningRecord.student_id == test_student.id
        ).first()
        assert record is not None
        # TODO: 验证 student_answer 字段已加密
        # assert record.student_answer != "42"

    def test_learning_record_detail_with_wrong_answer(
        self, client: TestClient, test_student: Student
    ):
        """
        测试获取学习记录详情（包含错题记录）

        验收场景：
        - 创建错误答案的学习记录
        - 获取记录详情应包含错题记录
        """
        # 创建错误答案的学习记录
        request_data = {
            "student_id": test_student.id,
            "question_content": "15 - 7 = ?",
            "question_type": "subtraction",
            "subject": "math",
            "difficulty_level": 2,
            "student_answer": "9",
            "correct_answer": "8",
            "time_spent_seconds": 30,
        }
        response = client.post("/api/v1/learning/records", json=request_data)
        assert response.status_code == 201
        record_id = response.json()["id"]

        # 获取记录详情
        response = client.get(f"/api/v1/learning/records/{record_id}")
        assert response.status_code == 200
        data = response.json()

        # 验证错题记录包含在详情中
        assert "wrong_answer_record" in data
        assert data["wrong_answer_record"] is not None
        assert data["wrong_answer_record"]["error_type"] == "calculation"
        assert data["wrong_answer_record"]["guidance_type"] == "hint"

    def test_progress_with_time_range_filtering(
        self, client: TestClient, test_student: Student
    ):
        """
        测试学习进度的时间范围筛选

        验收场景：
        - 创建多条学习记录
        - 使用不同时间范围查询进度
        - 验证统计数据正确
        """
        # 创建多条学习记录
        for i in range(5):
            request_data = {
                "student_id": test_student.id,
                "question_content": f"题目 {i}",
                "question_type": "addition",
                "subject": "math",
                "difficulty_level": 1,
                "student_answer": str(i),
                "correct_answer": str(i),
                "time_spent_seconds": 10 + i,
            }
            response = client.post("/api/v1/learning/records", json=request_data)
            assert response.status_code == 201

        # 查询所有时间的进度
        response = client.get(f"/api/v1/learning/progress?student_id={test_student.id}&time_range=all")
        assert response.status_code == 200
        data_all = response.json()
        assert data_all["total_questions"] == 5

        # 查询今天的进度
        response = client.get(f"/api/v1/learning/progress?student_id={test_student.id}&time_range=today")
        assert response.status_code == 200
        data_today = response.json()
        assert data_today["total_questions"] == 5  # 所有记录都是今天创建的

        # 查询本周的进度
        response = client.get(f"/api/v1/learning/progress?student_id={test_student.id}&time_range=week")
        assert response.status_code == 200
        data_week = response.json()
        assert data_week["total_questions"] == 5  # 所有记录都是本周创建的
