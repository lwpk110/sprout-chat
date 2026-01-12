"""
Phase 2.2 学习管理 API 请求/响应模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CreateLearningRecordRequest(BaseModel):
    """创建学习记录请求"""
    student_id: int
    question_content: str = Field(..., max_length=1000)
    question_type: str = Field(..., description="addition, subtraction, multiplication, etc.")
    subject: str = Field(default="math")
    difficulty_level: int = Field(default=1, ge=1, le=5)
    student_answer: str = Field(..., max_length=500)
    correct_answer: str = Field(..., max_length=500)
    time_spent_seconds: int = Field(..., ge=0)


class LearningRecordResponse(BaseModel):
    """学习记录响应"""
    id: int
    student_id: int
    question_content: str
    question_type: str
    subject: str
    difficulty_level: int
    student_answer: str
    correct_answer: str
    is_correct: bool
    time_spent_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True


class WrongAnswerRecordResponse(BaseModel):
    """错题记录响应"""
    id: int
    error_type: str
    guidance_type: str
    guidance_content: str
    is_resolved: bool

    class Config:
        from_attributes = True


class LearningRecordDetailResponse(LearningRecordResponse):
    """学习记录详情响应"""
    wrong_answer_record: Optional[WrongAnswerRecordResponse] = None


class LearningProgressResponse(BaseModel):
    """学习进度响应"""
    student_id: int
    total_questions: int
    correct_count: int
    wrong_count: int
    accuracy_rate: float
    current_streak: int
    longest_streak: int
    total_time_spent_seconds: int
    average_time_per_question_seconds: float
    time_range: str = "all"


class QuestionTypeStats(BaseModel):
    """题型统计"""
    question_type: str
    total_count: int
    correct_count: int
    accuracy_rate: float


class DifficultyLevelStats(BaseModel):
    """难度等级统计"""
    difficulty_level: int
    total_count: int
    correct_count: int
    accuracy_rate: float


class LearningReportResponse(BaseModel):
    """学习报告响应"""
    student_id: int
    period_start: str
    period_end: str

    # 摘要
    summary: dict

    # 按题型统计
    by_question_type: List[QuestionTypeStats]

    # 按难度统计
    by_difficulty_level: List[DifficultyLevelStats]

    # 连续答对记录
    streak_records: dict
