"""
学习追踪数据模型

记录学生的学习进度、答题历史和生成学习报告
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class AnswerResult(Enum):
    """答题结果"""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"
    ABANDONED = "abandoned"


class ProblemType(Enum):
    """问题类型"""
    ADDITION = "加法"
    SUBTRACTION = "减法"
    MULTIPLICATION = "乘法"
    DIVISION = "除法"
    COMPARISON = "比较"
    WORD_PROBLEM = "应用题"
    UNKNOWN = "未知"


class LearningRecord(BaseModel):
    """
    单次学习记录

    记录一次完整的问答交互
    """
    id: Optional[str] = None
    session_id: str
    student_id: str
    student_age: int
    subject: str

    # 问题信息
    problem_type: ProblemType
    problem_text: str
    problem_image_url: Optional[str] = None

    # 学生回答
    student_answer: str
    answer_result: AnswerResult
    attempts: int = 1  # 尝试次数
    hints_used: int = 0  # 使用提示次数

    # 时间信息
    question_time: datetime = Field(default_factory=datetime.now)
    answer_time: Optional[datetime] = None
    response_duration: Optional[float] = None  # 响应时长（秒）

    # 教学信息
    strategy_used: Optional[str] = None  # 使用的教学策略
    metaphor_used: Optional[str] = None  # 使用的比喻

    # 额外数据
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        pass


class StudentProgress(BaseModel):
    """
    学生进度统计

    汇总学生的学习进展
    """
    student_id: str
    subject: str
    student_age: int

    # 总体统计
    total_questions: int = 0
    total_correct: int = 0
    total_incorrect: int = 0
    total_partial: int = 0

    # 按类型统计
    by_problem_type: Dict[str, Dict[str, int]] = Field(
        default_factory=dict
    )

    # 学习时长
    total_learning_time: float = 0  # 总学习时长（秒）
    average_response_time: float = 0  # 平均响应时长（秒）

    # 时间范围
    first_activity: Optional[datetime] = None
    last_activity: Optional[datetime] = None

    # 连续统计
    current_streak: int = 0  # 当前连续答对次数
    longest_streak: int = 0  # 最长连续答对次数

    # 掌握程度
    mastery_level: Dict[str, float] = Field(
        default_factory=dict
    )  # 各知识点掌握程度 (0-1)

    @property
    def accuracy_rate(self) -> float:
        """正确率"""
        if self.total_questions == 0:
            return 0.0
        return self.total_correct / self.total_questions

    @property
    def completion_rate(self) -> float:
        """完成率（非放弃）"""
        if self.total_questions == 0:
            return 0.0
        completed = self.total_questions - self.total_partial
        return completed / self.total_questions


class LearningReport(BaseModel):
    """
    学习报告

    按时间范围生成的学习报告
    """
    report_id: Optional[str] = None
    student_id: str
    subject: str

    # 时间范围
    start_date: datetime
    end_date: datetime
    generated_at: datetime = Field(default_factory=datetime.now)

    # 总体统计
    total_sessions: int = 0
    total_questions: int = 0
    total_learning_time: float = 0

    # 正确率统计
    overall_accuracy: float = 0
    daily_accuracy: Dict[str, float] = Field(default_factory=dict)

    # 按题型统计
    by_problem_type: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict
    )

    # 学习趋势
    learning_trend: list = Field(default_factory=list)

    # 强弱项分析
    strong_areas: list = Field(default_factory=list)
    weak_areas: list = Field(default_factory=list)

    # 建议
    recommendations: list = Field(default_factory=list)


class ProgressUpdate(BaseModel):
    """
    进度更新请求
    """
    session_id: str
    student_id: str
    problem_type: str
    problem_text: str
    student_answer: str
    answer_result: str
    attempts: int = 1
    hints_used: int = 0
    response_duration: Optional[float] = None
    strategy_used: Optional[str] = None
    metaphor_used: Optional[str] = None


class ReportRequest(BaseModel):
    """
    报告生成请求
    """
    student_id: str
    subject: str = "数学"
    days: int = 7  # 最近多少天


class ProgressSummary(BaseModel):
    """
    进度摘要（API 响应）
    """
    student_id: str
    total_questions: int
    correct_count: int
    accuracy_rate: float
    learning_time_minutes: float
    current_streak: int
    strongest_type: Optional[str] = None
    weakest_type: Optional[str] = None
    last_activity: Optional[datetime] = None
