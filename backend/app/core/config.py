"""
小芽家教 - 核心配置
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    app_name: str = "小芽家教"
    app_version: str = "0.1.0"
    debug: bool = True

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库
    database_url: str = "sqlite:///./sprout_chat.db"

    # CORS
    cors_origins: str = '["http://localhost:3000", "http://localhost:5173"]'

    # AI 配置
    ai_provider: str = "anthropic"  # anthropic 或 openai
    ai_model: str = "claude-3-5-sonnet-20241022"
    ai_vision_model: str = "glm-4.6v"  # 视觉模型（图像识别）
    ai_max_tokens: int = 1000
    ai_temperature: float = 0.7
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://open.bigmodel.cn/api/paas/v4/"

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

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """将 JSON 字符串转换为列表"""
        try:
            return json.loads(self.cors_origins)
        except:
            return ["http://localhost:3000"]


settings = Settings()