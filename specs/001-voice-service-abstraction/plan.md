t# Implementation Plan: 语音服务抽象层集成

**Branch**: `001-voice-service-abstraction` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-voice-service-abstraction/spec.md`

## Summary

本功能为小芽家教应用集成专业的语音服务能力，支持学生通过语音与 AI 教师进行自然交互。系统将采用**后端代理模式**集成豆包语音服务（Doubao ASR + TTS），并设计**抽象层接口**以支持未来扩展到其他语音服务提供商（如 Azure Speech Services、Google Cloud Speech-to-Text、阿里云智能语音等）。

**技术方法**：
- 使用策略模式（Strategy Pattern）实现语音服务抽象层
- 通过工厂模式（Factory Pattern）动态切换服务提供商
- 实现自动降级机制：豆包不可用时切换到 Web Speech API
- 后端 API 代理：保护 API 密钥，实现认证和限流

---

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.2+ (Frontend)

**Primary Dependencies**:
- **Backend**: FastAPI 0.104+, httpx 0.25+, Pydantic v2, Python 3.11+
- **Frontend**: React 18.2+, Axios 1.6+, HTML5 Audio API, Web Speech API
- **Voice Services**: Doubao (豆包) bytedance, Web Speech API (降级)

**Storage**:
- **配置**: 环境变量（.env）
- **API Keys**: 加密存储在后端（不暴露给前端）
- **临时文件**: 音频文件临时存储（处理完成后立即删除）
- **缓存**: 可选 Redis 缓存 TTS 常用结果

**Testing**:
- **Backend**: pytest 7.0+, pytest-asyncio, pytest-cov (覆盖率 ≥80%)
- **Frontend**: Vitest / React Testing Library
- **集成测试**: 真实 API 调用（测试环境）

**Target Platform**:
- **Backend**: Linux server (Docker container)
- **Frontend**: Modern browsers (Chrome 90+, Safari 14+, Firefox 88+)

**Project Type**: web (backend + frontend)

**Performance Goals**:
- ASR 响应时间（p95）: ≤ 3 秒
- TTS 响应时间（p95）: ≤ 1 秒
- 并发支持: ≥ 10 个并发语音请求
- 服务降级触发频率: < 5%

**Constraints**:
- API Key 不得暴露给前端
- 原始音频文件不得长期存储
- 必须支持 HTTPS 加密传输
- 必须符合儿童隐私保护法规
- 不得依赖单一供应商（需支持切换）

**Scale/Scope**:
- 初期: 100 个并发学生
- 预计日均调用量: 1000 次 ASR + 500 次 TTS
- 月度预算: ¥1000
- 目标用户: 一年级学生（6-8 岁）

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**参考项目宪章**：[.specify/memory/constitution.md](../../.specify/memory/constitution.md)

### 核心价值观检查

- [x] **规范先于代码**：✅ 已创建规范文档 ([spec.md](./spec.md))
- [x] **质量不可妥协**：✅ 测试覆盖率目标 ≥ 80%（Backend pytest + Frontend Vitest）
- [x] **用户价值至上**：✅ 优先考虑一年级学生认知能力（语音交互降低输入门槛）
- [x] **透明可追溯**：✅ 可追溯到规范（001-voice-service-abstraction/spec.md）和 Task ID（待创建）

### 不可违反的原则检查

- [x] **P1: 规范完整性**：✅ 规范包含所有必需章节（Overview, User Scenarios, Requirements, Success Criteria）
- [x] **P2: TDD 强制执行**：✅ 将遵循 Red-Green-Refactor 循环（见后续 tasks.md）
- [x] **P3: 安全优先**：✅ 已考虑安全要求（API Key 加密、HTTPS 传输、儿童数据保护）
- [x] **P4: 性能合约**：✅ API 响应时间已明确（ASR ≤3s, TTS ≤1s, p95）
- [x] **P5: 向后兼容**：✅ 无破坏性变更（新增功能，不影响现有 API）
- [x] **P6: 代码一致性**：✅ 实施计划与规范一致（ASR/TTS、抽象层、降级方案）

**Constitution Check Result**: ✅ **PASSED** - 可以继续 Phase 0 研究

---

## Project Structure

### Documentation (this feature)

```text
specs/001-voice-service-abstraction/
├── spec.md              # 功能规范（已完成）
├── plan.md              # 实施计划（本文档）
├── research.md          # Phase 0 输出（技术研究）
├── data-model.md        # Phase 1 输出（数据模型）
├── quickstart.md        # Phase 1 输出（快速开始）
├── contracts/           # Phase 1 输出（API 契约）
│   ├── asr-api.yaml    # ASR API OpenAPI 规范
│   └── tts-api.yaml    # TTS API OpenAPI 规范
├── tasks.md             # Phase 2 输出（任务清单，由 /speckit.tasks 生成）
└── checklists/          # 质量检查清单
    └── requirements.md  # 规范质量验证（已完成）
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── voice.py           # 语音 API 端点（/api/v1/voice/asr, /api/v1/voice/tts）
│   ├── services/
│   │   ├── voice/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # VoiceService 抽象基类（Protocol）
│   │   │   ├── doubao.py           # DoubaoVoiceService 实现
│   │   │   ├── webspeech.py        # WebSpeechVoiceService 降级实现
│   │   │   └── factory.py          # VoiceServiceFactory 工厂类
│   │   └── engine.py               # AI 对话引擎（已存在）
│   ├── models/
│   │   └── voice.py                # 语音数据模型（ASRRequest, TTSRequest 等）
│   ├── core/
│   │   ├── config.py               # 配置管理（DOUBAO_API_KEY 等）
│   │   └── security.py             # API Key 加密存储
│   └── utils/
│       └── audio.py                # 音频处理工具（格式转换、压缩）
└── tests/
    ├── test_voice_service.py       # 抽象层单元测试
    ├── test_doubao_service.py      # 豆包服务集成测试
    ├── test_voice_api.py           # API 端点集成测试
    └── fixtures/
        └── audio_samples/           # 测试音频样本

frontend/
├── src/
│   ├── components/
│   │   ├── VoiceRecorder.tsx       # 录音组件（支持上传到后端）
│   │   └── AudioPlayer.tsx         # 播放组件（支持播放 TTS 音频）
│   ├── services/
│   │   └── voiceApi.ts             # 语音 API 客户端
│   └── hooks/
│       ├── useASR.ts                # ASR Hook（调用后端 ASR API）
│       └── useTTS.ts                # TTS Hook（调用后端 TTS API）
└── public/
    └── audio/                       # 静态音频资源（降级方案提示音）
```

**Structure Decision**: 选择 **Web application (Option 2)** 结构，因为：
1. 本项目是 Web 应用（backend + frontend）
2. 语音服务需要后端代理模式（保护 API Key）
3. 前端需要录音和播放组件
4. 符合现有项目结构（已存在 backend/ 和 frontend/ 目录）

---

## Complexity Tracking

> **无需填写** - Constitution Check 全部通过，无违规需要解释。

---

## Phase 0: Research & Technology Decisions

> **目标**: 解决技术上下文中的未知项，研究最佳实践和集成模式

### Research Tasks

1. **豆包语音服务 API 研究**
   - ASR API: 请求格式、响应格式、错误码
   - TTS API: 请求格式、音频返回方式、支持参数
   - 认证方式: x-api-key header
   - 限流策略: 并发数、QPS 限制

2. **语音服务抽象层设计模式研究**
   - 策略模式（Strategy Pattern）vs 工厂模式（Factory Pattern）
   - Python Protocol vs Abstract Base Class (ABC)
   - 依赖注入: dependency-injector 库 vs 手动注入
   - 参考项目: AWS SDK (boto3)、Azure SDK 抽象层设计

3. **音频处理最佳实践**
   - 音频格式转换: WAV ↔ MP3
   - 音频压缩: 减少上传时间
   - 流式处理: 是否支持流式 TTS
   - 临时文件管理: 自动清理机制

4. **降级策略研究**
   - Web Speech API 兼容性: Chrome/Safari/Firefox 支持度
   - 降级触发条件: 超时时间、错误码、连续失败次数
   - 自动恢复机制: 健康检查、回切到主服务

5. **安全与合规研究**
   - API Key 加密存储: Python cryptography、环境变量
   - 儿童隐私保护: COPPA 合规、数据不存储原则
   - HTTPS 强制: 中间人攻击防护

---

### Research Findings

**Decision 1: 使用 Python Protocol 定义抽象接口**

**Rationale**:
- Protocol 比 ABC 更灵活（鸭子类型）
- 不强制继承，支持运行时接口检查
- 更符合 Python 3.11+ 的现代实践
- 参考：TypedDict、Protocol 在现代项目中的广泛应用

**Alternatives Considered**:
- ABC (Abstract Base Class): 更严格，但不灵活
- Duck typing without Protocol: 无接口检查，容易出错

---

**Decision 2: 使用工厂模式创建服务实例**

**Rationale**:
- 支持配置化切换服务提供商
- 易于扩展新的服务适配器
- 符合开闭原则（对扩展开放，对修改封闭）

**Alternatives Considered**:
- 直接实例化: 不支持配置化切换
- 依赖注入容器: 过度工程，增加复杂度

---

**Decision 3: 使用 httpx.AsyncClient 作为 HTTP 客户端**

**Rationale**:
- 原生支持 async/await（符合 FastAPI 异步架构）
- 连接池自动管理
- 超时和重试机制完善
- 比 aiohttp 更现代和维护良好

**Alternatives Considered**:
- requests: 不支持 async
- aiohttp: 社区活跃度低于 httpx

---

**Decision 4: 降级策略 - 超时 5 秒触发降级**

**Rationale**:
- 平衡用户体验和服务稳定性
- 5 秒是学生可接受的等待时间上限
- 避免长时间等待无响应

**Alternatives Considered**:
- 3 秒降级: 过于激进，可能误判
- 10 秒降级: 过于保守，影响用户体验

---

**Decision 5: 不存储原始音频文件**

**Rationale**:
- 符合儿童隐私保护要求
- 降低存储成本
- 降低数据泄露风险

**Alternatives Considered**:
- 存储 7 天后删除: 仍需存储和清理机制
- 转录后立即删除: 符合隐私原则，但无法进行问题排查

**Trade-off**: 降级方案 - 仅存储元数据（请求日志），不存储音频内容

---

## Phase 1: Design & Contracts

> **目标**: 生成数据模型、API 契约和快速开始指南

### 1. Data Model (data-model.md)

**核心实体定义**:

```python
# 语音服务抽象接口
from typing import Protocol
from dataclasses import dataclass

class VoiceService(Protocol):
    """语音服务抽象接口"""

    async def speech_to_text(self, audio_data: bytes, format: str) -> str:
        """语音识别（ASR）"""
        ...

    async def text_to_speech(self, text: str) -> str:
        """语音合成（TTS），返回音频 URL"""
        ...

    async def health_check(self) -> bool:
        """健康检查"""
        ...

# ASR 请求
@dataclass
class ASRRequest:
    audio_url: str          # 音频文件 URL 或 base64
    format: str            # mp3, wav
    codec: str = "raw"     # raw, pcm
    rate: int = 16000      # 采样率
    bits: int = 16         # 位深
    channel: int = 1       # 声道数

# ASR 响应
@dataclass
class ASRResponse:
    text: str              # 识别文本
    confidence: float       # 置信度 0-1
    process_time: float    # 处理时间（秒）
    audio_duration: float  # 音频时长（秒）

# TTS 请求
@dataclass
class TTSRequest:
    text: str              # 待合成文本
    voice_type: str        # 音色
    encoding: str = "mp3"  # 音频编码
    speed_ratio: float = 1.0  # 语速
    volume_ratio: float = 1.0  # 音量
    pitch_ratio: float = 1.0   # 音调

# TTS 响应
@dataclass
class TTSResponse:
    audio_url: str         # 音频文件 URL
    duration: float        # 音频时长（秒）
    format: str            # 音频格式
    process_time: float    # 处理时间（秒）

# 服务提供商配置
@dataclass
class VoiceServiceProvider:
    name: str              # 提供商名称（doubao, webspeech）
    api_key: str | None    # API 密钥（可选，Web Speech 不需要）
    base_url: str          # API 基础 URL
    asr_model: str         # ASR 模型
    tts_voice: str         # TTS 音色
    timeout: int = 30     # 超时时间（秒）
    max_retries: int = 3   # 最大重试次数
    enabled: bool = True   # 是否启用
```

**关键设计决策**:
- 使用 Python dataclass 定义数据结构（类型安全、自动生成 `__init__`）
- 使用 Protocol 定义接口（灵活、现代）
- 不在模型中包含业务逻辑（关注点分离）

---

### 2. API Contracts (contracts/)

#### ASR API Contract (contracts/asr-api.yaml)

```yaml
openapi: 3.0.0
info:
  title: Voice ASR API
  version: 1.0.0
  description: 语音识别 API - 将音频转换为文本

paths:
  /api/v1/voice/asr:
    post:
      summary: 上传音频并获取识别文本
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required:
                - file
              properties:
                file:
                  type: string
                  format: binary
                  description: 音频文件（MP3 或 WAV）
                format:
                  type: string
                  enum: [mp3, wav]
                  description: 音频格式
      responses:
        '200':
          description: 识别成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  text:
                    type: string
                    description: 识别文本
                    example: "五加三等于多少？"
                  confidence:
                    type: number
                    format: float
                    description: 置信度（0-1）
                    example: 0.95
                  process_time:
                    type: number
                    format: float
                    description: 处理时间（秒）
                    example: 1.23
                  audio_duration:
                    type: number
                    format: float
                    description: 音频时长（秒）
                    example: 3.45
        '400':
          description: 请求错误（无效音频格式）
        '401':
          description: 未授权（API Key 无效）
        '500':
          description: 服务内部错误
        '503':
          description: 服务不可用（降级到 Web Speech API）
```

#### TTS API Contract (contracts/tts-api.yaml)

```yaml
openapi: 3.0.0
info:
  title: Voice TTS API
  version: 1.0.0
  description: 语音合成 API - 将文本转换为音频

paths:
  /api/v1/voice/tts:
    post:
      summary: 提交文本并获取合成音频
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - text
              properties:
                text:
                  type: string
                  description: 待合成文本
                  example: "很好！五加三等于八。"
                  maxLength: 500
                voice_type:
                  type: string
                  description: 音色
                  example: "zh_female_cancan_mars_bigtts"
                speed_ratio:
                  type: number
                  format: float
                  description: 语速（0.8-1.2）
                  example: 1.0
      responses:
        '200':
          description: 合成成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  audio_url:
                    type: string
                    description: 音频文件 URL
                    example: "https://cdn.example.com/audio/tts_123.mp3"
                  duration:
                    type: number
                    format: float
                    description: 音频时长（秒）
                    example: 4.56
                  format:
                    type: string
                    description: 音频格式
                    example: "mp3"
                  process_time:
                    type: number
                    format: float
                    description: 处理时间（秒）
                    example: 0.78
        '400':
          description: 请求错误（文本为空或超长）
        '500':
          description: 服务内部错误
        '503':
          description: 服务不可用（降级到 Web Speech API）
```

---

### 3. Quick Start Guide (quickstart.md)

#### 开发环境设置

1. **配置环境变量** (backend/.env)

```bash
# 豆包语音服务配置
DOUBAO_API_KEY=745daf50-75a9-4acc-9352-91a7c0482d8f
DOUBAO_BASE_URL=https://openspeech.bytedance.com/api/v3
DOUBAO_ASR_MODEL=bigmodel
DOUBAO_TTS_VOICE=zh_female_cancan_mars_bigtts
DOUBAO_TTS_RATE=1.0
DOUBAO_TTS_PITCH=1.0
DOUBAO_TTS_VOLUME=1.0
DOUBAO_TIMEOUT=30
DOUBAO_MAX_RETRIES=3

# 语音服务配置
VOICE_PRIMARY_PROVIDER=doubao
VOICE_FALLBACK_PROVIDER=webspeech
VOICE_ENABLE_FALLBACK=true

# 性能配置
VOICE_MAX_CONCURRENT_REQUESTS=10
VOICE_REQUEST_TIMEOUT=5
VOICE_CACHE_TTS_RESULTS=true
```

2. **安装依赖**

```bash
# Backend
cd backend
pip install httpx pydantic
pip install pytest pytest-asyncio pytest-cov

# Frontend（已存在，无需额外安装）
cd frontend
npm install axios
```

3. **运行后端服务**

```bash
cd backend
uvicorn app.main:app --reload
```

4. **运行前端服务**

```bash
cd frontend
npm start
```

#### 测试语音服务

1. **测试 ASR（语音识别）**

```bash
# 使用 curl 测试
curl -X POST "http://localhost:8000/api/v1/voice/asr" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_audio.mp3" \
  -F "format=mp3"
```

2. **测试 TTS（语音合成）**

```bash
curl -X POST "http://localhost:8000/api/v1/voice/tts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，我是小芽老师",
    "voice_type": "zh_female_cancan_mars_bigtts"
  }'
```

#### 前端集成示例

```typescript
// ASR 示例
import { useASR } from '../hooks/useASR';

function VoiceInput() {
  const { transcribe, isLoading, error } = useASR();

  const handleAudioRecorded = async (audioBlob: Blob) => {
    const text = await transcribe(audioBlob);
    console.log('识别文本:', text);
  };

  return <VoiceRecorder onRecordComplete={handleAudioRecorded} />;
}

// TTS 示例
import { useTTS } from '../hooks/useTTS';

function AIResponse({ text }) {
  const { synthesize, audioUrl, isLoading } = useTTS();

  useEffect(() => {
    synthesize(text);
  }, [text]);

  if (isLoading) return <div>合成中...</div>;
  if (audioUrl) return <audio src={audioUrl} autoPlay />;
  return null;
}
```

---

## Architecture Decision Records (ADRs)

### ADR-001: 后端代理模式 vs 前端直接调用

**Status**: Accepted

**Context**: 需要决定语音服务的调用方式

**Decision**: 采用后端代理模式，所有豆包 API 调用通过后端转发

**Rationale**:
- ✅ API Key 安全存储在后端，不暴露给前端
- ✅ 可实现统一的认证、限流和成本监控
- ✅ 便于记录调用日志和问题排查
- ✅ 支持降级策略（后端判断何时切换）

**Consequences**:
- 正面：提高安全性、可控性、可观测性
- 负面：增加后端复杂度和网络开销
- 缓解：音频压缩、CDN 加速

**Alternatives Rejected**:
- 前端直接调用：API Key 暴露在浏览器中（安全风险）

---

### ADR-002: 策略模式 vs 工厂模式

**Status**: Accepted

**Context**: 需要选择抽象层设计模式

**Decision**: 结合使用策略模式 + 工厂模式

**Rationale**:
- 策略模式（Strategy）: 定义 VoiceService 接口，每个服务独立实现
- 工厂模式（Factory）: 根据配置动态创建服务实例
- 两者结合：灵活切换、易于扩展

**Consequences**:
- 正面：支持配置化切换、符合开闭原则
- 负面：增加类和接口数量
- 缓解：清晰的文档和示例

**Alternatives Rejected**:
- 单一服务实现：无法切换供应商（供应商锁定）

---

### ADR-003: 降级策略设计

**Status**: Accepted

**Context**: 需要设计豆包服务不可用时的降级方案

**Decision**: 自动降级 + 自动恢复

**降级触发条件**:
- 请求超时 > 5 秒
- 连续失败 3 次
- 返回 5xx 错误

**恢复策略**:
- 每隔 1 分钟健康检查主服务
- 检查通过后自动切回主服务

**Consequences**:
- 正面：提高服务可用性
- 负面：降级期间识别率下降
- 缓解：明确提示用户"已切换到备用服务"

**Alternatives Rejected**:
- 手动切换：需要人工干预，响应慢
- 无降级：服务完全不可用

---

## Implementation Phases

### Phase 0: Research & Design ✅ (本文档)

**输出**:
- research.md（技术研究）
- data-model.md（数据模型）
- contracts/（API 契约）
- quickstart.md（快速开始）

### Phase 1: Backend Development (待 /speckit.tasks 生成)

**任务**:
1. 创建语音服务抽象接口
2. 实现豆包语音服务适配器
3. 实现 Web Speech API 降级适配器
4. 创建工厂类和配置管理
5. 实现 API 端点（/api/v1/voice/asr, /api/v1/voice/tts）
6. 编写单元测试和集成测试

### Phase 2: Frontend Development (待 /speckit.tasks 生成)

**任务**:
1. 创建 VoiceRecorder 组件
2. 创建 AudioPlayer 组件
3. 实现 useASR Hook
4. 实现 useTTS Hook
5. 集成到对话界面
6. 编写组件测试

### Phase 3: Integration & Testing (待 /speckit.tasks 生成)

**任务**:
1. 端到端测试（录音 → ASR → AI → TTS → 播放）
2. 性能测试（并发、响应时间）
3. 降级测试（阻断豆包服务）
4. 安全测试（API Key 不泄露）
5. 成本监控（调用次数统计）

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| 豆包服务不稳定 | 高 | 中 | 自动降级到 Web Speech API |
| API Key 泄露 | 高 | 低 | 加密存储、环境变量、定期轮换 |
| 成本超预算 | 中 | 中 | 限流、缓存、监控告警 |
| 降级识别率低 | 中 | 低 | 明确提示用户、优化录音质量 |
| 音频上传慢 | 中 | 中 | 音频压缩、CDN 加速 |
| 隐私合规问题 | 高 | 低 | 不存储原始音频、HTTPS 加密 |

---

## Success Criteria Validation

根据 spec.md 中的成功标准：

| SC | Metric | Target | Validation Method |
|----|--------|--------|-------------------|
| SC-001 | ASR 准确率 | ≥95% (标准), ≥90% (儿童) | 集成测试 100 个音频样本 |
| SC-002 | ASR 响应时间 | ≤3s (p95) | 性能测试（1000 并发请求） |
| SC-003 | TTS 响应时间 | ≤1s (p95) | 性能测试（1000 并发请求） |
| SC-004 | 并发支持 | ≥10 | 性能测试（压测工具） |
| SC-005 | 降级触发频率 | <5% | 监控日志统计 |
| SC-006 | 服务切换成功率 | 100% | 故障注入测试 |
| SC-007 | API Key 泄露事件 | 0 | 安全审计、代码审查 |
| SC-008 | 首次使用成功率 | ≥90% | 用户测试（10 个一年级学生） |
| SC-009 | 任务完成率提升 | ≥20% | A/B 测试（语音 vs 文本） |
| SC-010 | 系统可用性 | ≥99.5% | 监控统计（30 天） |

---

## Next Steps

1. ✅ **Phase 0 完成**：本文档（plan.md）已创建
2. ⏭️ **Phase 1 等待**：`/speckit.tasks` 将生成 tasks.md
3. ⏭️ **Phase 2 准备**：创建 Taskmaster 任务并开始实施

**命令建议**:
```bash
# 生成任务清单
/speckit.tasks

# 创建 Taskmaster 任务（待 tasks.md 生成后）
tm add-task --title="实现语音服务抽象层" --priority=P1
```

---

**Plan Status**: Draft - Ready for Task Generation
**Last Updated**: 2026-01-14
**Reviewed By**: Claude (Architect Agent)
**Next Review**: After tasks.md generated
