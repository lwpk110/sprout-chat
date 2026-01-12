"""
用户认证服务

实现用户注册、登录、密码管理等功能
"""

from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import TokenData, UserRole


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    认证服务

    处理用户注册、登录、Token 管理等
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            plain_password: 明文密码
            hashed_password: 加密后的密码

        Returns:
            是否匹配
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        获取密码哈希

        Args:
            password: 明文密码

        Returns:
            加密后的密码
        """
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问 Token

        Args:
            data: Token 数据
            expires_delta: 过期时间

        Returns:
            JWT Token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> TokenData:
        """
        验证 Token

        Args:
            token: JWT Token

        Returns:
            Token 数据

        Raises:
            HTTPException: Token 无效
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.ALGORITHM]
            )

            user_id_str: str = payload.get("sub")
            username: str = payload.get("username")
            role: str = payload.get("role", UserRole.PARENT)

            if user_id_str is None or username is None:
                raise credentials_exception

            token_data = TokenData(
                user_id=int(user_id_str),
                username=username,
                role=role
            )

            return token_data

        except (JWTError, ValueError):
            raise credentials_exception

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> Optional[object]:
        """
        验证用户

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            用户对象或 None
        """
        from app.models.database import User

        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        full_name: str,
        phone: Optional[str] = None
    ) -> object:
        """
        创建用户

        Args:
            db: 数据库会话
            username: 用户名
            email: 邮箱
            password: 密码
            full_name: 姓名
            phone: 手机号

        Returns:
            用户对象
        """
        from app.models.database import User

        # 检查用户名是否已存在
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被注册"
                )

        # 创建用户
        hashed_password = AuthService.get_password_hash(password)
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            phone=phone,
            is_active=True,
            is_verified=False  # 需要邮箱验证
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def update_last_login(db: Session, user_id: int):
        """
        更新最后登录时间

        Args:
            db: 数据库会话
            user_id: 用户 ID
        """
        from app.models.database import User

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
