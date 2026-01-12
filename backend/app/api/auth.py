"""
用户认证 API 端点

提供用户注册、登录、密码管理等功能
"""

from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import get_db
from app.models.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    StudentCreate,
    StudentResponse,
    Token
)
from app.models.database import User, Student
from app.services.auth import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.post("/register", response_model=Token)
async def register(
    user_in: UserRegister,
    db: Session = Depends(get_db)
):
    """
    用户注册

    创建新用户账户
    """
    # 创建用户
    user = AuthService.create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        phone=user_in.phone
    )

    # 创建访问 Token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": "parent"},
        expires_delta=access_token_expires
    )

    # 更新最后登录时间
    AuthService.update_last_login(db, user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录

    使用用户名/邮箱和密码登录
    """
    # 验证用户
    user = AuthService.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )

    # 创建访问 Token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": "parent"},
        expires_delta=access_token_expires
    )

    # 更新最后登录时间
    AuthService.update_last_login(db, user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息

    需要认证
    """
    # 验证 Token
    token_data = AuthService.verify_token(token)

    # 获取用户
    user = db.query(User).filter(User.id == token_data.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return UserResponse.model_validate(user)


@router.post("/students", response_model=StudentResponse)
async def create_student(
    student_in: StudentCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    创建学生账户

    为当前用户创建一个学生账户
    """
    # 验证 Token
    token_data = AuthService.verify_token(token)

    # 创建学生
    db_student = Student(
        parent_id=token_data.user_id,
        name=student_in.name,
        nickname=student_in.nickname,
        age=student_in.age,
        grade=student_in.grade,
        avatar_url=student_in.avatar_url,
        is_active=True
    )

    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return StudentResponse.model_validate(db_student)


@router.get("/students", response_model=List[StudentResponse])
async def get_students(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有学生

    需要认证
    """
    # 验证 Token
    token_data = AuthService.verify_token(token)

    # 获取学生列表
    students = db.query(Student).filter(
        Student.parent_id == token_data.user_id,
        Student.is_active == True
    ).all()

    return [StudentResponse.model_validate(s) for s in students]


@router.get("/health")
async def health_check():
    """
    健康检查

    验证认证服务是否正常运行
    """
    return {
        "status": "healthy",
        "service": "认证服务"
    }
