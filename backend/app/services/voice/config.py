"""
语音服务配置管理

使用 Pydantic Settings 实现类型安全的配置管理
支持开发/生产环境分离
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict
from pydantic import Field, validator
from .interfaces import ProviderType, AudioFormat


class VoiceServiceSettings(BaseSettings):
    """
    语音服务配置

    支持环境变量和 .env 文件
    """

    # ========================================================================
    # 全局配置
    # ========================================================================

    # 默认服务提供商
    asr_provider: ProviderType = Field(
        default=ProviderType.DOUBAO,
        description="ASR 默认提供商"
    )
    tts_provider: ProviderType = Field(
        default=ProviderType.DOUBAO,
        description="TTS 默认提供商"
    )

    # 降级配置（按优先级排序）
    asr_fallback_providers: List[ProviderType] = Field(
        default=[ProviderType.AZURE, ProviderType.GOOGLE],
        description="ASR 降级提供商列表"
    )
    tts_fallback_providers: List[ProviderType] = Field(
        default=[ProviderType.AZURE, ProviderType.GOOGLE],
        description="TTS 降级提供商列表"
    )

    # 超时配置
    asr_timeout_seconds: int = Field(
        default=10,
        ge=1,
        le=60,
        description="ASR 请求超时时间（秒）"
    )
    tts_timeout_seconds: int = Field(
        default=10,
        ge=1,
        le=60,
        description="TTS 请求超时时间（秒）"
    )

    # 重试配置
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="最大重试次数"
    )
    retry_backoff_factor: float = Field(
        default=1.5,
        ge=1.0,
        le=5.0,
        description="重试退避因子（指数）"
    )

    # 缓存配置（TTS）
    tts_cache_enabled: bool = Field(
        default=True,
        description="是否启用 TTS 缓存"
    )
    tts_cache_ttl_seconds: int = Field(
        default=3600,
        ge=60,
        description="TTS 缓存过期时间（秒）"
    )

    # ========================================================================
    # 豆包 (Doubao) 配置
    # ========================================================================

    doubao_api_key: str = Field(
        default="",
        description="豆包 API Key"
    )
    doubao_app_id: str = Field(
        default="",
        description="豆包应用 ID"
    )
    doubao_region: str = Field(
        default="cn-north-1",
        description="豆包区域"
    )
    doubao_endpoint: Optional[str] = Field(
        default=None,
        description="豆包自定义端点（覆盖默认）"
    )

    # 豆包 ASR 配置
    doubao_asr_model: str = Field(
        default="general",
        description="豆包 ASR 模型（general/phone/smart_call）"
    )
    doubao_asr_language: str = Field(
        default="zh-CN",
        description="豆包 ASR 语言"
    )

    # 豆包 TTS 配置
    doubao_tts_voice: str = Field(
        default="zh_female_xiaoyun",
        description="豆包 TTS 默认语音"
    )
    doubao_tts_format: AudioFormat = Field(
        default=AudioFormat.MP3,
        description="豆包 TTS 音频格式"
    )

    # ========================================================================
    # Azure 配置
    # ========================================================================

    azure_speech_key: str = Field(
        default="",
        description="Azure 语音服务密钥"
    )
    azure_speech_region: str = Field(
        default="eastasia",
        description="Azure 语音服务区域"
    )
    azure_endpoint: Optional[str] = Field(
        default=None,
        description="Azure 自定义端点（覆盖默认）"
    )

    # Azure ASR 配置
    azure_asr_language: str = Field(
        default="zh-CN",
        description="Azure ASR 语言"
    )
    azure_asr_profanity_option: str = Field(
        default="Masked",
        description="Azure ASR 脏词处理（Masked/Removed/Raw）"
    )

    # Azure TTS 配置
    azure_tts_voice: str = Field(
        default="zh-CN-XiaoxiaoNeural",
        description="Azure TTS 默认语音"
    )
    azure_tts_format: AudioFormat = Field(
        default=AudioFormat.MP3,
        description="Azure TTS 音频格式"
    )

    # ========================================================================
    # Google Cloud 配置
    # ========================================================================

    google_cloud_credentials_path: str = Field(
        default="",
        description="Google Cloud 服务账号 JSON 文件路径"
    )
    google_cloud_project_id: str = Field(
        default="",
        description="Google Cloud 项目 ID"
    )

    # Google ASR 配置
    google_asr_language: str = Field(
        default="zh-CN",
        description="Google ASR 语言"
    )
    google_asr_model: str = Field(
        default="default",
        description="Google ASR 模型（default/phone_call/video）"
    )
    google_asr_enhanced: bool = Field(
        default=True,
        description="Google ASR 增强模型"
    )

    # Google TTS 配置
    google_tts_voice: str = Field(
        default="zh-CN-Wavenet-A",
        description="Google TTS 默认语音"
    )
    google_tts_gender: str = Field(
        default="FEMALE",
        description="Google TTS 性别"
    )
    google_tts_encoding: str = Field(
        default="MP3",
        description="Google TTS 音频编码"
    )

    # ========================================================================
    # 阿里云 (Aliyun) 配置
    # ========================================================================

    aliyun_access_key_id: str = Field(
        default="",
        description="阿里云 Access Key ID"
    )
    aliyun_access_key_secret: str = Field(
        default="",
        description="阿里云 Access Key Secret"
    )
    aliyun_region: str = Field(
        default="cn-shanghai",
        description="阿里云区域"
    )
    aliyun_app_key: str = Field(
        default="",
        description="阿里云 NLS App Key"
    )

    # 阿里云 ASR 配置
    aliyun_asr_format: AudioFormat = Field(
        default=AudioFormat.WAV,
        description="阿里云 ASR 音频格式"
    )
    aliyun_asr_sample_rate: int = Field(
        default=16000,
        description="阿里云 ASR 采样率"
    )
    aliyun_asr_language: str = Field(
        default="zh-CN",
        description="阿里云 ASR 语言"
    )

    # 阿里云 TTS 配置
    aliyun_tts_voice: str = Field(
        default="xiaoyun",
        description="阿里云 TTS 默认语音"
    )
    aliyun_tts_volume: int = Field(
        default=50,
        ge=0,
        le=100,
        description="阿里云 TTS 音量（0-100）"
    )
    aliyun_tts_speech_rate: int = Field(
        default=0,
        ge=-500,
        le=500,
        description="阿里云 TTS 语速（-500 到 500）"
    )

    # ========================================================================
    # 安全配置
    # ========================================================================

    enable_request_logging: bool = Field(
        default=True,
        description="是否记录请求日志"
    )
    sanitize_audio_logs: bool = Field(
        default=True,
        description="日志中是否隐藏音频数据（仅显示哈希）"
    )
    audit_log_enabled: bool = Field(
        default=True,
        description="是否启用审计日志"
    )

    # ========================================================================
    # 监控配置
    # ========================================================================

    metrics_enabled: bool = Field(
        default=True,
        description="是否启用指标收集"
    )
    tracing_enabled: bool = Field(
        default=True,
        description="是否启用分布式追踪"
    )

    # ========================================================================
    # 限流配置
    # ========================================================================

    rate_limit_enabled: bool = Field(
        default=True,
        description="是否启用限流"
    )
    rate_limit_requests_per_minute: int = Field(
        default=60,
        ge=1,
        description="每分钟请求限制"
    )

    # ========================================================================
    # Pydantic 配置
    # ========================================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========================================================================
    # 验证器 (Validators)
    # ========================================================================

    @validator("asr_provider", "tts_provider")
    def validate_provider(cls, v):
        """验证服务提供商是否支持"""
        if v == ProviderType.WEB_SPEECH:
            raise ValueError(
                "WEB_SPEECH 仅用于前端，后端不支持。"
                "请使用 DOUBAO/AZURE/GOOGLE/ALIYUN"
            )
        return v

    @validator("doubao_api_key", "azure_speech_key")
    def validate_api_key(cls, v, field):
        """验证必需的 API Key"""
        # 注意：这里只验证是否为空，实际验证在服务初始化时
        if not v:
            # 开发环境可以跳过验证
            import os
            if os.getenv("ENVIRONMENT") == "development":
                return v
            # 生产环境警告（不抛异常，因为可能使用其他提供商）
            import warnings
            warnings.warn(f"{field.name} is empty in production")
        return v

    # ========================================================================
    # 辅助方法
    # ========================================================================

    def get_provider_config(self, provider: ProviderType) -> Dict[str, any]:
        """
        获取特定提供商的配置

        Args:
            provider: 服务提供商类型

        Returns:
            Dict[str, Any]: 提供商配置字典
        """
        configs = {
            ProviderType.DOUBAO: {
                "api_key": self.doubao_api_key,
                "app_id": self.doubao_app_id,
                "region": self.doubao_region,
                "endpoint": self.doubao_endpoint,
                "timeout": self.asr_timeout_seconds,
            },
            ProviderType.AZURE: {
                "api_key": self.azure_speech_key,
                "region": self.azure_speech_region,
                "endpoint": self.azure_endpoint,
                "timeout": self.asr_timeout_seconds,
            },
            ProviderType.GOOGLE: {
                "credentials_path": self.google_cloud_credentials_path,
                "project_id": self.google_cloud_project_id,
                "timeout": self.asr_timeout_seconds,
            },
            ProviderType.ALIYUN: {
                "access_key_id": self.aliyun_access_key_id,
                "access_key_secret": self.aliyun_access_key_secret,
                "region": self.aliyun_region,
                "app_key": self.aliyun_app_key,
                "timeout": self.asr_timeout_seconds,
            },
        }
        return configs.get(provider, {})

    def is_provider_configured(self, provider: ProviderType) -> bool:
        """
        检查提供商是否已配置

        Args:
            provider: 服务提供商类型

        Returns:
            bool: 是否已配置
        """
        config = self.get_provider_config(provider)

        # 检查关键配置是否存在
        required_keys = {
            ProviderType.DOUBAO: ["api_key"],
            ProviderType.AZURE: ["api_key"],
            ProviderType.GOOGLE: ["credentials_path", "project_id"],
            ProviderType.ALIYUN: ["access_key_id", "access_key_secret", "app_key"],
        }

        if provider not in required_keys:
            return False

        for key in required_keys[provider]:
            if not config.get(key):
                return False

        return True


# 全局配置实例
voice_settings = VoiceServiceSettings()
