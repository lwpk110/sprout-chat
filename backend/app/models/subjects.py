"""
多科目扩展数据模型

支持语文、英语、科学等多科目的学习和追踪
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
from pydantic import BaseModel, Field


class Subject(Enum):
    """科目枚举"""
    MATH = "数学"
    CHINESE = "语文"
    ENGLISH = "英语"
    SCIENCE = "科学"


class MathProblemType(Enum):
    """数学题型"""
    ADDITION = "加法"
    SUBTRACTION = "减法"
    MULTIPLICATION = "乘法"
    DIVISION = "除法"
    COMPARISON = "比较"
    WORD_PROBLEM = "应用题"


class ChineseProblemType(Enum):
    """语文题型"""
    PINYIN = "拼音"
    RECOGNITION = "识字"
    WRITING = "写字"
    RECITATION = "背诵"
    COMPREHENSION = "阅读理解"


class EnglishProblemType(Enum):
    """英语题型"""
    ALPHABET = "字母"
    VOCABULARY = "词汇"
    SIMPLE_SENTENCES = "简单句子"
    LISTENING = "听力"
    SPEAKING = "口语"


class ScienceProblemType(Enum):
    """科学题型"""
    NATURE = "自然观察"
    EXPERIMENT = "小实验"
    PHENOMENON = "科学现象"
    DISCOVERY = "探索发现"


class SubjectConfig(BaseModel):
    """
    科目配置
    """
    subject: Subject
    enabled: bool = True
    difficulty_level: str = "简单"  # 简单、中等、困难
    age_appropriate: bool = True  # 是否适合当前年龄

    # 教学设置
    teaching_style: str = "引导式"  # 引导式、讲解式、互动式
    use_metaphor: bool = True
    use_games: bool = True

    # 自定义配置
    custom_settings: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        pass


class Problem(BaseModel):
    """
    通用题目模型
    """
    problem_id: Optional[str] = None
    subject: Subject
    problem_type: str  # 各科目的题型
    content: str  # 题目内容
    options: Optional[List[str]] = None  # 选项（选择题）
    correct_answer: str  # 正确答案
    difficulty: str = "简单"  # 难度

    # 扩展字段
    image_url: Optional[str] = None  # 题目图片
    audio_url: Optional[str] = None  # 题目音频（语文/英语）
    explanation: Optional[str] = None  # 解析

    # 标签和分类
    tags: List[str] = Field(default_factory=list)
    knowledge_points: List[str] = Field(default_factory=list)

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        pass


class StudentAnswer(BaseModel):
    """
    学生答题记录（多科目）
    """
    answer_id: Optional[str] = None
    student_id: str
    problem_id: str
    subject: Subject
    problem_type: str

    # 答题信息
    student_answer: str
    is_correct: bool
    attempts: int = 1

    # 时间信息
    question_time: datetime = Field(default_factory=datetime.now)
    answer_time: Optional[datetime] = None
    response_duration: Optional[float] = None

    # 额外数据
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        pass


class SubjectProgress(BaseModel):
    """
    科目进度
    """
    student_id: str
    subject: Subject

    # 总体统计
    total_problems: int = 0
    correct_count: int = 0
    accuracy_rate: float = 0.0

    # 按题型统计
    by_problem_type: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict
    )

    # 学习时长
    total_learning_time: float = 0  # 总学习时长（秒）

    # 掌握的知识点
    mastered_points: List[str] = Field(default_factory=list)
    weak_points: List[str] = Field(default_factory=list)

    # 时间范围
    first_activity: Optional[datetime] = None
    last_activity: Optional[datetime] = None

    class Config:
        pass


class SubjectReport(BaseModel):
    """
    科目学习报告
    """
    report_id: Optional[str] = None
    student_id: str
    subject: Subject

    # 时间范围
    start_date: datetime
    end_date: datetime
    generated_at: datetime = Field(default_factory=datetime.now)

    # 总体统计
    total_problems: int = 0
    correct_count: int = 0
    accuracy_rate: float = 0.0

    # 按题型统计
    by_problem_type: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict
    )

    # 学习趋势
    learning_trend: List[Dict[str, Any]] = Field(default_factory=list)

    # 强弱项
    strong_areas: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)

    # 建议
    recommendations: List[str] = Field(default_factory=list)

    class Config:
        pass


class MultiSubjectSummary(BaseModel):
    """
    多科目汇总
    """
    student_id: str

    # 各科目进度
    subject_progress: Dict[str, SubjectProgress] = Field(
        default_factory=dict
    )

    # 总体统计
    total_problems: int = 0
    total_correct: int = 0
    overall_accuracy: float = 0.0

    # 最强和最弱科目
    strongest_subject: Optional[str] = None
    weakest_subject: Optional[str] = None

    # 学习时长分布
    learning_time_by_subject: Dict[str, float] = Field(
        default_factory=dict
    )

    # 生成时间
    generated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        pass
