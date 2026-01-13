"""
脚手架持久化服务 (LWP-15)

提供脚手架层级和表现指标的数据库持久化功能
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.scaffolding import ScaffoldingLevelRecord, PerformanceMetric
from app.models.socratic import ScaffoldingLevel


class ScaffoldingPersistenceService:
    """
    脚手架持久化服务

    负责将脚手架层级和表现指标持久化到数据库，支持跨会话的个性化学习跟踪
    """

    # 连续正确/错误阈值
    SUCCESS_THRESHOLD = 3  # 连续 3 个正确答案 → 降级
    ERROR_THRESHOLD = 3    # 连续 3 个错误 → 升级

    def __init__(self, db: Session):
        """
        初始化服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def get_current_level(
        self,
        student_id: int,
        problem_domain: str = "general"
    ) -> ScaffoldingLevelRecord:
        """
        获取学生当前脚手架层级

        如果学生没有层级记录，创建默认层级（MODERATE）

        Args:
            student_id: 学生 ID
            problem_domain: 问题领域（math, reading, general）

        Returns:
            脚手架层级记录
        """
        # 查询现有记录
        record = self.db.query(ScaffoldingLevelRecord).filter(
            ScaffoldingLevelRecord.student_id == student_id,
            ScaffoldingLevelRecord.problem_domain == problem_domain
        ).first()

        # 如果不存在，创建默认层级
        if not record:
            record = ScaffoldingLevelRecord(
                student_id=student_id,
                problem_domain=problem_domain,
                level=ScaffoldingLevel.MODERATE,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)

        return record

    def update_level(
        self,
        student_id: int,
        problem_domain: str,
        new_level: ScaffoldingLevel
    ) -> ScaffoldingLevelRecord:
        """
        更新脚手架层级

        Args:
            student_id: 学生 ID
            problem_domain: 问题领域
            new_level: 新的脚手架层级

        Returns:
            更新后的层级记录
        """
        # 获取或创建记录
        record = self.get_current_level(student_id, problem_domain)

        # 更新层级
        record.level = new_level
        record.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(record)

        return record

    def record_performance(
        self,
        student_id: int,
        conversation_id: str,
        problem_domain: str,
        is_correct: bool,
        scaffolding_level_at_time: ScaffoldingLevel,
        hints_needed: int = 0,
        response_time_seconds: Optional[float] = None,
        self_corrected: bool = False,
        question_type: Optional[str] = None
    ) -> PerformanceMetric:
        """
        记录学生表现指标

        Args:
            student_id: 学生 ID
            conversation_id: 会话 ID
            problem_domain: 问题领域
            is_correct: 是否正确
            scaffolding_level_at_time: 当时的脚手架层级
            hints_needed: 需要的提示数量
            response_time_seconds: 响应时间（秒）
            self_corrected: 是否自我纠正
            question_type: 问题类型

        Returns:
            创建的表现指标记录
        """
        metric = PerformanceMetric(
            student_id=student_id,
            conversation_id=conversation_id,
            problem_domain=problem_domain,
            is_correct=is_correct,
            hints_needed=hints_needed,
            response_time_seconds=response_time_seconds,
            self_corrected=self_corrected,
            scaffolding_level_at_time=scaffolding_level_at_time,
            question_type=question_type,
            created_at=datetime.now(timezone.utc)
        )

        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)

        return metric

    def get_recent_metrics(
        self,
        student_id: int,
        problem_domain: str,
        limit: int = 10
    ) -> List[PerformanceMetric]:
        """
        获取学生最近的表现指标

        Args:
            student_id: 学生 ID
            problem_domain: 问题领域
            limit: 返回的最大记录数

        Returns:
            最近的表现指标列表（按时间倒序）
        """
        metrics = self.db.query(PerformanceMetric).filter(
            PerformanceMetric.student_id == student_id,
            PerformanceMetric.problem_domain == problem_domain
        ).order_by(
            desc(PerformanceMetric.created_at)
        ).limit(limit).all()

        return metrics

    def calculate_adjustment(
        self,
        student_id: int,
        problem_domain: str,
        recent_metrics: List[PerformanceMetric]
    ) -> Optional[ScaffoldingLevel]:
        """
        根据最近表现计算是否需要调整脚手架层级

        规则：
        - 连续 3 个正确 → 降级（减少引导）
        - 连续 3 个错误 → 升级（增加引导）
        - 混合表现 → 维持当前层级

        Args:
            student_id: 学生 ID
            problem_domain: 问题领域
            recent_metrics: 最近的表现指标列表

        Returns:
            新的脚手架层级，如果不需要调整则返回 None
        """
        if not recent_metrics:
            return None

        # 获取当前层级
        current_record = self.get_current_level(student_id, problem_domain)
        current_level = current_record.level

        # 分析最近的表现（取最近 ERROR_THRESHOLD 个）
        recent_performance = recent_metrics[:self.ERROR_THRESHOLD]

        # 计算连续正确次数
        consecutive_correct = 0
        for metric in recent_performance:
            if metric.is_correct:
                consecutive_correct += 1
            else:
                break

        # 计算连续错误次数
        consecutive_errors = 0
        for metric in recent_performance:
            if not metric.is_correct:
                consecutive_errors += 1
            else:
                break

        # 根据连续表现调整层级
        if consecutive_correct >= self.SUCCESS_THRESHOLD:
            # 连续正确 → 降级（减少引导）
            if current_level == ScaffoldingLevel.HIGHLY_GUIDED:
                new_level = ScaffoldingLevel.MODERATE
            elif current_level == ScaffoldingLevel.MODERATE:
                new_level = ScaffoldingLevel.MINIMAL
            else:
                new_level = None  # 已经是最小了
        elif consecutive_errors >= self.ERROR_THRESHOLD:
            # 连续错误 → 升级（增加引导）
            if current_level == ScaffoldingLevel.MINIMAL:
                new_level = ScaffoldingLevel.MODERATE
            elif current_level == ScaffoldingLevel.MODERATE:
                new_level = ScaffoldingLevel.HIGHLY_GUIDED
            else:
                new_level = None  # 已经是最大了
        else:
            # 混合表现 → 维持当前层级
            new_level = None

        return new_level

    def get_performance_stats(
        self,
        student_id: int,
        problem_domain: str
    ) -> Dict[str, Any]:
        """
        获取学生表现统计

        Args:
            student_id: 学生 ID
            problem_domain: 问题领域

        Returns:
            统计信息字典
        """
        # 查询所有相关指标
        metrics = self.db.query(PerformanceMetric).filter(
            PerformanceMetric.student_id == student_id,
            PerformanceMetric.problem_domain == problem_domain
        ).all()

        if not metrics:
            return {
                "total_attempts": 0,
                "correct_count": 0,
                "accuracy": 0.0,
                "avg_hints_needed": 0.0,
                "avg_response_time": None,
                "current_level": ScaffoldingLevel.MODERATE.value
            }

        # 计算统计数据
        correct_count = sum(1 for m in metrics if m.is_correct)
        total_count = len(metrics)
        hints_needed = sum(m.hints_needed for m in metrics)

        # 计算平均响应时间（排除 None）
        response_times = [m.response_time_seconds for m in metrics if m.response_time_seconds is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else None

        # 获取当前层级
        current_record = self.get_current_level(student_id, problem_domain)

        return {
            "total_attempts": total_count,
            "correct_count": correct_count,
            "accuracy": correct_count / total_count if total_count > 0 else 0.0,
            "avg_hints_needed": hints_needed / total_count if total_count > 0 else 0.0,
            "avg_response_time": avg_response_time,
            "current_level": current_record.level.value
        }
