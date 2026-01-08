"""
数据模型和 Schema 定义
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 请求模型 ==========

class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    student_id: str = Field(..., description="学生 ID")
    subject: str = Field(default="数学", description="科目")
    student_age: int = Field(default=6, description="学生年龄")
    topic: str = Field(default="基础对话", description="对话主题")


class VoiceInputRequest(BaseModel):
    """语音输入请求"""
    session_id: str = Field(..., description="会话 ID")
    transcript: str = Field(..., description="语音识别文本")
    confidence: Optional[float] = Field(None, description="识别置信度")


class TextInputRequest(BaseModel):
    """文字输入请求"""
    session_id: str = Field(..., description="会话 ID")
    content: str = Field(..., description="输入内容")


class GetHistoryRequest(BaseModel):
    """获取历史请求"""
    session_id: str = Field(..., description="会话 ID")
    limit: int = Field(default=10, description="返回数量限制")


# ========== 响应模型 ==========

class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    student_id: str
    subject: str
    student_age: int
    created_at: datetime
    is_valid: bool


class MessageResponse(BaseModel):
    """消息响应"""
    role: str
    content: str
    timestamp: str


class ConversationResponse(BaseModel):
    """对话响应"""
    session_id: str
    response: str
    timestamp: str


class HistoryResponse(BaseModel):
    """历史记录响应"""
    session_id: str
    messages: List[MessageResponse]
    total_count: int


class SessionStatsResponse(BaseModel):
    """会话统计响应"""
    session_id: str
    student_id: str
    subject: str
    message_count: int
    duration_seconds: int
    created_at: str
    last_activity: str
    is_valid: bool


# ========== 错误模型 ==========

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())