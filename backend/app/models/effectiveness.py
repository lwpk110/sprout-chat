"""
实时反馈机制数据模型 (LWP-18)

定义有效性信号、分数和反馈调整的数据结构
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class EffectivenessSignal(BaseModel):
    """有效性信号

    单个学生交互的即时反馈信号
    """
    id: Optional[str] = None
    response_id: str
    student_id: str
    signal_type: str  # correct_answer, hint_requested, self_correction, response_time
    problem_type: str
    weight: float = 0.0  # 信号权重（正或负）
    is_correct_after_guidance: Optional[bool] = None
    hints_needed: int = 0
    response_time_seconds: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class EffectivenessScore(BaseModel):
    """有效性分数

    单个响应的综合有效性分数
    """
    response_id: str
    student_id: str
    problem_type: str
    overall_score: float = 0.0  # 0-10 分制
    contributing_signals_count: int = 0
    contributing_signals: List[str] = []
    calculated_at: datetime = Field(default_factory=datetime.now)


class FeedbackAdjustment(BaseModel):
    """反馈调整建议

    基于有效性数据的脚手架调整建议
    """
    student_id: str
    recommended_action: str  # increase_scaffolding, decrease_scaffolding, maintain
    confidence: float = 0.0  # 0-1，建议的置信度
    reason: str = ""
    based_on_signals: int = 0  # 基于多少个信号
    suggested_at: datetime = Field(default_factory=datetime.now)


class EffectivenessAnomaly(BaseModel):
    """有效性异常

    检测到异常模式（连续低有效性）
    """
    student_id: str
    anomaly_type: str  # consecutive_low_effectiveness, rapid_decline, etc.
    consecutive_count: int = 0
    avg_score: float = 0.0
    threshold: float = 3.0
    triggered_at: datetime = Field(default_factory=datetime.now)
    recommended_action: str = "consider_alternative_approach"


class AggregatedEffectivenessMetrics(BaseModel):
    """聚合有效性指标

    按问题类型、脚手架层级等维度聚合
    """
    dimension: str  # question_type, scaffolding_level, problem_domain, student_profile
    dimension_value: str
    avg_effectiveness_score: float = 0.0
    total_responses: int = 0
    high_effectiveness_count: int = 0  # > 7 分
    low_effectiveness_count: int = 0   # < 3 分
    last_updated: datetime = Field(default_factory=datetime.now)
