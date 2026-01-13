"""
脚手架持久化服务测试 (LWP-15)

测试 ScaffoldingPersistenceService 的所有功能
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base, get_db
from app.models.scaffolding import ScaffoldingLevelRecord, PerformanceMetric
from app.models.socratic import ScaffoldingLevel
from app.services.scaffolding_persistence import ScaffoldingPersistenceService


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_scaffolding.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=test_engine)

    # 创建会话
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理：删除所有表
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def persistence_service(db_session):
    """创建 ScaffoldingPersistenceService 实例"""
    return ScaffoldingPersistenceService(db_session)


class TestScaffoldingLevelTracking:
    """测试脚手架层级跟踪功能"""

    def test_get_current_level_for_new_student(self, persistence_service, db_session):
        """测试：新学生应该返回默认层级（moderate）"""
        # Given: 新学生 ID
        student_id = 999
        problem_domain = "math"

        # When: 获取当前层级
        level_record = persistence_service.get_current_level(student_id, problem_domain)

        # Then: 应该返回默认层级
        assert level_record is not None
        assert level_record.level == ScaffoldingLevel.MODERATE
        assert level_record.student_id == student_id
        assert level_record.problem_domain == problem_domain

    def test_update_scaffolding_level(self, persistence_service, db_session):
        """测试：更新脚手架层级"""
        # Given: 学生和当前层级
        student_id = 999
        problem_domain = "math"
        initial_record = persistence_service.get_current_level(student_id, problem_domain)
        assert initial_record.level == ScaffoldingLevel.MODERATE

        # When: 更新到 HIGHLY_GUIDED
        updated_record = persistence_service.update_level(
            student_id,
            problem_domain,
            ScaffoldingLevel.HIGHLY_GUIDED
        )

        # Then: 层级应该被更新
        assert updated_record.level == ScaffoldingLevel.HIGHLY_GUIDED
        assert updated_record.student_id == student_id
        assert updated_record.problem_domain == problem_domain

    def test_record_performance_metric(self, persistence_service, db_session):
        """测试：记录表现指标"""
        # Given: 学生和会话
        student_id = 999
        conversation_id = "conv_test_001"
        problem_domain = "math"
        scaffolding_level = ScaffoldingLevel.MODERATE

        # When: 记录表现
        metric = persistence_service.record_performance(
            student_id=student_id,
            conversation_id=conversation_id,
            problem_domain=problem_domain,
            is_correct=True,
            hints_needed=0,
            response_time_seconds=30.5,
            self_corrected=False,
            scaffolding_level_at_time=scaffolding_level,
            question_type="addition"
        )

        # Then: 指标应该被正确保存
        assert metric.id is not None
        assert metric.student_id == student_id
        assert metric.conversation_id == conversation_id
        assert metric.problem_domain == problem_domain
        assert metric.is_correct is True
        assert metric.hints_needed == 0
        assert metric.response_time_seconds == 30.5
        assert metric.self_corrected is False
        assert metric.scaffolding_level_at_time == scaffolding_level
        assert metric.question_type == "addition"

    def test_get_recent_metrics(self, persistence_service, db_session):
        """测试：获取最近的表现指标"""
        # Given: 学生和多个表现记录
        student_id = 999
        problem_domain = "math"

        # 创建 5 个表现记录
        for i in range(5):
            persistence_service.record_performance(
                student_id=student_id,
                conversation_id=f"conv_{i}",
                problem_domain=problem_domain,
                is_correct=i % 2 == 0,  # 交替正确/错误
                hints_needed=i,
                response_time_seconds=30.0 + i,
                self_corrected=i % 2 == 0,
                scaffolding_level_at_time=ScaffoldingLevel.MODERATE,
                question_type="addition"
            )

        # When: 获取最近 3 个指标
        recent_metrics = persistence_service.get_recent_metrics(
            student_id,
            problem_domain,
            limit=3
        )

        # Then: 应该返回最近的 3 个记录
        assert len(recent_metrics) == 3
        # 应该按时间倒序排列
        assert recent_metrics[0].conversation_id == "conv_4"
        assert recent_metrics[1].conversation_id == "conv_3"
        assert recent_metrics[2].conversation_id == "conv_2"

    def test_calculate_adjustment_three_correct(self, persistence_service, db_session):
        """测试：连续 3 个正确答案应该降级到 minimal"""
        # Given: 学生当前在 MODERATE 层级
        student_id = 999
        problem_domain = "math"
        persistence_service.get_current_level(student_id, problem_domain)

        # 记录 3 个连续正确答案
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

        # When: 计算调整
        recent_metrics = persistence_service.get_recent_metrics(student_id, problem_domain, limit=5)
        new_level = persistence_service.calculate_adjustment(
            student_id,
            problem_domain,
            recent_metrics
        )

        # Then: 应该降级到 MINIMAL
        assert new_level == ScaffoldingLevel.MINIMAL

    def test_calculate_adjustment_three_incorrect(self, persistence_service, db_session):
        """测试：连续 3 个错误答案应该升级到 highly_guided"""
        # Given: 学生当前在 MODERATE 层级
        student_id = 999
        problem_domain = "math"
        persistence_service.get_current_level(student_id, problem_domain)

        # 记录 3 个连续错误答案
        for i in range(3):
            persistence_service.record_performance(
                student_id=student_id,
                conversation_id=f"conv_{i}",
                problem_domain=problem_domain,
                is_correct=False,
                hints_needed=2,
                response_time_seconds=60.0,
                self_corrected=False,
                scaffolding_level_at_time=ScaffoldingLevel.MODERATE,
                question_type="addition"
            )

        # When: 计算调整
        recent_metrics = persistence_service.get_recent_metrics(student_id, problem_domain, limit=5)
        new_level = persistence_service.calculate_adjustment(
            student_id,
            problem_domain,
            recent_metrics
        )

        # Then: 应该升级到 HIGHLY_GUIDED
        assert new_level == ScaffoldingLevel.HIGHLY_GUIDED

    def test_calculate_adjustment_mixed_performance(self, persistence_service, db_session):
        """测试：混合表现应该维持当前层级"""
        # Given: 学生当前在 MODERATE 层级
        student_id = 999
        problem_domain = "math"
        persistence_service.get_current_level(student_id, problem_domain)

        # 记录混合表现（正确、错误、正确）
        performance_pattern = [True, False, True]
        for i, is_correct in enumerate(performance_pattern):
            persistence_service.record_performance(
                student_id=student_id,
                conversation_id=f"conv_{i}",
                problem_domain=problem_domain,
                is_correct=is_correct,
                hints_needed=0 if is_correct else 2,
                response_time_seconds=30.0,
                self_corrected=False,
                scaffolding_level_at_time=ScaffoldingLevel.MODERATE,
                question_type="addition"
            )

        # When: 计算调整
        recent_metrics = persistence_service.get_recent_metrics(student_id, problem_domain, limit=5)
        new_level = persistence_service.calculate_adjustment(
            student_id,
            problem_domain,
            recent_metrics
        )

        # Then: 应该维持 MODERATE
        assert new_level is None  # None 表示不需要调整

    def test_problem_domain_isolation(self, persistence_service, db_session):
        """测试：不同问题领域的层级应该独立"""
        # Given: 同一个学生
        student_id = 999

        # When: 设置不同领域的不同层级
        math_level = persistence_service.get_current_level(student_id, "math")
        persistence_service.update_level(student_id, "math", ScaffoldingLevel.MINIMAL)

        reading_level = persistence_service.get_current_level(student_id, "reading")
        persistence_service.update_level(student_id, "reading", ScaffoldingLevel.HIGHLY_GUIDED)

        # Then: 不同领域的层级应该独立
        math_level_retrieved = persistence_service.get_current_level(student_id, "math")
        reading_level_retrieved = persistence_service.get_current_level(student_id, "reading")

        assert math_level_retrieved.level == ScaffoldingLevel.MINIMAL
        assert reading_level_retrieved.level == ScaffoldingLevel.HIGHLY_GUIDED

    def test_get_performance_stats(self, persistence_service, db_session):
        """测试：获取表现统计"""
        # Given: 学生和多个表现记录
        student_id = 999
        problem_domain = "math"

        # 创建 5 个记录（3 正确，2 错误）
        for i in range(5):
            persistence_service.record_performance(
                student_id=student_id,
                conversation_id=f"conv_{i}",
                problem_domain=problem_domain,
                is_correct=i < 3,  # 前 3 个正确
                hints_needed=0,
                response_time_seconds=30.0,
                self_corrected=False,
                scaffolding_level_at_time=ScaffoldingLevel.MODERATE,
                question_type="addition"
            )

        # When: 获取统计
        stats = persistence_service.get_performance_stats(student_id, problem_domain)

        # Then: 统计应该正确
        assert stats["total_attempts"] == 5
        assert stats["correct_count"] == 3
        assert stats["accuracy"] == 0.6
        assert stats["avg_hints_needed"] == 0.0
