"""
测试学生表现分析服务 (LWP-17)

测试覆盖：
- 性能数据收集点
- 指标计算（成功率、引导效率、学习速度、信心水平）
- 趋势检测（平台期、突破、困难模式）
- 实时指标检索
"""
import pytest
from datetime import datetime, timedelta
from app.services.performance_analytics import PerformanceAnalyticsService
from app.models.analytics import (
    PerformanceEvent,
    PerformanceMetrics,
    TrendAnalysis,
    LearningPlateau,
    BreakthroughMoment,
    StrugglePattern
)


class TestDataCollection:
    """测试性能数据收集"""

    @pytest.mark.asyncio
    async def test_collect_correct_answer_event(self, analytics_service):
        """
        测试：收集正确答案事件

        Given: 学生在苏格拉底引导后提供了正确答案
        When: 记录这个性能事件
        Then: 事件应包含时间戳、学生ID、问题类型、答案正确性
        """
        event = await analytics_service.record_performance_event(
            student_id="student_001",
            problem_type="addition",
            event_type="answer_given",
            is_correct=True,
            hints_needed=1,
            guidance_received=True,
            response_time_seconds=8.5
        )

        assert event.student_id == "student_001"
        assert event.problem_type == "addition"
        assert event.is_correct is True
        assert event.hints_needed == 1
        assert event.guidance_received is True
        assert event.response_time_seconds == 8.5
        assert event.timestamp is not None

    @pytest.mark.asyncio
    async def test_collect_hint_request_event(self, analytics_service):
        """
        测试：收集提示请求事件

        Given: 学生请求额外提示
        When: 记录这个事件
        Then: 事件应标记为困惑信号
        """
        event = await analytics_service.record_performance_event(
            student_id="student_001",
            problem_type="subtraction",
            event_type="hint_requested",
            is_correct=None,
            hints_needed=1,
            guidance_received=True,
            response_time_seconds=5.0
        )

        assert event.event_type == "hint_requested"
        assert event.is_correct is None  # 尚未回答

    @pytest.mark.asyncio
    async def test_collect_self_correction_event(self, analytics_service):
        """
        测试：收集自我修正事件

        Given: 学生在引导式问题后自我修正
        When: 记录这个事件
        Then: 事件应标记为理解的强信号
        """
        event = await analytics_service.record_performance_event(
            student_id="student_001",
            problem_type="multiplication",
            event_type="self_correction",
            is_correct=True,
            hints_needed=0,
            guidance_received=True,
            response_time_seconds=12.0,
            self_corrected=True
        )

        assert event.self_corrected is True
        assert event.is_correct is True


class TestMetricsCalculation:
    """测试指标计算"""

    @pytest.mark.asyncio
    async def test_calculate_success_rate(self, analytics_service):
        """
        测试：计算成功率

        Given: 学生有 10 次尝试，其中 7 次正确
        When: 计算成功率
        Then: 应返回 0.7 (70%)
        """
        # 模拟 10 次尝试
        for i in range(10):
            await analytics_service.record_performance_event(
                student_id="student_001",
                problem_type="addition",
                event_type="answer_given",
                is_correct=(i < 7),  # 前 7 次正确
                hints_needed=0,
                guidance_received=True,
                response_time_seconds=5.0
            )

        metrics = await analytics_service.calculate_success_rate(
            student_id="student_001",
            problem_type="addition"
        )

        assert metrics.success_rate == 0.7
        assert metrics.total_attempts == 10
        assert metrics.correct_answers == 7

    @pytest.mark.asyncio
    async def test_calculate_guidance_efficiency(self, analytics_service):
        """
        测试：计算引导效率

        Given: 学生平均需要 1.5 个提示来解决问题
        When: 计算引导效率
        Then: 应返回平均提示数和效率分数
        """
        # 模拟不同提示需求
        hints_needed = [1, 2, 1, 3, 1, 2, 1]
        for hints in hints_needed:
            await analytics_service.record_performance_event(
                student_id="student_001",
                problem_type="subtraction",
                event_type="answer_given",
                is_correct=True,
                hints_needed=hints,
                guidance_received=True,
                response_time_seconds=8.0
            )

        efficiency = await analytics_service.calculate_guidance_efficiency(
            student_id="student_001",
            problem_type="subtraction"
        )

        assert efficiency.avg_hints_needed == pytest.approx(1.57, 0.01)
        assert efficiency.total_problems == len(hints_needed)
        assert efficiency.efficiency_score > 0  # 应该有正效率分数

    @pytest.mark.asyncio
    async def test_calculate_learning_velocity(self, analytics_service):
        """
        测试：计算学习速度

        Given: 学生在一段时间内改善性能
        When: 计算学习速度
        Then: 应返回改善速率（正确率增长/时间）
        """
        base_time = datetime.now()

        # 模拟 5 天的学习过程，逐步改善
        for day in range(5):
            for attempt in range(10):
                # 逐步提高正确率：20% -> 40% -> 60% -> 80% -> 100%
                target_correct = 2 + day * 2
                is_correct = attempt < target_correct

                await analytics_service.record_performance_event(
                    student_id="student_002",
                    problem_type="addition",
                    event_type="answer_given",
                    is_correct=is_correct,
                    hints_needed=0,
                    guidance_received=True,
                    response_time_seconds=5.0,
                    timestamp=base_time + timedelta(days=day)
                )

        velocity = await analytics_service.calculate_learning_velocity(
            student_id="student_002",
            problem_type="addition"
        )

        assert velocity.improvement_rate > 0  # 应该有正改善
        assert velocity.start_accuracy == pytest.approx(0.2, 0.01)
        assert velocity.end_accuracy == pytest.approx(1.0, 0.01)
        assert velocity.time_period_days == 4  # 5 天中的 4 天间隔

    @pytest.mark.asyncio
    async def test_calculate_confidence_level(self, analytics_service):
        """
        测试：计算信心水平

        Given: 学生的回答模式（快速正确、自我修正、猜测）
        When: 计算信心水平
        Then: 应基于响应模式返回信心分数
        """
        # 高信心场景：快速正确回答
        for _ in range(5):
            await analytics_service.record_performance_event(
                student_id="student_003",
                problem_type="addition",
                event_type="answer_given",
                is_correct=True,
                hints_needed=0,
                guidance_received=False,
                response_time_seconds=3.0,  # 快速
                self_corrected=False
            )

        confidence = await analytics_service.calculate_confidence_level(
            student_id="student_003",
            problem_type="addition"
        )

        assert confidence.confidence_score >= 0.7  # 应该有高信心
        assert confidence.confidence_level == "high"


class TestTrendDetection:
    """测试趋势检测"""

    @pytest.mark.asyncio
    async def test_detect_learning_plateau(self, analytics_service):
        """
        测试：检测学习平台期

        Given: 学生在一段时间内正确率停滞在 50%
        When: 检测趋势
        Then: 应识别出平台期
        """
        base_time = datetime.now()

        # 模拟 7 天的平台期
        for day in range(7):
            for attempt in range(10):
                is_correct = attempt < 5  # 持续 50% 正确率

                await analytics_service.record_performance_event(
                    student_id="student_004",
                    problem_type="geometry",
                    event_type="answer_given",
                    is_correct=is_correct,
                    hints_needed=1,
                    guidance_received=True,
                    response_time_seconds=8.0,
                    timestamp=base_time + timedelta(days=day)
                )

        trends = await analytics_service.detect_trends(
            student_id="student_004",
            problem_type="geometry"
        )

        assert len(trends.plateaus) > 0
        assert trends.plateaus[0].duration_days >= 5
        assert trends.plateaus[0].accuracy_level == pytest.approx(0.5, 0.1)

    @pytest.mark.asyncio
    async def test_detect_breakthrough_moment(self, analytics_service):
        """
        测试：检测突破时刻

        Given: 学生突然从 40% 正确率跃升到 90%
        When: 检测趋势
        Then: 应识别出突破时刻
        """
        base_time = datetime.now()

        # 前 3 天：40% 正确率
        for day in range(3):
            for attempt in range(10):
                is_correct = attempt < 4
                await analytics_service.record_performance_event(
                    student_id="student_005",
                    problem_type="division",
                    event_type="answer_given",
                    is_correct=is_correct,
                    hints_needed=2,
                    guidance_received=True,
                    response_time_seconds=10.0,
                    timestamp=base_time + timedelta(days=day)
                )

        # 第 4 天开始：90% 正确率（突破）
        for day in range(3, 6):
            for attempt in range(10):
                is_correct = attempt < 9
                await analytics_service.record_performance_event(
                    student_id="student_005",
                    problem_type="division",
                    event_type="answer_given",
                    is_correct=is_correct,
                    hints_needed=0,
                    guidance_received=False,
                    response_time_seconds=5.0,
                    timestamp=base_time + timedelta(days=day)
                )

        trends = await analytics_service.detect_trends(
            student_id="student_005",
            problem_type="division"
        )

        assert len(trends.breakthroughs) > 0
        assert trends.breakthroughs[0].accuracy_jump >= 0.4  # 至少 40% 跳升
        assert trends.breakthroughs[0].day == 3  # 第 3 天（从 0 开始）

    @pytest.mark.asyncio
    async def test_detect_struggle_pattern(self, analytics_service):
        """
        测试：检测困难模式

        Given: 学生在特定问题上持续困难（高提示需求、低正确率）
        When: 检测趋势
        Then: 应识别出困难模式
        """
        base_time = datetime.now()

        # 模拟在几何问题上持续困难
        for day in range(5):
            for attempt in range(10):
                is_correct = attempt < 3  # 30% 正确率
                await analytics_service.record_performance_event(
                    student_id="student_006",
                    problem_type="geometry",
                    event_type="answer_given",
                    is_correct=is_correct,
                    hints_needed=3,  # 高提示需求
                    guidance_received=True,
                    response_time_seconds=15.0,  # 慢响应
                    timestamp=base_time + timedelta(days=day)
                )

        trends = await analytics_service.detect_trends(
            student_id="student_006",
            problem_type="geometry"
        )

        assert len(trends.struggles) > 0
        assert trends.struggles[0].problem_type == "geometry"
        assert trends.struggles[0].avg_hints_needed >= 2
        assert trends.struggles[0].success_rate <= 0.4


class TestRealTimeMetrics:
    """测试实时指标"""

    @pytest.mark.asyncio
    async def test_get_current_success_rate(self, analytics_service):
        """
        测试：获取当前成功率（最近 5-10 次尝试）

        Given: 学生最近 10 次尝试中有 8 次正确
        When: 获取实时成功率
        Then: 应返回 0.8 且检索时间 <100ms
        """
        # 创建 20 次尝试历史
        for i in range(20):
            await analytics_service.record_performance_event(
                student_id="student_007",
                problem_type="addition",
                event_type="answer_given",
                is_correct=(i >= 12),  # 最近 8 次正确
                hints_needed=0,
                guidance_received=True,
                response_time_seconds=5.0
            )

        import time
        start = time.time()

        metrics = await analytics_service.get_real_time_metrics(
            student_id="student_007",
            problem_type="addition"
        )

        elapsed = (time.time() - start) * 1000  # 转换为毫秒

        assert metrics.current_success_rate == pytest.approx(0.8, 0.1)
        assert elapsed < 100  # 必须在 100ms 内完成

    @pytest.mark.asyncio
    async def test_get_recent_guidance_efficiency(self, analytics_service):
        """
        测试：获取最近引导效率（最近 3 次交互）

        Given: 学生最近 3 次交互平均需要 1.3 个提示
        When: 获取实时引导效率
        Then: 应返回平均提示数
        """
        # 创建最近的交互
        recent_hints = [1, 2, 1]
        for hints in recent_hints:
            await analytics_service.record_performance_event(
                student_id="student_008",
                problem_type="subtraction",
                event_type="answer_given",
                is_correct=True,
                hints_needed=hints,
                guidance_received=True,
                response_time_seconds=8.0
            )

        metrics = await analytics_service.get_real_time_metrics(
            student_id="student_008",
            problem_type="subtraction"
        )

        assert metrics.recent_guidance_efficiency == pytest.approx(1.33, 0.1)
        assert metrics.recent_interaction_count == 3


@pytest.fixture
def analytics_service():
    """创建性能分析服务实例"""
    return PerformanceAnalyticsService()
