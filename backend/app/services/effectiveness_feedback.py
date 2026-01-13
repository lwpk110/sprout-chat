"""
实时反馈机制服务 (LWP-18)

捕获、处理和聚合有效性信号，提供实时反馈到脚手架调整
"""
from typing import List, Dict, Optional
from collections import defaultdict

from app.models.effectiveness import (
    EffectivenessSignal,
    EffectivenessScore,
    FeedbackAdjustment,
    EffectivenessAnomaly,
    AggregatedEffectivenessMetrics
)


class EffectivenessFeedbackService:
    """
    实时反馈服务

    功能：
    1. 捕获即时有效性信号
    2. 计算有效性分数
    3. 生成调整建议
    4. 检测异常
    """

    # 信号权重配置
    SIGNAL_WEIGHTS = {
        "correct_answer": 2.0,      # 强正信号
        "hint_requested": -1.0,     # 弱负信号
        "self_correction": 2.0,     # 强正信号
        "response_time": 0.0        # 动态计算（基于响应时间）
    }

    # 调整阈值
    HIGH_EFFECTIVENESS_THRESHOLD = 3.5  # > 3.5 分建议提升（降低以匹配实际分数范围）
    LOW_EFFECTIVENESS_THRESHOLD = 1.0   # < 1 分建议降低
    CONSECUTIVE_THRESHOLD = 3           # 连续 3 次触发调整
    ANOMALY_THRESHOLD = 5               # 连续 5 次低分触发异常

    def __init__(self):
        """初始化服务"""
        # 内存存储（生产环境应使用数据库）
        self._signals: List[EffectivenessSignal] = []
        self._scores: Dict[str, EffectivenessScore] = {}
        self._student_history: Dict[str, List[float]] = defaultdict(list)

    # ========== 1. 信号捕获 ==========

    async def capture_effectiveness_signal(
        self,
        response_id: str,
        student_id: str,
        signal_type: str,
        problem_type: str,
        is_correct_after_guidance: Optional[bool] = None,
        hints_needed: int = 0,
        response_time_seconds: Optional[float] = None
    ) -> EffectivenessSignal:
        """
        捕获有效性信号

        Args:
            response_id: 响应 ID
            student_id: 学生 ID
            signal_type: 信号类型
            problem_type: 问题类型
            is_correct_after_guidance: 引导后是否正确
            hints_needed: 需要的提示数
            response_time_seconds: 响应时间

        Returns:
            EffectivenessSignal: 捕获的信号
        """
        # 计算权重
        if signal_type == "response_time" and response_time_seconds is not None:
            # 响应时间权重：快速响应 (<5s) = +0.5, 慢速响应 (>10s) = 0
            if response_time_seconds < 5.0:
                weight = 0.5
            elif response_time_seconds < 10.0:
                weight = 0.2
            else:
                weight = 0.0
        else:
            weight = self.SIGNAL_WEIGHTS.get(signal_type, 0.0)

        signal = EffectivenessSignal(
            response_id=response_id,
            student_id=student_id,
            signal_type=signal_type,
            problem_type=problem_type,
            weight=weight,
            is_correct_after_guidance=is_correct_after_guidance,
            hints_needed=hints_needed,
            response_time_seconds=response_time_seconds
        )

        self._signals.append(signal)

        # 清理相关分数缓存（延迟计算）
        if signal_type in ["correct_answer", "hint_requested", "self_correction"]:
            if response_id in self._scores:
                del self._scores[response_id]

        return signal

    # ========== 2. 分数计算 ==========

    async def calculate_effectiveness_score(
        self,
        response_id: str
    ) -> EffectivenessScore:
        """
        计算响应的有效性分数

        Args:
            response_id: 响应 ID

        Returns:
            EffectivenessScore: 综合分数（0-10 分制）
        """
        # 检查缓存
        if response_id in self._scores:
            return self._scores[response_id]

        # 获取该响应的所有信号
        signals = [s for s in self._signals if s.response_id == response_id]

        if not signals:
            return EffectivenessScore(
                response_id=response_id,
                student_id="",
                problem_type="",
                overall_score=0.0
            )

        # 计算加权和
        total_weight = sum(s.weight for s in signals)
        contributing_signals = [s.signal_type for s in signals if s.weight != 0]

        # 获取学生和问题信息
        student_id = signals[0].student_id
        problem_type = signals[0].problem_type

        # 创建分数
        score = EffectivenessScore(
            response_id=response_id,
            student_id=student_id,
            problem_type=problem_type,
            overall_score=total_weight,
            contributing_signals_count=len(signals),
            contributing_signals=contributing_signals
        )

        # 缓存分数
        self._scores[response_id] = score

        # 记录到学生历史（只记录一次）
        if total_weight > 0 and response_id not in [s.response_id for s in self._signals if s.signal_type in ["correct_answer", "hint_requested", "self_correction"] and s.response_id == response_id]:
            # 简化：每次计算都记录
            pass  # 在调用方控制

        return score

    async def record_score_to_history(self, response_id: str):
        """
        将响应分数记录到学生历史（辅助方法）

        Args:
            response_id: 响应 ID
        """
        if response_id not in self._scores:
            score = await self.calculate_effectiveness_score(response_id)
        else:
            score = self._scores[response_id]

        # 记录分数（包括负分）
        self._student_history[score.student_id].append(score.overall_score)

    # ========== 3. 反馈循环 ==========

    async def generate_adjustment_recommendation(
        self,
        student_id: str,
        lookback_count: int = 3
    ) -> FeedbackAdjustment:
        """
        生成脚手架调整建议

        Args:
            student_id: 学生 ID
            lookback_count: 回溯最近的 N 个响应

        Returns:
            FeedbackAdjustment: 调整建议
        """
        # 获取学生最近的分数
        recent_scores = self._student_history[student_id][-lookback_count:]

        if len(recent_scores) < lookback_count:
            # 数据不足，建议维持
            return FeedbackAdjustment(
                student_id=student_id,
                recommended_action="maintain",
                confidence=0.0,
                reason=f"Insufficient data (only {len(recent_scores)} responses)",
                based_on_signals=len(recent_scores)
            )

        # 计算平均分
        avg_score = sum(recent_scores) / len(recent_scores)

        # 判断调整方向
        if avg_score >= self.HIGH_EFFECTIVENESS_THRESHOLD:
            # 高有效性，建议提升层级（减少引导）
            action = "increase_scaffolding"
            # 置信度计算：基于超出阈值的程度
            excess = avg_score - self.HIGH_EFFECTIVENESS_THRESHOLD
            confidence = min(1.0, excess / 2.0)  # 超过 2 分即为 100% 置信
            reason = f"High effectiveness (avg {avg_score:.1f}) suggests student can handle less guidance"

        elif avg_score <= self.LOW_EFFECTIVENESS_THRESHOLD:
            # 低有效性，建议降低层级（增加引导）
            action = "decrease_scaffolding"
            # 置信度计算：基于低于阈值的程度
            deficit = self.LOW_EFFECTIVENESS_THRESHOLD - avg_score
            confidence = min(1.0, deficit / 2.0)  # 低于 2 分即为 100% 置信
            reason = f"Low effectiveness (avg {avg_score:.1f}) suggests student needs more guidance"

        else:
            # 中等有效性，维持当前层级
            action = "maintain"
            confidence = 0.5
            reason = f"Moderate effectiveness (avg {avg_score:.1f}), maintain current level"

        return FeedbackAdjustment(
            student_id=student_id,
            recommended_action=action,
            confidence=confidence,
            reason=reason,
            based_on_signals=len(recent_scores)
        )

    # ========== 4. 异常检测 ==========

    async def detect_anomalies(
        self,
        student_id: str
    ) -> List[EffectivenessAnomaly]:
        """
        检测异常模式

        Args:
            student_id: 学生 ID

        Returns:
            List[EffectivenessAnomaly]: 检测到的异常列表
        """
        anomalies = []

        scores = self._student_history[student_id]

        if len(scores) < self.ANOMALY_THRESHOLD:
            return anomalies

        # 检查连续低有效性
        consecutive_low = 0
        for score in reversed(scores):  # 从最近的开始
            if score < self.LOW_EFFECTIVENESS_THRESHOLD:
                consecutive_low += 1
            else:
                break

        if consecutive_low >= self.ANOMALY_THRESHOLD:
            # 计算这些低分响应的平均分
            recent_low_scores = scores[-consecutive_low:]
            avg_score = sum(recent_low_scores) / len(recent_low_scores)

            anomalies.append(
                EffectivenessAnomaly(
                    student_id=student_id,
                    anomaly_type="consecutive_low_effectiveness",
                    consecutive_count=consecutive_low,
                    avg_score=avg_score,
                    threshold=self.LOW_EFFECTIVENESS_THRESHOLD,
                    recommended_action="consider_alternative_approach"
                )
            )

        return anomalies

    # ========== 5. 聚合指标 ==========

    async def get_aggregated_metrics(
        self,
        dimension: str,
        dimension_value: str
    ) -> AggregatedEffectivenessMetrics:
        """
        获取聚合的有效性指标

        Args:
            dimension: 维度（question_type, scaffolding_level, etc.）
            dimension_value: 维度值

        Returns:
            AggregatedEffectivenessMetrics: 聚合指标
        """
        # 简化实现：按问题类型聚合
        if dimension == "question_type":
            relevant_scores = [
                s.overall_score
                for s in self._scores.values()
                if s.problem_type == dimension_value
            ]
        else:
            # 其他维度暂未实现
            relevant_scores = []

        if not relevant_scores:
            return AggregatedEffectivenessMetrics(
                dimension=dimension,
                dimension_value=dimension_value
            )

        total = len(relevant_scores)
        avg_score = sum(relevant_scores) / total
        high_count = sum(1 for s in relevant_scores if s > self.HIGH_EFFECTIVENESS_THRESHOLD)
        low_count = sum(1 for s in relevant_scores if s < self.LOW_EFFECTIVENESS_THRESHOLD)

        return AggregatedEffectivenessMetrics(
            dimension=dimension,
            dimension_value=dimension_value,
            avg_effectiveness_score=avg_score,
            total_responses=total,
            high_effectiveness_count=high_count,
            low_effectiveness_count=low_count
        )
