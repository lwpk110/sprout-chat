"""
脚手架持久化集成测试 (LWP-15)

测试脚手架持久化服务与对话流程的集成
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base
from app.models.scaffolding import ScaffoldingLevelRecord, PerformanceMetric
from app.models.socratic import ScaffoldingLevel
from app.services.scaffolding_persistence import ScaffoldingPersistenceService


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_scaffolding_integration.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# 覆盖数据库依赖
def override_get_db():
    """测试数据库会话"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.models.database import get_db


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 设置 dependency override
    app.dependency_overrides[get_db] = override_get_db
    # 每个测试前创建所有表
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 每个测试后删除所有表
        Base.metadata.drop_all(bind=test_engine)
        # 清理 dependency override
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client():
    """测试客户端"""
    with TestClient(app) as test_client:
        yield test_client


class TestScaffoldingIntegration:
    """测试脚手架持久化集成"""

    def test_end_to_end_scaffolding_adjustment(self, client, db_session):
        """测试：端到端的脚手架层级调整流程"""
        # Given: 学生 ID 和问题领域
        student_id = 100  # 使用独特的 ID 避免冲突
        problem_domain = "math"

        # 创建持久化服务
        persistence_service = ScaffoldingPersistenceService(db_session)

        # Step 1: 获取初始层级（应该是 MODERATE）
        initial_level = persistence_service.get_current_level(student_id, problem_domain)
        assert initial_level.level == ScaffoldingLevel.MODERATE

        # Step 2: 记录 3 个连续正确答案
        for i in range(3):
            persistence_service.record_performance(
                student_id=student_id,
                conversation_id=f"conv_{i}",
                problem_domain=problem_domain,
                is_correct=True,
                hints_needed=0,
                response_time_seconds=30.0,
                self_corrected=False,
                scaffolding_level_at_time=ScaffoldingLevel.MODERATE,
                question_type="addition"
            )

        # Step 3: 获取最近表现并计算调整
        recent_metrics = persistence_service.get_recent_metrics(student_id, problem_domain, limit=5)
        new_level = persistence_service.calculate_adjustment(
            student_id,
            problem_domain,
            recent_metrics
        )

        # Step 4: 验证应该降级到 MINIMAL
        assert new_level == ScaffoldingLevel.MINIMAL

        # Step 5: 应用调整
        updated_record = persistence_service.update_level(student_id, problem_domain, new_level)
        assert updated_record.level == ScaffoldingLevel.MINIMAL

        # Step 6: 通过 API 验证层级已更新
        response = client.get(
            f"/api/v1/scaffolding/students/{student_id}/level",
            params={"problem_domain": problem_domain}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "minimal"

    def test_cross_session_persistence(self, client, db_session):
        """测试：跨会话的脚手架层级持久化"""
        # Given: 学生 ID
        student_id = 101  # 使用独特的 ID 避免冲突
        problem_domain = "math"

        # 创建持久化服务
        persistence_service = ScaffoldingPersistenceService(db_session)

        # 会话 1: 记录表现并调整层级到 MINIMAL
        for i in range(3):
            persistence_service.record_performance(
                student_id=student_id,
                conversation_id=f"conv_1_{i}",
                problem_domain=problem_domain,
                is_correct=True,
                hints_needed=0,
                response_time_seconds=30.0,
                self_corrected=False,
                scaffolding_level_at_time=ScaffoldingLevel.MODERATE,
                question_type="addition"
            )

        recent_metrics = persistence_service.get_recent_metrics(student_id, problem_domain, limit=5)
        new_level = persistence_service.calculate_adjustment(student_id, problem_domain, recent_metrics)
        persistence_service.update_level(student_id, problem_domain, new_level)

        # 验证层级
        level_after_session_1 = persistence_service.get_current_level(student_id, problem_domain)
        assert level_after_session_1.level == ScaffoldingLevel.MINIMAL

        # 模拟会话结束，创建新的数据库会话
        db_session.close()
        new_db_session = TestSessionLocal()
        new_persistence_service = ScaffoldingPersistenceService(new_db_session)

        # 会话 2: 验证层级仍然存在（跨会话持久化）
        level_in_session_2 = new_persistence_service.get_current_level(student_id, problem_domain)
        assert level_in_session_2.level == ScaffoldingLevel.MINIMAL

        new_db_session.close()

    def test_performance_stats_aggregation(self, client, db_session):
        """测试：表现统计聚合功能"""
        # Given: 学生 ID
        student_id = 102  # 使用独特的 ID 避免冲突
        problem_domain = "math"

        # 创建持久化服务
        persistence_service = ScaffoldingPersistenceService(db_session)

        # 记录 5 个表现（3 正确，2 错误）
        for i in range(5):
            persistence_service.record_performance(
                student_id=student_id,
                conversation_id=f"conv_{i}",
                problem_domain=problem_domain,
                is_correct=i < 3,  # 前 3 个正确
                hints_needed=0 if i < 3 else 2,
                response_time_seconds=30.0 + i * 5,
                self_corrected=False,
                scaffolding_level_at_time=ScaffoldingLevel.MODERATE,
                question_type="addition"
            )

        # 获取统计
        stats = persistence_service.get_performance_stats(student_id, problem_domain)

        # 验证统计结果
        assert stats["total_attempts"] == 5
        assert stats["correct_count"] == 3
        assert stats["accuracy"] == 0.6
        assert stats["avg_hints_needed"] == 0.8  # (0*3 + 2*2) / 5

        # 通过 API 验证
        response = client.get(
            f"/api/v1/scaffolding/students/{student_id}/performance/stats",
            params={"problem_domain": problem_domain}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_attempts"] == 5
        assert data["accuracy"] == 0.6
