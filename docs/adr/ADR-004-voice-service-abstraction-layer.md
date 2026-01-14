# ADR-004: 语音服务抽象层架构设计

## 状态
**已批准** | 2025-01-14

## 上下文

小芽家教需要集成多个语音服务提供商（豆包、Azure、Google 等），当前硬编码的方式存在以下问题：

### 当前痛点
1. **厂商锁定**: 难以切换语音服务提供商
2. **代码重复**: 每个服务都要重新实现认证、重试、降级逻辑
3. **测试困难**: 无法 Mock 具体实现进行单元测试
4. **扩展性差**: 添加新服务需要修改业务代码
5. **可观测性不足**: 缺乏统一的监控和日志

### 业务需求
- 支持多个 ASR（语音转文字）和 TTS（文字转语音）提供商
- 自动降级和容错（主服务失败时切换备用服务）
- 统一的配置管理和错误处理
- 便于测试和开发环境 Mock

## 决策

采用**策略模式 + 工厂模式 + 依赖注入**的分层架构，设计生产级别的语音服务抽象层。

### 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                          │
│                   (FastAPI Routes / API)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    Application Layer                            │
│                    (VoiceServiceProxy)                          │
│  - 依赖注入 (Dependency Injection)                               │
│  - 自动降级 (Auto Fallback)                                      │
│  - 重试机制 (Retry with Tenacity)                                │
│  - 指标监控 (Metrics & Tracing)                                  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      Abstraction Layer                          │
│                     (VoiceService Protocol)                     │
│  - ASRInterface (Speech-to-Text)                                │
│  - TTSInterface (Text-to-Speech)                                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────────┐  ┌──────▼─────────┐  ┌───────▼──────────┐
│  Doubao Service  │  │ Azure Service  │  │  Google Service  │
│  (豆包)          │  │                │  │                  │
└──────────────────┘  └────────────────┘  └──────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                      │
│  - Config (Pydantic Settings)                               │
│  - HTTP Client (httpx.AsyncClient Pool)                     │
│  - Cache (Redis for TTS results)                            │
│  - Logging (loguru / structlog)                             │
│  - Metrics (Prometheus)                                     │
└─────────────────────────────────────────────────────────────┘
```

## 原因

### 1. 符合 SOLID 原则

#### 单一职责原则 (SRP)
- **ASRInterface** 只负责语音转文字
- **TTSInterface** 只负责文字转语音
- **VoiceServiceProxy** 只负责降级、重试、监控
- 每个具体实现只负责对接特定厂商 API

#### 开放封闭原则 (OCP)
- 添加新服务（如阿里云）只需实现接口，无需修改现有代码
- 通过工厂模式动态创建服务实例
- 策略模式允许运行时切换服务

#### 里氏替换原则 (LSP)
- 所有实现都可以无缝替换，不影响业务逻辑
- 接口契约确保行为一致性

#### 接口隔离原则 (ISP)
- ASR 和 TTS 分离，避免臃肿接口
- 客户端只依赖需要的接口

#### 依赖倒置原则 (DIP)
- 业务层依赖抽象（Protocol），不依赖具体实现
- 通过依赖注入（FastAPI Depends）解耦

### 2. 工程化最佳实践

#### 依赖注入
```python
# 使用 dependency-injector 或 FastAPI Depends
from fastapi import Depends

def get_voice_service(
    service: VoiceService = Depends(get_voice_service_from_config)
) -> VoiceService:
    return service
```

**优点**:
- 易于测试（可以注入 Mock 实现）
- 配置集中管理
- 生命周期管理（连接池复用）

#### 配置管理
```python
# 使用 Pydantic Settings
class VoiceServiceSettings(BaseSettings):
    asr_provider: str = "doubao"
    tts_provider: str = "doubao"
    fallback_providers: List[str] = ["azure", "google"]

    # 豆包配置
    doubao_api_key: str
    doubao_region: str = "cn-north-1"

    # Azure 配置
    azure_speech_key: str
    azure_speech_region: str = "eastasia"

    # 超时和重试
    timeout_seconds: int = 10
    max_retries: int = 3
    retry_backoff_factor: float = 1.5
```

**优点**:
- 类型安全
- 环境变量自动映射
- 开发/生产环境分离

#### 重试机制
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def transcribe_with_retry(audio_data: bytes) -> str:
    # ASR 调用逻辑
    pass
```

**优点**:
- 指数退避（避免雪崩）
- 自动重试临时失败
- 可配置重试次数

#### 连接池
```python
import httpx

async with httpx.AsyncClient() as client:
    # 连接复用
    response = await client.post(url, data=audio_data)
```

**优点**:
- 减少 TCP 握手开销
- 提升性能
- 支持 HTTP/2

#### 限流
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/voice/transcribe")
@limiter.limit("10/minute")
async def transcribe_audio(request: Request):
    # 限流保护
    pass
```

**优点**:
- 防止 API 滥用
- 控制成本
- 保护服务稳定性

### 3. 可观测性设计

#### 结构化日志
```python
from loguru import logger

logger.info(
    "ASR request completed",
    provider="doubao",
    duration_ms=123,
    audio_length_seconds=5.2,
    success=True
)
```

**优点**:
- 便于日志分析（ELK）
- 结构化查询
- 问题定位快速

#### 指标监控
```python
from prometheus_client import Counter, Histogram

asr_requests_total = Counter(
    'asr_requests_total',
    'Total ASR requests',
    ['provider', 'status']
)

asr_duration_seconds = Histogram(
    'asr_duration_seconds',
    'ASR request duration',
    ['provider']
)
```

**优点**:
- 实时监控（Grafana）
- 告警（Prometheus AlertManager）
- 性能分析

#### 分布式追踪
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("transcribe_audio") as span:
    span.set_attribute("provider", "doubao")
    # ASR 调用
```

**优点**:
- 跨服务追踪
- 性能瓶颈定位
- 依赖关系可视化

#### 健康检查
```python
@app.get("/health/voice")
async def health_check():
    services = await check_all_voice_services()
    return {
        "status": "healthy" if all(s["healthy"] for s in services) else "degraded",
        "services": services
    }
```

### 4. 测试策略

#### 单元测试（Mock）
```python
from unittest.mock import AsyncMock, patch

async def test_transcribe_with_mock():
    mock_service = AsyncMock()
    mock_service.transcribe.return_value = "测试文本"

    with patch('get_voice_service', return_value=mock_service):
        result = await transcribe_audio(b"fake_audio")
        assert result == "测试文本"
```

#### 契约测试（接口一致性）
```python
@pytest.mark.parametrize("service", [
    DoubaoASRService(),
    AzureASRService(),
])
async def test_asr_contract(service):
    audio_data = load_test_audio()
    text = await service.transcribe(audio_data)

    # 契约：所有实现必须返回非空字符串
    assert isinstance(text, str)
    assert len(text) > 0
```

#### 集成测试（真实 API）
```python
@pytest.mark.integration
async def test_doubao_real_api():
    service = DoubaoASRService(settings.doubao_api_key)
    audio_data = load_real_audio()

    text = await service.transcribe(audio_data)
    assert "测试" in text
```

### 5. 安全性设计

#### 密钥管理
```python
from azure.keyvault.secrets import SecretClient

# 从 Azure Key Vault 获取密钥
secret_client = SecretClient(
    vault_url="https://sprout-vault.vault.azure.net",
    credential=DefaultAzureCredential()
)
api_key = secret_client.get_secret("doubao-api-key").value
```

**优点**:
- 密钥不硬编码
- 自动轮换
- 审计日志

#### 加密传输
- 强制 HTTPS（TLS 1.3）
- 证书固定（Certificate Pinning）
- 请求签名（HMAC）

#### 审计日志
```python
audit_logger.info(
    "ASR API call",
    user_id=user.id,
    provider="doubao",
    audio_hash=sha256(audio_data),
    timestamp=datetime.now()
)
```

### 6. 性能优化

#### 缓存策略
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
async def get_tts_audio_cached(text: str, voice: str) -> bytes:
    # Redis 缓存 TTS 结果
    cache_key = f"tts:{hashlib.md5(text+voice).hexdigest()}"
    cached = await redis.get(cache_key)

    if cached:
        return cached

    audio = await tts_service.synthesize(text, voice)
    await redis.setex(cache_key, 3600, audio)  # 1小时
    return audio
```

**优点**:
- 减少 API 调用成本
- 降低延迟
- 提升用户体验

#### 批处理
```python
async def batch_transcribe(audio_list: List[bytes]) -> List[str]:
    # 批量处理多个音频
    tasks = [service.transcribe(audio) for audio in audio_list]
    return await asyncio.gather(*tasks)
```

#### CDN 分发
- TTS 音频文件上传到 CDN（阿里云 OSS / AWS S3）
- 返回 CDN URL 给前端
- 减少后端带宽压力

## 后果

### 正面影响
1. **可维护性**: 新增服务只需实现接口，无需修改业务代码
2. **可测试性**: 可以轻松 Mock 进行单元测试
3. **可观测性**: 统一的监控、日志、追踪
4. **可靠性**: 自动降级、重试、限流
5. **性能**: 连接池、缓存、批处理
6. **安全性**: 密钥管理、加密传输、审计日志

### 负面影响
1. **复杂度增加**: 初期架构设计需要投入更多时间
2. **学习曲线**: 团队需要熟悉策略模式、依赖注入等概念
3. **依赖增加**: 需要引入额外的库（dependency-injector、tenacity、loguru）
4. **抽象泄漏**: 某些服务特有功能可能无法通用化

### 风险
1. **过度设计**: 对于只有一个服务的情况可能过于复杂
   - **缓解**: 从简单接口开始，逐步演进
2. **性能开销**: 抽象层可能带来轻微性能损耗
   - **缓解**: 异步处理、连接池复用
3. **维护成本**: 需要维护多个服务的实现
   - **缓解**: 定期评估服务使用情况，移除不常用的实现

## 替代方案

### 方案 A: 硬编码（当前方案）
**为什么不用**:
- 厂商锁定，难以切换
- 代码重复，违反 DRY 原则
- 无法测试业务逻辑

### 方案 B: Facade 模式
**为什么不用**:
- Facade 模式适合简化复杂子系统，但我们的需求是**多策略切换**
- Facade 不支持运行时动态切换服务
- 不符合"开闭原则"

### 方案 C: 简单工厂
**为什么不用**:
- 简单工厂每次新增服务都要修改工厂类
- 不支持依赖注入
- 难以管理服务生命周期

### 方案 D: 微服务拆分
**为什么不用**:
- 当前规模不需要微服务
- 增加运维复杂度（服务发现、网络延迟）
- 团队规模小，不适合

## 技术选型

### 依赖库
| 库名 | 用途 | 版本 |
|------|------|------|
| `pydantic-settings` | 配置管理 | 2.1.0 |
| `httpx` | HTTP 客户端 | 0.26.0 |
| `tenacity` | 重试机制 | 8.2.3 |
| `dependency-injector` | 依赖注入 | 4.41.0 |
| `loguru` | 结构化日志 | 0.7.2 |
| `prometheus-client` | 指标监控 | 0.19.0 |
| `opentelemetry-api` | 分布式追踪 | 1.22.0 |

### 为什么选这些库？
- **httpx**: 异步 HTTP 客户端，支持 HTTP/2，连接池
- **tenacity**: 灵活的重试策略，指数退避
- **dependency-injector**: Python 最流行的 DI 框架
- **loguru**: 简单易用的日志库，内置轮转
- **prometheus-client**: 官方 Prometheus 客户端
- **opentelemetry**: 业界标准的分布式追踪

## 实施计划

### Phase 1: 接口设计（1 天）
- 定义 `ASRInterface` 和 `TTSInterface` Protocol
- 定义数据模型（`AudioRequest`, `TranscriptionResult`）
- 编写契约测试

### Phase 2: 基础设施（2 天）
- 配置管理（`VoiceServiceSettings`）
- HTTP 客户端池（`httpx.AsyncClient`）
- 日志、指标、追踪集成

### Phase 3: 服务实现（3 天）
- 豆包实现（`DoubaoASRService`, `DoubaoTTSService`）
- Azure 实现（`AzureASRService`, `AzureTTSService`）
- 工厂类（`VoiceServiceFactory`）

### Phase 4: 高级特性（2 天）
- 降级装饰器（`with_fallback`）
- 缓存装饰器（Redis）
- 重试装饰器（Tenacity）

### Phase 5: API 集成（1 天）
- FastAPI 路由
- 前端 TypeScript 类型定义
- API 文档（OpenAPI）

### Phase 6: 测试与优化（2 天）
- 单元测试
- 集成测试
- 性能基准测试
- 文档完善

**总计**: 11 天（2 周）

## 完成标准

- [ ] 所有服务实现通过契约测试
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试通过（至少 2 个服务）
- [ ] 性能基准测试完成（QPS、延迟、成本）
- [ ] 文档完整（架构图、API 文档、迁移指南）
- [ ] 健康检查端点正常
- [ ] 监控指标正常上报
- [ ] 安全审查通过（密钥管理、审计日志）

## 参考资料

- [FastAPI 依赖注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Python Protocol vs ABC](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [策略模式 - Refactoring Guru](https://refactoring.guru/design-patterns/strategy)
- [AWS SDK 设计模式](https://aws.amazon.com/blogs/architecture/)
- [Google Cloud API 设计指南](https://cloud.google.com/apis/design)
- [Tenacity 重试库](https://tenacity.readthedocs.io/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Prometheus 最佳实践](https://prometheus.io/docs/practices/naming/)

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| 1.0.0 | 2025-01-14 | Principal Architect | 初始版本 |

---

**审批人**: Principal Architect
**生效日期**: 2025-01-14
