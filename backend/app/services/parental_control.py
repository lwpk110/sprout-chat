"""
家长控制服务

实现学习时间限制、难度调整、内容过滤、提醒设置等功能
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, time, timedelta, date
from collections import defaultdict
import uuid

from app.models.parental_control import (
    TimeRestriction,
    DifficultySettings,
    ContentFilter,
    ReminderSettings,
    ParentalControlConfig,
    ControlCheck,
    DifficultyAdjustment,
    ContentFilterResult,
    DifficultyLevel,
    TimeLimitType,
    ContentType,
    FilterType
)


class ParentalControlService:
    """
    家长控制服务

    负责管理学习时间限制、难度调整、内容过滤、提醒设置
    """

    def __init__(self):
        """初始化家长控制服务"""
        # 内存存储（生产环境应使用数据库）
        self.configs: Dict[str, ParentalControlConfig] = {}
        self.usage_records: Dict[str, Dict[str, Any]] = {}
        self.answer_records: Dict[str, List[Dict]] = defaultdict(list)

    # ============ 时间限制 ============

    def create_time_restriction(
        self,
        student_id: str,
        limit_type: TimeLimitType,
        max_minutes: int,
        allowed_start: Optional[time] = None,
        allowed_end: Optional[time] = None,
        allowed_days: Optional[List[int]] = None
    ) -> TimeRestriction:
        """
        创建时间限制

        Args:
            student_id: 学生 ID
            limit_type: 限制类型
            max_minutes: 最大分钟数
            allowed_start: 允许开始时间
            allowed_end: 允许结束时间
            allowed_days: 允许的星期（0=周一）

        Returns:
            时间限制配置
        """
        restriction = TimeRestriction(
            restriction_id=str(uuid.uuid4()),
            student_id=student_id,
            limit_type=limit_type,
            max_minutes=max_minutes,
            allowed_start=allowed_start,
            allowed_end=allowed_end,
            allowed_days=allowed_days or [0, 1, 2, 3, 4, 5, 6]
        )

        # 添加到配置
        self._ensure_config(student_id, "system")
        self.configs[student_id].time_restrictions.append(restriction)

        return restriction

    def check_time_limit(self, student_id: str) -> ControlCheck:
        """
        检查时间限制

        Args:
            student_id: 学生 ID

        Returns:
            检查结果
        """
        config = self.configs.get(student_id)
        if not config or not config.time_restrictions:
            return ControlCheck(allowed=True, remaining_minutes=None)

        today = date.today()
        usage_key = f"{student_id}_{today}"

        # 获取今日已使用时长
        if usage_key in self.usage_records:
            used_minutes = self.usage_records[usage_key].get("total_minutes", 0)
        else:
            used_minutes = 0

        # 找到最严格的限制
        max_minutes = None
        for restriction in config.time_restrictions:
            if restriction.limit_type == TimeLimitType.DAILY and restriction.active:
                if max_minutes is None or restriction.max_minutes < max_minutes:
                    max_minutes = restriction.max_minutes

        if max_minutes is None:
            return ControlCheck(allowed=True, remaining_minutes=None)

        remaining = max_minutes - used_minutes

        if remaining <= 0:
            return ControlCheck(
                allowed=False,
                reason=f"已超过每日时间限制（{max_minutes}分钟）",
                remaining_minutes=0,
                suggestions=["明天再继续学习", "请家长调整时间限制"]
            )

        return ControlCheck(
            allowed=True,
            remaining_minutes=remaining
        )

    def check_time_window(self, student_id: str) -> ControlCheck:
        """
        检查时间窗口

        验证当前时间是否在允许的学习窗口内

        Args:
            student_id: 学生 ID

        Returns:
            检查结果
        """
        config = self.configs.get(student_id)
        if not config or not config.time_restrictions:
            return ControlCheck(allowed=True)

        now = datetime.now()
        current_weekday = now.weekday()
        current_time = now.time()

        for restriction in config.time_restrictions:
            if not restriction.active:
                continue

            # 检查星期
            if current_weekday not in restriction.allowed_days:
                return ControlCheck(
                    allowed=False,
                    reason="今天不允许学习",
                    suggestions=["请在允许的日期学习"]
                )

            # 检查时间窗口
            if restriction.allowed_start and restriction.allowed_end:
                if restriction.allowed_start <= current_time <= restriction.allowed_end:
                    return ControlCheck(allowed=True)
                else:
                    return ControlCheck(
                        allowed=False,
                        reason=f"当前时间不在允许的学习窗口内（{restriction.allowed_start.strftime('%H:%M')}-{restriction.allowed_end.strftime('%H:%M')}）",
                        suggestions=["请在允许的时间内学习"]
                    )

        return ControlCheck(allowed=True)

    def record_usage(self, student_id: str, minutes: int):
        """
        记录使用时长

        Args:
            student_id: 学生 ID
            minutes: 使用分钟数
        """
        today = date.today()
        usage_key = f"{student_id}_{today}"

        if usage_key not in self.usage_records:
            self.usage_records[usage_key] = {
                "student_id": student_id,
                "date": today,
                "total_minutes": 0,
                "learning_minutes": 0,
                "session_count": 0
            }

        self.usage_records[usage_key]["total_minutes"] += minutes
        self.usage_records[usage_key]["learning_minutes"] += minutes
        self.usage_records[usage_key]["session_count"] += 1

    # ============ 难度调整 ============

    def create_difficulty_settings(
        self,
        student_id: str,
        subject: str,
        current_level: DifficultyLevel = DifficultyLevel.ADAPTIVE,
        adaptive_enabled: bool = True,
        increase_threshold: float = 0.8,
        decrease_threshold: float = 0.5
    ) -> DifficultySettings:
        """
        创建难度设置

        Args:
            student_id: 学生 ID
            subject: 科目
            current_level: 当前难度
            adaptive_enabled: 是否启用自适应
            increase_threshold: 提升难度阈值
            decrease_threshold: 降低难度阈值

        Returns:
            难度设置
        """
        settings = DifficultySettings(
            settings_id=str(uuid.uuid4()),
            student_id=student_id,
            subject=subject,
            current_level=current_level,
            adaptive_enabled=adaptive_enabled,
            increase_threshold=increase_threshold,
            decrease_threshold=decrease_threshold
        )

        # 添加到配置
        self._ensure_config(student_id, "system")
        self.configs[student_id].difficulty_settings.append(settings)

        return settings

    def record_answer(
        self,
        student_id: str,
        subject: str,
        problem_type: str,
        correct: bool
    ):
        """
        记录答题结果

        用于自适应难度调整

        Args:
            student_id: 学生 ID
            subject: 科目
            problem_type: 题型
            correct: 是否正确
        """
        key = f"{student_id}_{subject}"
        self.answer_records[key].append({
            "problem_type": problem_type,
            "correct": correct,
            "timestamp": datetime.now()
        })

    def suggest_difficulty_adjustment(
        self,
        student_id: str,
        subject: str
    ) -> Optional[DifficultyAdjustment]:
        """
        建议难度调整

        基于最近的答题情况建议难度调整

        Args:
            student_id: 学生 ID
            subject: 科目

        Returns:
            难度调整建议
        """
        config = self.configs.get(student_id)
        if not config:
            return None

        # 找到对应科目的设置
        settings = None
        for s in config.difficulty_settings:
            if s.subject == subject:
                settings = s
                break

        if not settings or not settings.adaptive_enabled:
            return None

        # 获取最近的答题记录
        key = f"{student_id}_{subject}"
        recent_answers = self.answer_records.get(key, [])

        if len(recent_answers) < 10:  # 至少10题
            return None

        # 计算最近20题的正确率
        recent_20 = recent_answers[-20:]
        correct_count = sum(1 for a in recent_20 if a["correct"])
        accuracy = correct_count / len(recent_20)

        current_level = settings.current_level
        suggested_level = current_level
        reason = "当前难度适宜"

        # 判断是否需要调整
        if accuracy >= settings.increase_threshold and current_level != DifficultyLevel.HARD:
            # 提升难度
            levels = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
            current_index = levels.index(current_level) if current_level in levels else 1
            if current_index < len(levels) - 1:
                suggested_level = levels[current_index + 1]
                reason = f"正确率{accuracy*100:.0f}%较高，建议提升难度"
        elif accuracy <= settings.decrease_threshold and current_level != DifficultyLevel.EASY:
            # 降低难度
            levels = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
            current_index = levels.index(current_level) if current_level in levels else 1
            if current_index > 0:
                suggested_level = levels[current_index - 1]
                reason = f"正确率{accuracy*100:.0f}%较低，建议降低难度"

        return DifficultyAdjustment(
            student_id=student_id,
            subject=subject,
            current_level=current_level,
            suggested_level=suggested_level,
            reason=reason,
            accuracy_rate=accuracy,
            total_questions=len(recent_answers)
        )

    def update_difficulty_level(
        self,
        student_id: str,
        subject: str,
        new_level: DifficultyLevel
    ) -> DifficultySettings:
        """
        更新难度等级

        Args:
            student_id: 学生 ID
            subject: 科目
            new_level: 新难度

        Returns:
            更新后的设置
        """
        config = self.configs.get(student_id)
        if not config:
            raise ValueError(f"学生 {student_id} 的配置不存在")

        # 找到对应科目的设置
        settings = None
        for s in config.difficulty_settings:
            if s.subject == subject:
                settings = s
                break

        if not settings:
            raise ValueError(f"科目 {subject} 的设置不存在")

        settings.current_level = new_level
        return settings

    # ============ 内容过滤 ============

    def create_content_filter(
        self,
        student_id: str,
        filter_type: FilterType,
        content_types: List[ContentType],
        reason: Optional[str] = None
    ) -> ContentFilter:
        """
        创建内容过滤器

        Args:
            student_id: 学生 ID
            filter_type: 过滤类型
            content_types: 要过滤的内容类型
            reason: 原因

        Returns:
            内容过滤器
        """
        content_filter = ContentFilter(
            filter_id=str(uuid.uuid4()),
            student_id=student_id,
            filter_type=filter_type,
            content_types=content_types,
            reason=reason
        )

        # 添加到配置
        self._ensure_config(student_id, "system")
        self.configs[student_id].content_filters.append(content_filter)

        return content_filter

    def check_content(
        self,
        student_id: str,
        content_type: ContentType
    ) -> ContentFilterResult:
        """
        检查内容是否允许

        Args:
            student_id: 学生 ID
            content_type: 内容类型

        Returns:
            过滤结果
        """
        config = self.configs.get(student_id)
        if not config or not config.content_filters:
            return ContentFilterResult(allowed=True)

        # 检查是否有过滤器
        for content_filter in config.content_filters:
            if not content_filter.active:
                continue

            if content_type in content_filter.content_types:
                # 找到匹配的过滤器
                alternatives = []

                if content_filter.filter_type == FilterType.BLOCK:
                    # 提供替代内容
                    all_types = [
                        ContentType.ADDITION,
                        ContentType.SUBTRACTION,
                        ContentType.MULTIPLICATION,
                        ContentType.DIVISION,
                        ContentType.COMPARISON,
                        ContentType.WORD_PROBLEM
                    ]

                    for alt_type in all_types:
                        if alt_type not in content_filter.content_types:
                            alternatives.append(alt_type.value)

                    return ContentFilterResult(
                        allowed=False,
                        filtered_content=content_type.value,
                        reason=f"该内容已被家长屏蔽：{content_filter.reason or '未说明原因'}",
                        alternatives=alternatives[:3]  # 最多3个替代
                    )

        return ContentFilterResult(allowed=True)

    # ============ 提醒设置 ============

    def create_reminder_settings(
        self,
        student_id: str,
        reminder_before_end: int = 5,
        break_reminder: int = 20,
        break_duration: int = 10
    ) -> ReminderSettings:
        """
        创建提醒设置

        Args:
            student_id: 学生 ID
            reminder_before_end: 结束前几分钟提醒
            break_reminder: 每学习多少分钟提醒休息
            break_duration: 休息时长

        Returns:
            提醒设置
        """
        settings = ReminderSettings(
            reminder_id=str(uuid.uuid4()),
            student_id=student_id,
            reminder_before_end=reminder_before_end,
            break_reminder=break_reminder,
            break_duration=break_duration
        )

        # 添加到配置
        self._ensure_config(student_id, "system")
        self.configs[student_id].reminder_settings = settings

        return settings

    def check_reminder(self, student_id: str) -> Dict[str, Any]:
        """
        检查时间提醒

        Args:
            student_id: 学生 ID

        Returns:
            提醒信息
        """
        config = self.configs.get(student_id)
        if not config or not config.reminder_settings:
            return {"should_remind": False}

        reminder_settings = config.reminder_settings
        if not reminder_settings.time_reminder_enabled:
            return {"should_remind": False}

        # 检查时间限制
        time_check = self.check_time_limit(student_id)

        if not time_check.allowed:
            return {"should_remind": False}

        if time_check.remaining_minutes is not None:
            if time_check.remaining_minutes <= reminder_settings.reminder_before_end:
                return {
                    "should_remind": True,
                    "type": "time_limit",
                    "message": f"还有{time_check.remaining_minutes}分钟就要到时间限制了",
                    "remaining_minutes": time_check.remaining_minutes
                }

        return {"should_remind": False}

    def check_break_reminder(self, student_id: str) -> Dict[str, Any]:
        """
        检查休息提醒

        Args:
            student_id: 学生 ID

        Returns:
            提醒信息
        """
        config = self.configs.get(student_id)
        if not config or not config.reminder_settings:
            return {"should_remind": False}

        reminder_settings = config.reminder_settings
        if not reminder_settings.break_reminder_enabled:
            return {"should_remind": False}

        # 检查连续学习时长
        today = date.today()
        usage_key = f"{student_id}_{today}"

        if usage_key in self.usage_records:
            learning_minutes = self.usage_records[usage_key].get("learning_minutes", 0)

            if learning_minutes > 0 and learning_minutes % reminder_settings.break_reminder == 0:
                return {
                    "should_remind": True,
                    "type": "break",
                    "message": f"已经学习了{learning_minutes}分钟，建议休息{reminder_settings.break_duration}分钟",
                    "break_duration": reminder_settings.break_duration
                }

        return {"should_remind": False}

    # ============ 总配置管理 ============

    def create_parental_control_config(
        self,
        student_id: str,
        parent_id: str
    ) -> ParentalControlConfig:
        """
        创建家长控制配置

        Args:
            student_id: 学生 ID
            parent_id: 家长 ID

        Returns:
            配置
        """
        config = ParentalControlConfig(
            config_id=str(uuid.uuid4()),
            student_id=student_id,
            parent_id=parent_id
        )

        self.configs[student_id] = config
        return config

    def get_parental_control_config(self, student_id: str) -> Optional[ParentalControlConfig]:
        """
        获取家长控制配置

        Args:
            student_id: 学生 ID

        Returns:
            配置或 None
        """
        return self.configs.get(student_id)

    def clear_all_data(self):
        """清空所有数据（用于测试）"""
        self.configs.clear()
        self.usage_records.clear()
        self.answer_records.clear()

    # ============ 私有方法 ============

    def _ensure_config(self, student_id: str, parent_id: str = "system"):
        """确保配置存在"""
        if student_id not in self.configs:
            self.configs[student_id] = ParentalControlConfig(
                config_id=str(uuid.uuid4()),
                student_id=student_id,
                parent_id=parent_id
            )
