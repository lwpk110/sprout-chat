"""
学生表现分析数据模型 (LWP-17)

定义性能事件、指标和趋势分析的数据结构
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """事件类型"""
    ANSWER_GIVEN = "answer_given"
    HINT_REQUESTED = "hint_requested"
    SELF_CORRECTION = "self_correction"
    CLARIFICATION_REQUESTED = "clarification_requested"


class PerformanceEvent(BaseModel):
    """性能事件

    单个学生交互的性能数据点
    """
    id: Optional[str] = None
    student_id: str
    problem_type: str
    event_type: EventType
    is_correct: Optional[bool] = None
    hints_needed: int = 0
    guidance_received: bool = False
    self_corrected: bool = False
    response_time_seconds: float
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class PerformanceMetrics(BaseModel):
    """性能指标

    计算后的聚合性能指标
    """
    success_rate: float = 0.0
    total_attempts: int = 0
    correct_answers: int = 0
    avg_response_time: float = 0.0
    avg_hints_needed: float = 0.0


class GuidanceEfficiency(BaseModel):
    """引导效率指标"""
    avg_hints_needed: float = 0.0
    total_problems: int = 0
    efficiency_score: float = 0.0  # 0-1，越高越高效
    problems_with_no_hints: int = 0
    problems_with_multiple_hints: int = 0


class LearningVelocity(BaseModel):
    """学习速度指标"""
    improvement_rate: float = 0.0  # 每天改善率
    start_accuracy: float = 0.0
    end_accuracy: float = 0.0
    time_period_days: int = 0
    total_improvement: float = 0.0


class ConfidenceLevel(str, Enum):
    """信心水平"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceIndicators(BaseModel):
    """信心指标"""
    confidence_score: float = 0.0  # 0-1
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    avg_response_time_for_correct: float = 0.0
    self_correction_rate: float = 0.0
    consistency_score: float = 0.0  # 性能一致性


class LearningPlateau(BaseModel):
    """学习平台期"""
    start_date: datetime
    end_date: datetime
    duration_days: int
    accuracy_level: float
    problem_type: str


class BreakthroughMoment(BaseModel):
    """突破时刻"""
    timestamp: datetime
    day: int  # 在时间序列中的天数
    accuracy_before: float
    accuracy_after: float
    accuracy_jump: float
    problem_type: str


class StrugglePattern(BaseModel):
    """困难模式"""
    problem_type: str
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_days: int
    success_rate: float
    avg_hints_needed: float
    avg_response_time: float
    severity: str = "medium"  # low, medium, high


class TrendAnalysis(BaseModel):
    """趋势分析结果"""
    plateaus: List[LearningPlateau] = []
    breakthroughs: List[BreakthroughMoment] = []
    struggles: List[StrugglePattern] = []
    analysis_period_days: int = 0
    overall_trend: str = "stable"  # improving, stable, declining


class RealTimeMetrics(BaseModel):
    """实时性能指标

    用于脚手架调整的快速检索指标
    """
    student_id: str
    problem_type: str
    current_success_rate: float = 0.0  # 最近 5-10 次
    recent_interaction_count: int = 0
    recent_guidance_efficiency: float = 0.0  # 最近 3 次
    current_confidence_level: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)
