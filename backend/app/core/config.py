"""
小芽家教 - 核心配置

支持开发和生产环境配置
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import json
import os


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    app_name: str = "小芽家教"
    app_version: str = "0.1.0"
    environment: str = "development"  # development, staging, production
    debug: bool = True

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库
    database_url: str = "sqlite:///./sprout_chat.db"

    # 生产环境数据库配置
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = "sprout_chat"

    # CORS - 支持多个环境
    cors_origins: str = '["http://localhost:3000", "http://localhost:5173"]'

    # 生产环境 CORS 配置
    frontend_url: Optional[str] = None  # 生产环境前端地址

    # AI 配置
    ai_provider: str = "openai"  # anthropic 或 openai
    ai_model: str = "claude-3-5-sonnet-20241022"
    ai_vision_model: str = "glm-4v-flash"  # 视觉模型（图像识别）- 免费版本
    ai_max_tokens: int = 1000
    ai_temperature: float = 0.7
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    ai_timeout_seconds: int = 30
    ai_max_retries: int = 3

    # 语音配置
    stt_provider: str = "web_speech"
    tts_provider: str = "web_speech"

    # 会话管理
    session_timeout_minutes: int = 30
    max_conversation_history: int = 10

    # JWT 配置
    secret_key: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 天
    refresh_token_expire_days: int = 30  # 30 天

    # 日志配置
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file: Optional[str] = None  # 生产环境建议配置
    log_rotation: bool = True  # 日志轮转
    log_max_bytes: int = 10 * 1024 * 1024  # 10 MB
    log_backup_count: int = 5  # 保留 5 个备份

    # 速率限制（生产环境）
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100  # 每分钟请求数
    rate_limit_window: int = 60  # 时间窗口（秒）

    # 安全配置
    allowed_hosts: List[str] = ["*"]  # 生产环境应配置具体域名
    https_only: bool = False  # 生产环境建议启用
    hsts_enabled: bool = False  # HTTP Strict Transport Security

    # 缓存配置（可选）
    cache_enabled: bool = False
    cache_ttl_seconds: int = 300  # 5 分钟
    redis_url: Optional[str] = None  # Redis 连接字符串

    # 监控配置（可选）
    sentry_dsn: Optional[str] = None  # Sentry 错误追踪
    apm_enabled: bool = False  # 应用性能监控

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """将 JSON 字符串转换为列表"""
        try:
            origins = json.loads(self.cors_origins)
            # 生产环境添加前端 URL
            if self.environment == "production" and self.frontend_url:
                if self.frontend_url not in origins:
                    origins.append(self.frontend_url)
            return origins
        except:
            return ["http://localhost:3000"]

    @property
    def database_url_resolved(self) -> str:
        """解析数据库连接字符串"""
        # 如果已配置完整 URL，直接使用
        if "postgresql://" in self.database_url or "sqlite://" in self.database_url:
            return self.database_url

        # 生产环境使用 PostgreSQL
        if self.environment == "production" and all([
            self.db_host, self.db_port, self.db_user,
            self.db_password, self.db_name
        ]):
            return (
                f"postgresql://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )

        # 开发环境默认 SQLite
        return self.database_url

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"


settings = Settings()
