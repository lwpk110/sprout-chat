"""
语音服务抽象层 - 接口定义

遵循 SOLID 原则：
- 接口隔离原则 (ISP): ASR 和 TTS 分离
- 依赖倒置原则 (DIP): 业务层依赖抽象，不依赖具体实现
"""

from abc import ABC, abstractmethod
from typing import Protocol, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ProviderType(str, Enum):
    """语音服务提供商类型"""
    DOUBAO = "doubao"  # 豆包
    AZURE = "azure"    # Azure
    GOOGLE = "google"  # Google
    ALIYUN = "aliyun"  # 阿里云
    WEB_SPEECH = "web_speech"  # 浏览器内置（前端使用）


class AudioFormat(str, Enum):
    """音频格式"""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    PCM = "pcm"
    OPUS = "opus"


class VoiceType(str, Enum):
    """语音类型"""
    FEMALE = "female"
    MALE = "male"
    CHILD = "child"  # 儿童语音（适合一年级学生）


# ============================================================================
# 数据模型 (Data Models)
# ============================================================================

@dataclass
class AudioRequest:
    """
    音频请求通用模型

    用于 ASR 和 TTS 的请求参数
    """
    audio_data: bytes  # 音频二进制数据
    format: AudioFormat  # 音频格式
    sample_rate: int = 16000  # 采样率（Hz）
    channels: int = 1  # 声道数（1=单声道, 2=立体声）

    # 元数据（用于追踪和审计）
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TranscriptionResult:
    """
    ASR 转录结果

    所有 ASR 服务实现必须返回此结构
    """
    text: str  # 转录文本
    confidence: float  # 置信度 (0.0 - 1.0)
    language: str  # 语言代码（如 "zh-CN"）

    # 时间戳（可选）
    duration_ms: Optional[int] = None  # 音频时长（毫秒）

    # 词级时间戳（可选，用于前端高亮）
    words: Optional[List[Dict[str, Any]]] = None

    # 元数据
    provider: Optional[ProviderType] = None
    request_id: Optional[str] = None  # 用于追踪


@dataclass
class SynthesisRequest:
    """
    TTS 合成请求

    用于 TTS 的请求参数
    """
    text: str  # 要合成的文本
    voice_type: VoiceType = VoiceType.FEMALE  # 语音类型
    language: str = "zh-CN"  # 语言代码

    # 音频参数
    format: AudioFormat = AudioFormat.MP3
    sample_rate: int = 16000

    # 语速和音调（0.0 - 2.0，1.0 为正常）
    rate: float = 1.0
    pitch: float = 1.0

    # 元数据
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SynthesisResult:
    """
    TTS 合成结果

    所有 TTS 服务实现必须返回此结构
    """
    audio_data: bytes  # 音频二进制数据
    format: AudioFormat  # 音频格式
    duration_ms: int  # 音频时长（毫秒）

    # 元数据
    provider: Optional[ProviderType] = None
    voice_name: Optional[str] = None  # 具体使用的语音名称
    request_id: Optional[str] = None


@dataclass
class VoiceInfo:
    """
    语音信息

    用于列出可用的语音选项
    """
    voice_id: str  # 语音唯一标识
    name: str  # 语音名称（如 "小云（女声）"）
    language: str  # 语言代码
    voice_type: VoiceType  # 语音类型
    sample_rate: int  # 支持的采样率
    description: Optional[str] = None  # 描述


# ============================================================================
# ASR 接口 (Automatic Speech Recognition)
# ============================================================================

class ASRInterface(Protocol):
    """
    语音转文字接口

    遵循接口隔离原则（ISP），只包含 ASR 相关方法
    遵循里氏替换原则（LSP），所有实现可以无缝替换

    契约（Contract）:
        - 所有实现必须返回 TranscriptionResult
        - transcription_latency_ms 包含端到端延迟
        - 失败时抛出 ASRError 异常
    """

    async def transcribe(
        self,
        request: AudioRequest
    ) -> TranscriptionResult:
        """
        转录音频为文字

        Args:
            request: 音频请求对象

        Returns:
            TranscriptionResult: 转录结果

        Raises:
            ASRError: 转录失败时抛出
            ValueError: 请求参数无效

        契约:
            - 返回的 text 必须是非空字符串
            - confidence 必须在 [0.0, 1.0] 范围内
            - transcription_latency_ms 必须 >= 0
        """
        ...

    async def batch_transcribe(
        self,
        requests: List[AudioRequest]
    ) -> List[TranscriptionResult]:
        """
        批量转录音频（可选实现）

        默认实现：循环调用 transcribe()
        优化实现：使用批量 API（如果服务提供商支持）

        Args:
            requests: 音频请求列表

        Returns:
            List[TranscriptionResult]: 转录结果列表

        契约:
            - 返回列表长度必须与输入列表长度一致
            - 失败的请求在结果中抛出异常
        """
        ...

    def get_supported_formats(self) -> List[AudioFormat]:
        """
        获取支持的音频格式

        Returns:
            List[AudioFormat]: 支持的格式列表

        契约:
            - 返回列表必须非空
            - 必须包含至少一种常见格式（WAV/MP3）
        """
        ...

    def get_supported_languages(self) -> List[str]:
        """
        获取支持的语言代码

        Returns:
            List[str]: 语言代码列表（如 ["zh-CN", "en-US"]）

        契约:
            - 返回列表必须非空
            - 语言代码必须符合 BCP 47 标准
        """
        ...


# ============================================================================
# TTS 接口 (Text-to-Speech)
# ============================================================================

class TTSInterface(Protocol):
    """
    文字转语音接口

    遵循接口隔离原则（ISP），只包含 TTS 相关方法
    遵循里氏替换原则（LSP），所有实现可以无缝替换

    契约（Contract）:
        - 所有实现必须返回 SynthesisResult
        - synthesis_latency_ms 包含端到端延迟
        - 失败时抛出 TTSError 异常
    """

    async def synthesize(
        self,
        request: SynthesisRequest
    ) -> SynthesisResult:
        """
        合成文字为语音

        Args:
            request: 合成请求对象

        Returns:
            SynthesisResult: 合成结果（音频数据）

        Raises:
            TTSError: 合成失败时抛出
            ValueError: 请求参数无效

        契约:
            - 返回的 audio_data 必须是非空字节
            - duration_ms 必须 >= 0
            - synthesis_latency_ms 必须 >= 0
        """
        ...

    def get_available_voices(
        self,
        language: Optional[str] = None
    ) -> List[VoiceInfo]:
        """
        获取可用的语音列表

        Args:
            language: 语言代码过滤（可选）

        Returns:
            List[VoiceInfo]: 语音信息列表

        契约:
            - 返回列表必须非空
            - 每个语音必须包含唯一 voice_id
        """
        ...

    def get_supported_formats(self) -> List[AudioFormat]:
        """
        获取支持的音频格式

        Returns:
            List[AudioFormat]: 支持的格式列表

        契约:
            - 返回列表必须非空
            - 必须包含至少一种常见格式（MP3/WAV）
        """
        ...


# ============================================================================
# 异常类 (Exception Hierarchy)
# ============================================================================

class VoiceServiceError(Exception):
    """语音服务基础异常"""

    def __init__(
        self,
        message: str,
        provider: ProviderType,
        request_id: Optional[str] = None
    ):
        self.message = message
        self.provider = provider
        self.request_id = request_id
        super().__init__(f"[{provider.value}] {message}")


class ASRError(VoiceServiceError):
    """ASR 转录异常"""
    pass


class TTSError(VoiceServiceError):
    """TTS 合成异常"""
    pass


class AuthenticationError(VoiceServiceError):
    """认证失败异常（如 API Key 无效）"""
    pass


class RateLimitError(VoiceServiceError):
    """速率限制异常"""
    pass


class QuotaExceededError(VoiceServiceError):
    """配额超限异常"""
    pass
