"""
脚手架层级管理服务 (LWP-14)

根据学生表现动态调整脚手架层级
"""
from typing import Dict, List, Optional, Any
from collections import defaultdict

from app.models.socratic import ScaffoldingLevel


class ScaffoldingLevelManager:
    """
    脚手架层级管理器

    根据学生表现动态调整脚手架层级
    """

    # 连续正确/错误阈值
    SUCCESS_THRESHOLD = 3  # 连续 3 个正确答案 → 降级
    ERROR_THRESHOLD = 3    # 连续 3 个错误 → 升级

    def __init__(self):
        """初始化脚手架管理器"""
        # 会话脚手架层级缓存
        self.session_levels: Dict[str, ScaffoldingLevel] = {}

        # 会话表现历史
        self.session_performance: Dict[str, List[Dict]] = defaultdict(list)

    def determine_level(
        self,
        conversation_id: str,
        performance_history: Optional[List[Dict]] = None
    ) -> ScaffoldingLevel:
        """
        确定学生当前的脚手架层级

        Args:
            conversation_id: 会话 ID
            performance_history: 表现历史列表（可选）
                [{"is_correct": True/False}, ...]

        Returns:
            脚手架层级
        """
        # 如果提供了表现历史，更新缓存
        if performance_history is not None:
            self.session_performance[conversation_id] = performance_history

        # 获取该会话的表现历史
        history = self.session_performance.get(conversation_id, [])

        # 如果是新会话或没有历史，使用默认层级
        if not history:
            return ScaffoldingLevel.MODERATE

        # 分析最近的表现
        recent_performance = history[-self.ERROR_THRESHOLD:]  # 最近 3 次

        # 计算连续正确次数
        consecutive_correct = 0
        for record in reversed(recent_performance):
            if record.get("is_correct", False):
                consecutive_correct += 1
            else:
                break

        # 计算连续错误次数
        consecutive_errors = 0
        for record in reversed(recent_performance):
            if not record.get("is_correct", True):
                consecutive_errors += 1
            else:
                break

        # 根据连续表现调整层级
        current_level = self.session_levels.get(conversation_id, ScaffoldingLevel.MODERATE)

        if consecutive_correct >= self.SUCCESS_THRESHOLD:
            # 连续正确 → 降级（减少引导）
            if current_level == ScaffoldingLevel.HIGHLY_GUIDED:
                new_level = ScaffoldingLevel.MODERATE
            elif current_level == ScaffoldingLevel.MODERATE:
                new_level = ScaffoldingLevel.MINIMAL
            else:
                new_level = current_level  # 已经是最小了
        elif consecutive_errors >= self.ERROR_THRESHOLD:
            # 连续错误 → 升级（增加引导）
            if current_level == ScaffoldingLevel.MINIMAL:
                new_level = ScaffoldingLevel.MODERATE
            elif current_level == ScaffoldingLevel.MODERATE:
                new_level = ScaffoldingLevel.HIGHLY_GUIDED
            else:
                new_level = current_level  # 已经是最大了
        else:
            # 混合表现 → 维持当前层级
            new_level = current_level

        # 更新缓存
        self.session_levels[conversation_id] = new_level

        return new_level

    def record_performance(
        self,
        conversation_id: str,
        is_correct: bool,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        记录学生表现

        Args:
            conversation_id: 会话 ID
            is_correct: 是否正确
            metadata: 额外的元数据（可选）
        """
        record = {
            "is_correct": is_correct,
            "timestamp": self._get_timestamp()
        }

        if metadata:
            record.update(metadata)

        self.session_performance[conversation_id].append(record)

        # 限制历史长度
        if len(self.session_performance[conversation_id]) > 20:
            self.session_performance[conversation_id] = \
                self.session_performance[conversation_id][-20:]

    def get_performance_stats(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        获取学生表现统计

        Args:
            conversation_id: 会话 ID

        Returns:
            统计信息字典
        """
        history = self.session_performance.get(conversation_id, [])

        if not history:
            return {
                "total_attempts": 0,
                "correct_count": 0,
                "accuracy": 0.0,
                "current_level": ScaffoldingLevel.MODERATE.value
            }

        correct_count = sum(1 for record in history if record.get("is_correct", False))
        total_count = len(history)

        return {
            "total_attempts": total_count,
            "correct_count": correct_count,
            "accuracy": correct_count / total_count if total_count > 0 else 0.0,
            "current_level": self.session_levels.get(
                conversation_id,
                ScaffoldingLevel.MODERATE
            ).value
        }

    def reset_session(self, conversation_id: str) -> None:
        """
        重置会话的脚手架层级和表现历史

        Args:
            conversation_id: 会话 ID
        """
        if conversation_id in self.session_levels:
            del self.session_levels[conversation_id]

        if conversation_id in self.session_performance:
            del self.session_performance[conversation_id]

    def _get_timestamp(self) -> str:
        """
        获取当前时间戳

        Returns:
            ISO 格式的时间戳字符串
        """
        from datetime import datetime
        return datetime.now().isoformat()
