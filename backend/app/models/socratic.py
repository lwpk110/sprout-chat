"""
苏格拉底响应数据模型 (LWP-13)

定义请求和响应的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ScaffoldingLevel(str, Enum):
    """脚手架层级枚举"""
    HIGHLY_GUIDED = "highly_guided"  # 高度引导
    MODERATE = "moderate"  # 中度引导（默认）
    MINIMAL = "minimal"  # 最小引导


class SocraticRequest(BaseModel):
    """苏格拉底响应生成请求"""
    student_message: str = Field(..., description="学生的输入消息")
    problem_context: Optional[str] = Field(None, description="问题背景（如 OCR 识别的题目）")
    scaffolding_level: ScaffoldingLevel = Field(
        default=ScaffoldingLevel.MODERATE,
        description="脚手架层级"
    )
    conversation_id: Optional[str] = Field(None, description="会话 ID")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="对话历史"
    )
    student_level: Optional[str] = Field(None, description="学生年级水平")

    class Config:
        json_schema_extra = {
            "example": {
                "student_message": "1 + 1 = ?",
                "problem_context": "数学加法题",
                "scaffolding_level": "moderate",
                "conversation_id": "conv-123"
            }
        }


class ValidationResult(BaseModel):
    """响应验证结果"""
    is_valid: bool = Field(..., description="是否通过验证")
    contains_question: bool = Field(..., description="是否包含引导性问题")
    contains_direct_answer: bool = Field(..., description="是否包含直接答案")
    tone_appropriate: bool = Field(..., description="语气是否温柔鼓励")
    length_appropriate: bool = Field(..., description="长度是否适中")
    score: float = Field(..., ge=0.0, le=1.0, description="综合得分")
    reasons: List[str] = Field(default_factory=list, description="验证原因列表")

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "contains_question": True,
                "contains_direct_answer": False,
                "tone_appropriate": True,
                "length_appropriate": True,
                "score": 0.95,
                "reasons": ["包含引导性问题", "语气温柔", "长度适中"]
            }
        }


class SocraticResponse(BaseModel):
    """苏格拉底响应"""
    response: str = Field(..., description="生成的引导式响应")
    is_socratic: bool = Field(..., description="是否符合苏格拉底教学法")
    validation_score: float = Field(..., ge=0.0, le=1.0, description="验证得分")
    scaffolding_level: ScaffoldingLevel = Field(..., description="使用的脚手架层级")
    validation_result: Optional[ValidationResult] = Field(None, description="详细验证结果")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
                "is_socratic": True,
                "validation_score": 0.95,
                "scaffolding_level": "moderate",
                "validation_result": {
                    "is_valid": True,
                    "contains_question": True,
                    "contains_direct_answer": False,
                    "tone_appropriate": True,
                    "length_appropriate": True,
                    "score": 0.95,
                    "reasons": ["包含引导性问题", "语气温柔", "长度适中"]
                },
                "metadata": {
                    "model": "claude-3-5-sonnet",
                    "tokens_used": 100
                }
            }
        }


class SocraticError(BaseModel):
    """苏格拉底响应错误"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "APIError",
                "message": "Claude API 调用失败",
                "details": {
                    "status_code": 500,
                    "raw_error": "Connection timeout"
                }
            }
        }
