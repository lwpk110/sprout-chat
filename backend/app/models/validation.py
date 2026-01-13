"""
响应验证系统数据模型 (LWP-16)

定义多维度响应验证的数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from app.models.socratic import ScaffoldingLevel


class StudentContext(BaseModel):
    """学生上下文信息"""
    grade: int = Field(default=1, description="学生年级")
    problem_type: str = Field(default="general", description="问题类型（math, reading, general 等）")
    previous_attempts: List[str] = Field(
        default_factory=list,
        description="之前的尝试记录"
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="对话历史"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "grade": 1,
                "problem_type": "math",
                "previous_attempts": ["1 + 1 = 2", "1 + 1 = 3"],
                "conversation_history": [
                    {"role": "user", "content": "1 + 1 = ?"},
                    {"role": "assistant", "content": "🌱 你觉得..."}
                ]
            }
        }


class ValidationResult(BaseModel):
    """
    多维度响应验证结果

    五维验证系统：
    1. 引导性问题检测 (pattern-based)
    2. 直接答案检测 (pattern-based + AI-based)
    3. 脚手架层级对齐检测
    4. 问题质量评估 (AI-based)
    5. 上下文相关性验证 (AI-based)
    """
    is_valid: bool = Field(..., description="是否通过验证")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="综合得分 (0.0 - 1.0)")

    # 分维度分数
    guiding_question_score: float = Field(..., ge=0.0, le=1.0, description="引导性问题得分")
    direct_answer_violation: bool = Field(..., description="是否包含直接答案")
    scaffolding_alignment_score: float = Field(..., ge=0.0, le=1.0, description="脚手架层级对齐得分")
    question_quality_score: float = Field(..., ge=0.0, le=1.0, description="问题质量得分")
    context_relevance_score: float = Field(..., ge=0.0, le=1.0, description="上下文相关性得分")

    # 详细信息
    failure_reasons: List[str] = Field(default_factory=list, description="失败原因列表")
    suggestions: List[str] = Field(default_factory=list, description="改进建议列表")

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "overall_score": 0.95,
                "guiding_question_score": 1.0,
                "direct_answer_violation": False,
                "scaffolding_alignment_score": 0.9,
                "question_quality_score": 0.95,
                "context_relevance_score": 0.9,
                "failure_reasons": [],
                "suggestions": []
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_valid": self.is_valid,
            "overall_score": self.overall_score,
            "guiding_question_score": self.guiding_question_score,
            "direct_answer_violation": self.direct_answer_violation,
            "scaffolding_alignment_score": self.scaffolding_alignment_score,
            "question_quality_score": self.question_quality_score,
            "context_relevance_score": self.context_relevance_score,
            "failure_reasons": self.failure_reasons,
            "suggestions": self.suggestions
        }


class ValidationRequest(BaseModel):
    """响应验证请求"""
    response: str = Field(..., description="待验证的响应")
    scaffolding_level: ScaffoldingLevel = Field(
        default=ScaffoldingLevel.MODERATE,
        description="预期的脚手架层级"
    )
    student_context: Optional[StudentContext] = Field(
        default=None,
        description="学生上下文信息"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
                "scaffolding_level": "moderate",
                "student_context": {
                    "grade": 1,
                    "problem_type": "math",
                    "previous_attempts": ["1 + 1 = 2"]
                }
            }
        }


class ValidationSeverity(str, Enum):
    """验证严重级别"""
    CRITICAL = "critical"  # 严重违规（包含直接答案）
    WARNING = "warning"    # 轻微问题（质量不高）
    INFO = "info"          # 信息提示
