"""
学生表现分析服务 (LWP-17)

收集、聚合和分析学生性能数据，为自适应学习提供数据支持
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from collections import defaultdict
import time

from app.models.analytics import (
    PerformanceEvent,
    PerformanceMetrics,
    GuidanceEfficiency,
    LearningVelocity,
    ConfidenceIndicators,
    ConfidenceLevel,
    TrendAnalysis,
    LearningPlateau,
    BreakthroughMoment,
    StrugglePattern,
    RealTimeMetrics,
    EventType
)


class PerformanceAnalyticsService:
    """
    学生表现分析服务

    功能：
    1. 性能数据收集
    2. 指标计算（成功率、引导效率、学习速度、信心水平）
    3. 趋势检测（平台期、突破、困难模式）
    4. 实时指标检索
    """

    def __init__(self):
        """初始化服务"""
        # 内存存储（生产环境应使用数据库）
        self._events: List[PerformanceEvent] = []
        self._metrics_cache: Dict[str, PerformanceMetrics] = {}
        self._real_time_cache: Dict[str, RealTimeMetrics] = {}

    # ========== 1. 数据收集 ==========

    async def record_performance_event(
        self,
        student_id: str,
        problem_type: str,
        event_type: str,
        is_correct: Optional[bool],
        hints_needed: int,
        guidance_received: bool,
        response_time_seconds: float,
        self_corrected: bool = False,
        timestamp: Optional[datetime] = None
    ) -> PerformanceEvent:
        """
        记录性能事件

        Args:
            student_id: 学生 ID
            problem_type: 问题类型
            event_type: 事件类型
            is_correct: 是否正确
            hints_needed: 需要的提示数
            guidance_received: 是否收到引导
            response_time_seconds: 响应时间（秒）
            self_corrected: 是否自我修正
            timestamp: 事件时间戳（可选）

        Returns:
            PerformanceEvent: 记录的事件
        """
        event = PerformanceEvent(
            student_id=student_id,
            problem_type=problem_type,
            event_type=EventType(event_type),
            is_correct=is_correct,
            hints_needed=hints_needed,
            guidance_received=guidance_received,
            self_corrected=self_corrected,
            response_time_seconds=response_time_seconds,
            timestamp=timestamp or datetime.now()
        )

        self._events.append(event)

        # 清理缓存（新数据可能影响指标）
        cache_key = f"{student_id}:{problem_type}"
        if cache_key in self._metrics_cache:
            del self._metrics_cache[cache_key]
        if cache_key in self._real_time_cache:
            del self._real_time_cache[cache_key]

        return event

    # ========== 2. 指标计算 ==========

    async def calculate_success_rate(
        self,
        student_id: str,
        problem_type: Optional[str] = None
    ) -> PerformanceMetrics:
        """
        计算成功率

        Args:
            student_id: 学生 ID
            problem_type: 问题类型（可选，不指定则计算所有类型）

        Returns:
            PerformanceMetrics: 包含成功率的指标
        """
        # 筛选事件
        events = [
            e for e in self._events
            if e.student_id == student_id and
            e.event_type == EventType.ANSWER_GIVEN and
            e.is_correct is not None and
            (problem_type is None or e.problem_type == problem_type)
        ]

        if not events:
            return PerformanceMetrics()

        total = len(events)
        correct = sum(1 for e in events if e.is_correct)
        success_rate = correct / total if total > 0 else 0.0
        avg_response_time = sum(e.response_time_seconds for e in events) / total

        return PerformanceMetrics(
            success_rate=success_rate,
            total_attempts=total,
            correct_answers=correct,
            avg_response_time=avg_response_time,
            avg_hints_needed=sum(e.hints_needed for e in events) / total
        )

    async def calculate_guidance_efficiency(
        self,
        student_id: str,
        problem_type: str
    ) -> GuidanceEfficiency:
        """
        计算引导效率

        Args:
            student_id: 学生 ID
            problem_type: 问题类型

        Returns:
            GuidanceEfficiency: 引导效率指标
        """
        events = [
            e for e in self._events
            if e.student_id == student_id and
            e.problem_type == problem_type and
            e.event_type == EventType.ANSWER_GIVEN
        ]

        if not events:
            return GuidanceEfficiency()

        total = len(events)
        total_hints = sum(e.hints_needed for e in events)
        avg_hints = total_hints / total if total > 0 else 0

        no_hints = sum(1 for e in events if e.hints_needed == 0)
        multiple_hints = sum(1 for e in events if e.hints_needed > 1)

        # 效率分数：0-1，越少提示越高效
        # 公式：1 - (avg_hints / 10)，限制在 0-1 范围
        efficiency_score = max(0.0, min(1.0, 1.0 - (avg_hints / 10.0)))

        return GuidanceEfficiency(
            avg_hints_needed=avg_hints,
            total_problems=total,
            efficiency_score=efficiency_score,
            problems_with_no_hints=no_hints,
            problems_with_multiple_hints=multiple_hints
        )

    async def calculate_learning_velocity(
        self,
        student_id: str,
        problem_type: str,
        time_window_days: int = 30
    ) -> LearningVelocity:
        """
        计算学习速度

        Args:
            student_id: 学生 ID
            problem_type: 问题类型
            time_window_days: 时间窗口（天）

        Returns:
            LearningVelocity: 学习速度指标
        """
        cutoff_time = datetime.now() - timedelta(days=time_window_days)

        events = [
            e for e in self._events
            if e.student_id == student_id and
            e.problem_type == problem_type and
            e.event_type == EventType.ANSWER_GIVEN and
            e.is_correct is not None and
            e.timestamp >= cutoff_time
        ]

        if not events:
            return LearningVelocity()

        # 按天分组
        daily_accuracy: Dict[int, List[bool]] = defaultdict(list)
        for event in events:
            day = event.timestamp.day
            daily_accuracy[day].append(event.is_correct)

        # 计算每天的准确率
        daily_rates = {
            day: sum(results) / len(results)
            for day, results in daily_accuracy.items()
        }

        if len(daily_rates) < 2:
            return LearningVelocity()  # 需要至少 2 天的数据

        sorted_days = sorted(daily_rates.keys())
        start_day = sorted_days[0]
        end_day = sorted_days[-1]

        start_accuracy = daily_rates[start_day]
        end_accuracy = daily_rates[end_day]
        total_improvement = end_accuracy - start_accuracy
        time_period = end_day - start_day

        improvement_rate = total_improvement / time_period if time_period > 0 else 0

        return LearningVelocity(
            improvement_rate=improvement_rate,
            start_accuracy=start_accuracy,
            end_accuracy=end_accuracy,
            time_period_days=time_period,
            total_improvement=total_improvement
        )

    async def calculate_confidence_level(
        self,
        student_id: str,
        problem_type: str
    ) -> ConfidenceIndicators:
        """
        计算信心水平

        基于响应模式：
        - 快速正确回答 → 高信心
        - 自我修正 → 中等信心
        - 慢速或猜测 → 低信心

        Args:
            student_id: 学生 ID
            problem_type: 问题类型

        Returns:
            ConfidenceIndicators: 信心指标
        """
        events = [
            e for e in self._events
            if e.student_id == student_id and
            e.problem_type == problem_type and
            e.event_type == EventType.ANSWER_GIVEN and
            e.is_correct is not None
        ]

        if not events:
            return ConfidenceIndicators()

        correct_events = [e for e in events if e.is_correct]

        # 计算各种指标
        avg_response_time = 0
        if correct_events:
            avg_response_time = sum(e.response_time_seconds for e in correct_events) / len(correct_events)

        self_correction_rate = sum(1 for e in events if e.self_corrected) / len(events) if events else 0

        # 一致性分数（正确回答的方差越小，一致性越高）
        if len(correct_events) > 1:
            response_times = [e.response_time_seconds for e in correct_events]
            avg_time = sum(response_times) / len(response_times)
            variance = sum((t - avg_time) ** 2 for t in response_times) / len(response_times)
            consistency_score = max(0.0, 1.0 - (variance / 100.0))  # 简化的一致性计算
        else:
            consistency_score = 0.5

        # 综合信心分数 (0-1)
        confidence_score = (
            (1.0 if avg_response_time < 5 else 0.7 if avg_response_time < 10 else 0.4) * 0.4 +
            self_correction_rate * 0.3 +
            consistency_score * 0.3
        )

        # 确定信心水平
        if confidence_score >= 0.7:
            level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.4:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        return ConfidenceIndicators(
            confidence_score=confidence_score,
            confidence_level=level,
            avg_response_time_for_correct=avg_response_time,
            self_correction_rate=self_correction_rate,
            consistency_score=consistency_score
        )

    # ========== 3. 趋势检测 ==========

    async def detect_trends(
        self,
        student_id: str,
        problem_type: str,
        analysis_window_days: int = 30
    ) -> TrendAnalysis:
        """
        检测趋势

        Args:
            student_id: 学生 ID
            problem_type: 问题类型
            analysis_window_days: 分析窗口（天）

        Returns:
            TrendAnalysis: 趋势分析结果
        """
        cutoff_time = datetime.now() - timedelta(days=analysis_window_days)

        events = [
            e for e in self._events
            if e.student_id == student_id and
            e.problem_type == problem_type and
            e.event_type == EventType.ANSWER_GIVEN and
            e.is_correct is not None and
            e.timestamp >= cutoff_time
        ]

        if not events:
            return TrendAnalysis(analysis_period_days=analysis_window_days)

        # 按天分组
        daily_data: Dict[int, List[bool]] = defaultdict(list)
        daily_hints: Dict[int, List[int]] = defaultdict(list)
        daily_times: Dict[int, List[float]] = defaultdict(list)

        for event in events:
            day = event.timestamp.day
            daily_data[day].append(event.is_correct)
            daily_hints[day].append(event.hints_needed)
            daily_times[day].append(event.response_time_seconds)

        # 计算每天的指标
        daily_accuracy = {}
        daily_avg_hints = {}
        daily_avg_times = {}

        for day in set(daily_data.keys()) | set(daily_hints.keys()) | set(daily_times.keys()):
            results = daily_data.get(day, [])
            hints = daily_hints.get(day, [])
            times = daily_times.get(day, [])

            if results:
                daily_accuracy[day] = sum(results) / len(results)
            if hints:
                daily_avg_hints[day] = sum(hints) / len(hints)
            if times:
                daily_avg_times[day] = sum(times) / len(times)

        # 检测平台期
        plateaus = self._detect_plateaus(daily_accuracy, daily_avg_hints)

        # 检测突破
        breakthroughs = self._detect_breakthroughs(daily_accuracy)

        # 检测困难
        struggles = self._detect_struggles(
            problem_type,
            daily_accuracy,
            daily_avg_hints,
            daily_avg_times
        )

        # 计算整体趋势
        if len(daily_accuracy) >= 2:
            sorted_days = sorted(daily_accuracy.keys())
            first_acc = daily_accuracy[sorted_days[0]]
            last_acc = daily_accuracy[sorted_days[-1]]
            overall_diff = last_acc - first_acc

            if overall_diff > 0.1:
                trend = "improving"
            elif overall_diff < -0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return TrendAnalysis(
            plateaus=plateaus,
            breakthroughs=breakthroughs,
            struggles=struggles,
            analysis_period_days=analysis_window_days,
            overall_trend=trend
        )

    def _detect_plateaus(
        self,
        daily_accuracy: Dict[int, float],
        daily_hints: Dict[int, float]
    ) -> List[LearningPlateau]:
        """检测学习平台期"""
        plateaus = []

        if len(daily_accuracy) < 3:
            return plateaus

        sorted_days = sorted(daily_accuracy.keys())
        consecutive_similar = 1
        plateau_start_day = sorted_days[0]
        base_accuracy = daily_accuracy[plateau_start_day]

        for i in range(1, len(sorted_days)):
            day = sorted_days[i]
            accuracy = daily_accuracy[day]

            # 如果准确率变化小于 10%，认为是平台期
            if abs(accuracy - base_accuracy) < 0.1:
                consecutive_similar += 1
            else:
                # 检查是否满足平台期条件（至少 5 天）
                if consecutive_similar >= 5:
                    plateaus.append(
                        LearningPlateau(
                            start_date=datetime.now().replace(day=plateau_start_day),
                            end_date=datetime.now().replace(day=sorted_days[i-1]),
                            duration_days=consecutive_similar,
                            accuracy_level=base_accuracy,
                            problem_type=""
                        )
                    )

                # 重置
                consecutive_similar = 1
                plateau_start_day = day
                base_accuracy = accuracy

        # 检查最后一组
        if consecutive_similar >= 5:
            plateaus.append(
                LearningPlateau(
                    start_date=datetime.now().replace(day=plateau_start_day),
                    end_date=datetime.now().replace(day=sorted_days[-1]),
                    duration_days=consecutive_similar,
                    accuracy_level=base_accuracy,
                    problem_type=""
                )
            )

        return plateaus

    def _detect_breakthroughs(
        self,
        daily_accuracy: Dict[int, float]
    ) -> List[BreakthroughMoment]:
        """检测突破时刻"""
        breakthroughs = []

        if len(daily_accuracy) < 2:
            return breakthroughs

        sorted_days = sorted(daily_accuracy.keys())

        for i in range(1, len(sorted_days)):
            prev_day = sorted_days[i-1]
            curr_day = sorted_days[i]

            prev_acc = daily_accuracy[prev_day]
            curr_acc = daily_accuracy[curr_day]

            accuracy_jump = curr_acc - prev_acc

            # 定义突破：准确率跳跃 > 40%
            if accuracy_jump > 0.4:
                breakthroughs.append(
                    BreakthroughMoment(
                        timestamp=datetime.now().replace(day=curr_day),
                        day=i,
                        accuracy_before=prev_acc,
                        accuracy_after=curr_acc,
                        accuracy_jump=accuracy_jump,
                        problem_type=""
                    )
                )

        return breakthroughs

    def _detect_struggles(
        self,
        problem_type: str,
        daily_accuracy: Dict[int, float],
        daily_hints: Dict[int, float],
        daily_times: Dict[int, float]
    ) -> List[StrugglePattern]:
        """检测困难模式"""
        struggles = []

        # 简化实现：检查整体表现
        if not daily_accuracy:
            return struggles

        avg_acc = sum(daily_accuracy.values()) / len(daily_accuracy)
        avg_hints = sum(daily_hints.values()) / len(daily_hints) if daily_hints else 0
        avg_time = sum(daily_times.values()) / len(daily_times) if daily_times else 0

        # 困难条件：低正确率 + 高提示需求 + 慢响应
        if avg_acc < 0.5 and avg_hints > 2 and avg_time > 10:
            severity = "high" if avg_acc < 0.3 else "medium"

            struggles.append(
                StrugglePattern(
                    problem_type=problem_type,
                    start_date=datetime.now(),
                    duration_days=len(daily_accuracy),
                    success_rate=avg_acc,
                    avg_hints_needed=avg_hints,
                    avg_response_time=avg_time,
                    severity=severity
                )
            )

        return struggles

    # ========== 4. 实时指标 ==========

    async def get_real_time_metrics(
        self,
        student_id: str,
        problem_type: str
    ) -> RealTimeMetrics:
        """
        获取实时指标

        用于脚手架调整，必须在 100ms 内返回

        Args:
            student_id: 学生 ID
            problem_type: 问题类型

        Returns:
            RealTimeMetrics: 实时性能指标
        """
        start_time = time.time()

        cache_key = f"{student_id}:{problem_type}"

        # 检查缓存
        if cache_key in self._real_time_cache:
            cached = self._real_time_cache[cache_key]
            # 如果缓存不超过 5 秒，使用缓存
            if (datetime.now() - cached.last_updated).total_seconds() < 5:
                return cached

        # 获取最近的事件
        events = [
            e for e in self._events
            if e.student_id == student_id and
            e.problem_type == problem_type and
            e.event_type == EventType.ANSWER_GIVEN and
            e.is_correct is not None
        ]

        # 最近 10 次尝试的成功率
        recent_events = events[-10:] if len(events) >= 10 else events
        if recent_events:
            current_success_rate = sum(1 for e in recent_events if e.is_correct) / len(recent_events)
        else:
            current_success_rate = 0.0

        # 最近 3 次交互的引导效率
        recent_interactions = events[-3:] if len(events) >= 3 else events
        if recent_interactions:
            recent_guidance_efficiency = sum(e.hints_needed for e in recent_interactions) / len(recent_interactions)
        else:
            recent_guidance_efficiency = 0.0

        # 当前信心水平（简化版）
        correct_recent = [e for e in recent_events if e.is_correct]
        if correct_recent:
            avg_time = sum(e.response_time_seconds for e in correct_recent) / len(correct_recent)
            current_confidence = 1.0 if avg_time < 5 else 0.7
        else:
            current_confidence = 0.0

        metrics = RealTimeMetrics(
            student_id=student_id,
            problem_type=problem_type,
            current_success_rate=current_success_rate,
            recent_interaction_count=len(recent_events),
            recent_guidance_efficiency=recent_guidance_efficiency,
            current_confidence_level=current_confidence,
            last_updated=datetime.now()
        )

        # 缓存结果
        self._real_time_cache[cache_key] = metrics

        # 确保在 100ms 内完成
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms > 100:
            print(f"Warning: Real-time metrics took {elapsed_ms:.2f}ms (>100ms)")

        return metrics
