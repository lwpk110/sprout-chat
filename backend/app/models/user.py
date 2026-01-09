"""
用户认证和授权模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    """用户角色"""
    PARENT = "parent"  # 家长
    STUDENT = "student"  # 学生
    ADMIN = "admin"  # 管理员


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    full_name: str = Field(..., min_length=1, max_length=100, description="姓名")
    phone: Optional[str] = Field(None, description="手机号")


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class StudentCreate(BaseModel):
    """创建学生请求"""
    name: str = Field(..., min_length=1, max_length=50, description="学生姓名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    age: int = Field(..., ge=5, le=12, description="年龄（5-12岁）")
    grade: Optional[str] = Field(None, description="年级")
    avatar_url: Optional[str] = Field(None, description="头像URL")


class StudentResponse(BaseModel):
    """学生响应"""
    id: int
    parent_id: int
    name: str
    nickname: Optional[str] = None
    age: int
    grade: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token 数据"""
    user_id: int
    username: str
    role: UserRole


class PasswordChange(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class PasswordReset(BaseModel):
    """重置密码请求"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """确认重置密码"""
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)
