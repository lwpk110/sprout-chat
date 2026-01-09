"""
家长控制数据模型

实现学习时间限制、难度调整、内容过滤等功能
"""

from datetime import datetime, time
from typing import Optional, Dict, List, Any
from enum import Enum
from pydantic import BaseModel, Field


class DifficultyLevel(Enum):
    """难度等级"""
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"
    ADAPTIVE = "自适应"


class TimeLimitType(Enum):
    """时间限制类型"""
    DAILY = "每日"
    WEEKLY = "每周"
    PER_SESSION = "每次"


class ContentType(Enum):
    """内容类型"""
    ADDITION = "加法"
    SUBTRACTION = "减法"
    MULTIPLICATION = "乘法"
    DIVISION = "除法"
    COMPARISON = "比较"
    WORD_PROBLEM = "应用题"
    CRITICAL_THINKING = "思维训练"


class FilterType(Enum):
    """过滤类型"""
    BLOCK = "屏蔽"
    LIMIT = "限制"


class TimeRestriction(BaseModel):
    """
    时间限制配置
    """
    restriction_id: Optional[str] = None
    student_id: str
    limit_type: TimeLimitType
    max_minutes: int
    allowed_start: Optional[time] = None  # 允许开始时间
    allowed_end: Optional[time] = None  # 允许结束时间
    allowed_days: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])  # 0=周一
    active: bool = True

    class Config:
        pass


class DifficultySettings(BaseModel):
    """
    难度设置
    """
    settings_id: Optional[str] = None
    student_id: str
    subject: str = "数学"
    current_level: DifficultyLevel = DifficultyLevel.ADAPTIVE
    custom_settings: Dict[str, Any] = Field(default_factory=dict)

    # 针对每种题型的难度
    difficulty_by_type: Dict[str, DifficultyLevel] = Field(
        default_factory=dict
    )

    # 自适应参数
    adaptive_enabled: bool = True
    increase_threshold: float = 0.8  # 正确率>80%增加难度
    decrease_threshold: float = 0.5  # 正确率<50%降低难度

    class Config:
        pass


class ContentFilter(BaseModel):
    """
    内容过滤配置
    """
    filter_id: Optional[str] = None
    student_id: str
    filter_type: FilterType
    content_types: List[ContentType]
    reason: Optional[str] = None
    active: bool = True

    class Config:
        pass


class ReminderSettings(BaseModel):
    """
    提醒设置
    """
    reminder_id: Optional[str] = None
    student_id: str

    # 时间提醒
    reminder_before_end: int = 5  # 结束前几分钟提醒
    break_reminder: int = 20  # 每学习多少分钟提醒休息

    # 休息时长
    break_duration: int = 10  # 休息时长（分钟）

    # 启用状态
    time_reminder_enabled: bool = True
    break_reminder_enabled: bool = True

    # 自定义消息
    custom_time_message: Optional[str] = None
    custom_break_message: Optional[str] = None

    class Config:
        pass


class ParentalControlConfig(BaseModel):
    """
    家长控制总配置
    """
    config_id: Optional[str] = None
    student_id: str
    parent_id: str

    # 时间限制
    time_restrictions: List[TimeRestriction] = Field(default_factory=list)

    # 难度设置
    difficulty_settings: List[DifficultySettings] = Field(default_factory=list)

    # 内容过滤
    content_filters: List[ContentFilter] = Field(default_factory=list)

    # 提醒设置
    reminder_settings: Optional[ReminderSettings] = None

    # 创建和更新时间
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        pass


class TimeUsage(BaseModel):
    """
    时间使用统计
    """
    student_id: str
    date: datetime

    # 使用时长（分钟）
    total_minutes: int = 0
    learning_minutes: int = 0  # 学习时长
    break_minutes: int = 0  # 休息时长

    # 会话次数
    session_count: int = 0

    # 开始和结束时间
    first_session: Optional[datetime] = None
    last_session: Optional[datetime] = None

    class Config:
        pass


class ControlCheck(BaseModel):
    """
    控制检查结果
    """
    allowed: bool
    reason: Optional[str] = None
    remaining_minutes: Optional[int] = None
    suggestions: List[str] = Field(default_factory=list)


class DifficultyAdjustment(BaseModel):
    """
    难度调整建议
    """
    student_id: str
    subject: str
    current_level: DifficultyLevel
    suggested_level: DifficultyLevel
    reason: str
    accuracy_rate: float
    total_questions: int


class ContentFilterResult(BaseModel):
    """
    内容过滤结果
    """
    allowed: bool
    filtered_content: Optional[str] = None
    reason: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)
