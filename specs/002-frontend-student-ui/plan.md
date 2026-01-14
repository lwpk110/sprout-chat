# Implementation Plan: 小芽家教前端学生界面

**Branch**: `002-frontend-student-ui` | **Date**: 2025-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/luwei/workspace/github/sprout-chat/specs/002-frontend-student-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

实现小芽家教前端 React 应用，为一年级学生提供语音对话和拍照上传作业的 AI 学习界面。核心功能包括：

1. **语音对话学习** (P1): 通过 Web Speech API 实现语音输入，后端 AI 提供引导式教学响应
2. **拍照上传作业** (P2): 调用设备摄像头拍照，上传至后端 OCR 识别并获得辅导
3. **学习进度可视化** (P3): 展示学习记录、知识点掌握、成就徽章等

**技术方法**: 使用 React 18 + TypeScript + Vite，组件化设计，适龄界面（大按钮、大字体、高对比度），与后端 REST API 对接。

## Technical Context

**Language/Version**: TypeScript 5.2 + React 18.2
**Primary Dependencies**:
- **UI**: React 18, React Router 6, Tailwind CSS 3
- **状态管理**: Zustand 4
- **HTTP 客户端**: Axios 1.6
- **构建工具**: Vite 5
- **测试**: Jest 29 + Testing Library

**Storage**:
- **本地**: localStorage (会话缓存、离线数据)
- **云端**: 后端数据库 (通过 API 访问)

**Testing**: Jest + React Testing Library
- 单元测试覆盖率目标: ≥ 80%
- 集成测试覆盖关键用户流程

**Target Platform**:
- **浏览器**: Chrome 90+, Safari 14+, Edge 90+ (支持 Web Speech API)
- **设备**: 平板/手机 (触屏优先)
- **响应式**: 移动优先设计

**Project Type**: Web frontend (React SPA)

**Performance Goals**:
- 首屏加载时间: ≤ 2 秒
- 语音录制启动延迟: ≤ 500ms
- 界面响应时间: ≤ 200ms
- 图片上传完成时间: ≤ 5 秒 (图片 < 5MB)

**Constraints**:
- 必须兼容 Web Speech API (fallback 到文本输入)
- 必须处理弱网环境 (离线缓存、重试机制)
- 必须符合儿童隐私保护要求 (COPPA)
- 必须支持大字体、大按钮 (适龄设计)

**Scale/Scope**:
- 预计 20-25 React 组件
- 5-6 个自定义 Hooks
- 3 个主要页面 (主页、进度页、设置页)
- 预计 3000-4000 行代码

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**参考项目宪章**：[.specify/memory/constitution.md](../../.specify/memory/constitution.md)

### 核心价值观检查

- [x] **规范先于代码**：✅ 规范文档已存在 ([spec.md](./spec.md))
- [x] **质量不可妥协**：✅ 测试覆盖率目标 ≥ 80%，使用 Jest + Testing Library
- [x] **用户价值至上**：✅ 优先考虑一年级学生的认知能力（大按钮、大字体、语音交互）
- [x] **透明可追溯**：✅ 可追溯到 PRD ([docs/PRD.md](../../docs/PRD.md)) 和未来 Task ID

### 不可违反的原则检查

- [x] **P1: 规范完整性**：✅ 规范包含所有必需章节（用户故事、功能需求、成功标准等）
- [x] **P2: TDD 强制执行**：✅ 将遵循 Red-Green-Refactor 循环（详见 Phase 2 任务分解）
- [x] **P3: 安全优先**：✅ 考虑了安全要求（儿童数据保护、麦克风/摄像头权限、本地数据加密）
- [x] **P4: 性能合约**：✅ 明确了性能要求（语音 ≤ 4秒、拍照 ≤ 6秒、界面响应 ≤ 200ms）
- [x] **P5: 向后兼容**：✅ 无破坏性变更，新增功能独立模块化
- [x] **P6: 代码一致性**：✅ 实施计划与规范一致（API 对接 001-learning-management）

**Constitution Check 结果**: ✅ **全部通过**

## Project Structure

### Documentation (this feature)

```text
specs/002-frontend-student-ui/
├── spec.md              # 功能规范 ✅
├── plan.md              # 本文件 (技术实施计划)
├── research.md          # Phase 0: 技术研究
├── data-model.md        # Phase 1: 数据模型
├── quickstart.md        # Phase 1: 快速开始指南
├── contracts/           # Phase 1: API 契约
│   ├── conversations-api.yaml    # 对话 API 契约
│   └── images-api.yaml           # 图片上传 API 契约
└── tasks.md             # Phase 2: 任务清单 (/speckit.tasks 生成)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/           # React 组件
│   │   ├── VoiceInteraction.tsx       # 语音交互组件 ✅
│   │   ├── PhotoInteraction.tsx       # 拍照交互组件 ✅
│   │   ├── TextInteraction.tsx        # 文字交互组件 ✅
│   │   ├── GuidedResponse.tsx         # 引导响应组件 ✅
│   │   ├── ProgressBar.tsx            # 学习进度条 ⏳
│   │   ├── AchievementBadge.tsx       # 成就徽章 ⏳
│   │   ├── MistakeCard.tsx            # 错题卡片 ⏳
│   │   └── __tests__/                 # 组件单元测试
│   ├── pages/                # 页面组件
│   │   ├── StudentHome.tsx            # 学生主页 ✅
│   │   ├── ProgressPage.tsx           # 进度页面 ⏳
│   │   └── SettingsPage.tsx           # 设置页面 ⏳
│   ├── hooks/                # 自定义 Hooks
│   │   ├── useVoiceRecognition.ts     # Web Speech API 封装 ⏳
│   │   ├── useCamera.ts               # 摄像头访问封装 ⏳
│   │   ├── useOfflineSync.ts          # 离线数据同步 ⏳
│   │   └── useLocalStorage.ts         # localStorage 持久化 ⏳
│   ├── services/             # API 服务
│   │   └── api.ts                     # API 客户端 ✅
│   ├── store/                # 状态管理
│   │   └── sessionStore.ts            # 会话状态 (Zustand) ✅
│   ├── types/                # TypeScript 类型
│   │   └── index.ts                  # 类型定义 ✅
│   ├── utils/                # 工具函数
│   │   ├── audio.ts                   # 音频处理 ⏳
│   │   ├── image.ts                   # 图片压缩 ⏳
│   │   └── format.ts                  # 格式化工具 ⏳
│   ├── App.tsx               # 应用根组件 ✅
│   └── main.tsx              # 入口文件 ✅
├── public/                   # 静态资源
│   ├── icons/                # 图标资源
│   └── sounds/               # 音效文件
├── tests/                    # 集成测试
│   ├── integration/          # 集成测试用例
│   └── __mocks__/            # Mock 数据
├── package.json              # 依赖配置 ✅
├── vite.config.ts            # Vite 配置 ✅
├── tailwind.config.js        # Tailwind 配置 ✅
├── jest.config.cjs           # Jest 配置 ✅
└── tsconfig.json             # TypeScript 配置 ✅

backend/                      # 后端 API (已实现)
└── app/api/                  # REST API 端点
    ├── /v1/conversations/*   # 对话 API
    └── /v1/images/*          # OCR API
```

**Structure Decision**:
- **Web application (frontend + backend)**: 前端为 React SPA，后端为 FastAPI
- **现有代码**: 基础组件已实现 (VoiceInteraction, PhotoInteraction, TextInteraction)
- **待补充**: 学习进度可视化、离线缓存、错误处理增强、测试覆盖

## Complexity Tracking

> **无需填写** - Constitution Check 全部通过，无违规需论证。

---

## Phase 0: Research & Technology Decisions

### 待研究的未知项

1. **Web Speech API 兼容性**
   - 需要确认: Safari 14+ 的完整支持程度
   - Fallback 方案: 文本输入 + 语音提示

2. **图片压缩方案**
   - 需要确认: 前端压缩最佳实践 (browser-image-compression vs canvas)
   - 性能目标: 压缩至 < 1MB，耗时 < 2 秒

3. **离线存储策略**
   - 需要确认: localStorage vs IndexedDB (存储容量、API 复杂度)
   - 数据量: 预计 < 5MB (文本 + 图片缓存)

4. **适龄设计指南**
   - 需要确认: 一年级学生 UI/UX 最佳实践
   - 参考: Apple Human Interface Guidelines (Kids category)

5. **Web Speech API 持续录音**
   - 需要确认: 如何实现"3秒无声音自动结束"的检测逻辑
   - 技术方案: AudioContext 分析音量阈值

### Phase 0 输出文件

- **research.md**: 技术调研报告，包含上述问题的决策和备选方案

---

## Phase 1: Design & Contracts

### 1.1 数据模型设计 (data-model.md)

定义前端状态管理的数据模型：
- **SessionState**: 会话状态 (sessionStore.ts 扩展)
- **Message**: 对话消息实体
- **LearningProgress**: 学习进度实体
- **Achievement**: 成就徽章实体
- **Mistake**: 错题记录实体

### 1.2 API 契约定义 (contracts/)

基于 001-learning-management 后端 API 规范，定义前端对接契约：
- **conversations-api.yaml**: 对话 API OpenAPI 规范
- **images-api.yaml**: 图片上传 API OpenAPI 规范

### 1.3 快速开始指南 (quickstart.md)

为新开发者提供：
- 环境搭建步骤
- 本地开发命令
- 测试运行指南
- 代码结构说明

### 1.4 Agent Context 更新

运行 `.specify/scripts/bash/update-agent-context.sh` 更新 Claude 的上下文文件，添加前端技术栈信息。

---

## Phase 2: Task Generation (由 /speckit.tasks 执行)

Phase 1 完成后，使用 `/speckit.tasks` 生成任务清单，任务将按以下方式组织：

### User Story 1 - 语音对话学习 (P1)
- [ ] 实现 Web Speech API Hook (useVoiceRecognition)
- [ ] 增强 VoiceInteraction 组件 (错误处理、重试机制)
- [ ] 添加语音播报功能 (TTS)
- [ ] 编写语音交互集成测试

### User Story 2 - 拍照上传作业 (P2)
- [ ] 实现摄像头访问 Hook (useCamera)
- [ ] 实现图片压缩工具 (image.ts)
- [ ] 增强 PhotoInteraction 组件 (模糊检测、进度显示)
- [ ] 编写拍照上传集成测试

### User Story 3 - 学习进度可视化 (P3)
- [ ] 创建 ProgressPage 组件
- [ ] 实现 ProgressBar 组件
- [ ] 实现 AchievementBadge 组件
- [ ] 实现 MistakeCard 组件
- [ ] 对接学习记录 API
- [ ] 编写进度页面测试

### 通用任务
- [ ] 实现离线缓存机制 (useOfflineSync)
- [ ] 增强错误处理和用户提示
- [ ] 添加适龄设计优化 (大按钮、大字体验证)
- [ ] 性能优化 (代码分割、懒加载)
- [ ] 安全审计 (麦克风/摄像头权限、数据加密)
- [ ] 端到端测试 (关键用户流程)

---

## 完成标准

Phase 1 (plan.md 完成标志):
- [x] Constitution Check 全部通过
- [ ] research.md 完成 (所有 NEEDS CLARIFICATION 已解决)
- [ ] data-model.md 完成 (实体定义、关系、验证规则)
- [ ] contracts/*.yaml 完成 (API 契约、OpenAPI 规范)
- [ ] quickstart.md 完成 (环境搭建、开发指南)
- [ ] Agent context 已更新

Phase 2 (tasks.md 完成标志):
- [ ] tasks.md 生成 (由 /speckit.tasks 执行)
- [ ] 所有任务按用户故事组织
- [ ] 任务依赖关系明确
- [ ] 任务包含测试要求

Phase 3 (实施完成标志):
- [ ] 所有功能实现完成
- [ ] 测试覆盖率 ≥ 80%
- [ ] 所有性能指标达标
- [ ] 代码审查通过
- [ ] 用户测试通过 (一年级学生可独立完成核心操作)
