# 小芽家教 (SproutChat) - 项目记忆中枢

## 项目概述
小芽家教是面向一年级学生的 AI-First 个性化家教助手，通过语音拍照交互和引导式教学，帮助学生在快乐中学习成长。

## 技术栈

### 后端技术栈
- **框架**: Python FastAPI
- **AI 集成**: Claude API
- **语音处理**: Web Speech API + 云端 ASR
- **图像识别**: OCR (待确定具体方案)
- **数据库**: SQLite (初期) / PostgreSQL (后期)
- **缓存**: Redis (可选)

### 前端技术栈
- **框架**: React 18
- **样式**: Tailwind CSS
- **状态管理**: React Context / Zustand
- **路由**: React Router
- **HTTP 客户端**: Axios
- **UI 组件**: Headless UI (可选)

## 开发方法论

本项目采用 **规范驱动开发（SDD）** 方法论，结合任务管理和迭代开发。

### 项目宪章 ⚖️ **最高优先级**

**所有功能开发必须遵循项目宪章**

#### 核心原则
- **规范先于代码**: 没有规范不写代码
- **质量不可妥协**: 测试覆盖率 ≥ 80%，所有测试必须通过
- **用户价值至上**: 一年级学生认知能力优先
- **透明可追溯**: 所有决策和变更有据可查

#### 工作流程
```
需求分析 → 编写规范 → 规范审查 → 规范批准 → 创建实施计划 → 生成任务清单 → 执行实施（Ralph Loop） → 验证合规 → 标记完成
```

#### 项目宪章必读
- ⚖️ **[项目宪章](./.specify/memory/constitution.md)** - 4 条核心价值观，6 条不可违反的原则
- 📖 本文档下方有详细的工作流程说明

#### 快速开始
```bash
# 1. 编写新规范（使用 Spec-Kit 命令）
/speckit.specify "功能描述"

# 2. 分析规范完整性
/speckit.analyze

# 3. 创建实施计划
/speckit.plan

# 4. 生成任务清单
/speckit.tasks

# 5. 启动 Ralph Loop 实施
/ralph-loop "按规范实现功能"
```

---

### 1. Ralph Loop 迭代开发

本项目使用 **Ralph Loop** 插件进行迭代开发，这是基于 Ralph Wiggum 技术的 AI 原生开发方法。

#### 核心概念
- **迭代改进**: 通过重复执行相同任务提示词，持续改进代码
- **自引用**: Claude 通过文件和 git 历史看到自己的工作，进行迭代优化
- **确定性失败**: 可预测的问题使得系统性改进成为可能
- **规范驱动**: 每次迭代都遵循 Spec-Kit 规范

#### 使用方法
1. **编写规范**: 使用 `/speckit.specify "功能描述"` 生成规范
2. **规范审查**: 确保规范符合项目宪章要求
3. **启动循环**: `/ralph-loop "按规范实现功能"`
4. **迭代开发**: Claude 接收提示词，阅读规范，持续改进
5. **验证规范**: 确保代码符合规范要求
6. **完成信号**: 输出 `<promise>完成描述</promise>` 标签
7. **停止循环**: `/cancel-ralph`

#### 当前迭代提示词
详细的迭代任务请查看项目根目录的 `PROMPT.md`

#### Ralph Loop 指南
快速开始和最佳实践请查看 `RALPH_LOOP_GUIDE.md`

#### 与规范驱动开发的集成
- Ralph Loop 每次迭代开始时读取对应规范文档（使用 Spec-Kit 生成）
- 实施过程遵循规范中的 API 定义、数据模型、业务逻辑
- 完成后验证是否符合规范的完成标准
- 遵循项目宪章的所有原则

---

### 2. Task-Master 任务管理

Task-Master 负责任务的进度追踪和资源管理，与规范驱动开发互补。

#### 功能边界
| 维度 | Task-Master | 规范驱动开发 |
|------|-------------|----------|
| **职责** | 管理任务和进度 | 定义规范和标准 |
| **关注点** | 什么时候做 | 怎么做 |
| **核心问题** | What & When | How |
| **时间维度** | ✅ 优先级、排期 | ❌ |
| **技术维度** | ❌ | ✅ API、数据模型、测试 |

#### 使用规范
详见本文件"开发约定"部分的"1. Taskmaster 强制规范"

#### 与规范驱动开发的协作
```
规范批准
   ↓
创建任务引用规范 (Task-Master)
   ↓
按规范实施 (Ralph Loop)
   ↓
验证符合规范
   ↓
标记任务完成 (Task-Master)
```

---

### 三支柱协同示例

**场景：实现学习记录 API**

```bash
# 第 1 步：编写规范（使用 Spec-Kit）
/speckit.specify "实现学习记录 API，包括创建记录、查询进度、查询历史"
# 填写：用户故事、功能需求、成功标准

# 第 2 步：分析规范
/speckit.analyze
# ✅ 验证通过

# 第 3 步：创建实施计划
/speckit.plan

# 第 4 步：生成任务清单
/speckit.tasks

# 第 5 步：启动任务（Task-Master）
tm set-status --id=LWP-2.2.1 --status=in-progress

# 第 6 步：启动 Ralph Loop 实施
/ralph-loop "按规范实现学习记录 API"
# Ralph Loop 会：
# - 阅读规范文档
# - 按规范实现 API（TDD）
# - 验证符合规范

# 第 7 步：标记完成
tm set-status --id=LWP-2.2.1 --status=done
```

---

### 开发方法论文档

| 文档 | 用途 | 优先级 |
|------|------|--------|
| [项目宪章](./.specify/memory/constitution.md) | 最高原则，必须遵守 | ⚖️ P0 |
| [Ralph Loop 指南](./RALPH_LOOP_GUIDE.md) | 迭代开发快速开始 | 🔄 P1 |
| [Ralph Loop 配置](./RALPH_LOOP_SETUP.md) | 配置说明 | 🔧 P2 |
| [开发协议](./docs/development-guide.md) | TDD 自动化流程 | 🚦 P0 |

## 代码风格规范

### AI 原生开发原则
1. **模块化设计**: 每个功能模块独立，便于 AI 生成和维护
2. **命名规范**:
   - 组件: PascalCase (e.g., `SproutButton`)
   - 函数/变量: camelCase (e.g., `handleAudioInput`)
   - 常量: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
3. **文件组织**: 按功能模块划分，保持扁平化结构
4. **注释规范**: 关键逻辑必须注释，使用 JSDoc 格式

### 项目结构
```
sprout-chat/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   └── tests/              # 后端测试
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── hooks/          # 自定义 Hooks
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API 服务
│   │   └── utils/          # 工具函数
│   └── public/             # 静态资源
└── docs/                   # 项目文档
```

## 开发约定

### 0. 强制 TDD 流程 ⚠️ **必须遵守**

**所有 Feature 开发必须遵循【红灯 -> 绿灯】循环**

```bash
# TDD 循环流程
1. Red (红灯): 先写 tests/ 下的失败测试
2. Commit: 提交测试代码 (git commit -m "[LWP-X] test: 添加 XXX 测试")
3. Green (绿灯): 编写功能代码让测试通过
4. Commit: 提交功能代码 (git commit -m "[LWP-X] feat: 实现 XXX 功能")
5. Refactor (可选): 重构代码，保持测试通过
6. Commit: 提交重构代码 (git commit -m "[LWP-X] refactor: 优化 XXX 代码")
```

**禁止行为**:
- ❌ 先写功能代码，再补测试
- ❌ 一次性提交测试+功能代码
- ❌ 跳过测试直接编写功能

**验证标准**:
- 第一个 commit 运行测试必须失败 (Red)
- 第二个 commit 运行测试必须通过 (Green)
- 所有提交必须可以独立运行 pytest

### 1. Taskmaster 强制规范 ⚠️ **必须遵守**

#### 1.1 任务先行原则
**任何代码修改前，必须先在 Taskmaster 中确认对应任务 ID 处于 in-progress 状态**

```bash
# 开始任务前必须执行
task-master set-status --id=LWP-2 --status=in-progress

# 或者使用 MCP
mcp__task-master-ai__set_task_status {"id": "LWP-2", "status": "in-progress"}
```

**验证流程**:
1. 查看 Taskmaster 任务列表：`task-master list`
2. 确认任务状态为 `in-progress`
3. 记录任务 ID（如 LWP-2）
4. 开始编码

#### 1.2 自动状态更新
**代码完成并通过测试后，必须立即调用 Taskmaster 更新任务状态并标记为 done**

```bash
# 完成任务后必须执行
task-master set-status --id=LWP-2 --status=done

# 或者使用 MCP
mcp__task-master-ai__set_task_status {"id": "LWP-2", "status": "done"}
```

**完成标准**:
- 代码实现完成
- 单元测试通过（覆盖率 >80%）
- 功能测试验证
- 代码审查通过
- 文档已更新

#### 1.3 Git Commit 与任务关联
**在 Git Commit 信息中，必须附带对应的 Task ID**

```bash
# 推荐格式
git commit -m "[LWP-2] 实现 OCR 图像识别服务

- 集成 PaddleOCR
- 创建 /api/v1/ocr/upload 端点
- 添加图像预处理流程

Refs: LWP-2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Commit Message 格式**:
```
[Task-ID] 简短描述

详细说明：
- 完成项 1
- 完成项 2

Refs: Task-ID

Co-Authored-By: ... (如果有)
```

### 2. 提交规范
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关

### 3. 分支策略
- main: 生产环境分支
- develop: 开发环境分支
- feature/*: 功能开发分支
- hotfix/*: 紧急修复分支

### 4. 代码审查
- 所有代码必须经过 PR 审查
- 自动化测试必须通过
- 代码覆盖率不低于 80%

### 5. Git 版本控制规范 ⚠️ **必须遵守**

#### 5.1 原子提交原则 (Atomic Commits)
**每次提交仅包含一个逻辑变更，禁止批量提交**

```bash
# 正确的做法: 每个功能点独立提交
git add backend/app/api/conversations.py
git commit -m "[LWP-1] 实现会话创建 API"

git add backend/app/services/engine.py
git commit -m "[LWP-1] 实现对话引擎核心逻辑"

git add tests/test_engine.py
git commit -m "[LWP-1] 添加单元测试"

# 错误的做法: 一次性提交所有修改
git add .
git commit -m "LWP-1 完成"  # ❌ 违反原子提交原则
```

#### 5.2 提交信息格式 (Commit Message Format)
**所有提交必须遵循以下格式**

```bash
# 格式
<TYPE>(Task-ID): <简短描述>

# 详细说明（可选）
# - 完成项 1
# - 完成项 2

# Refs: Task-ID

# Co-Authored-By: ... (如果有)
```

**TYPE 类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**:
```bash
# 新功能
git commit -m "[LWP-2] 实现 OCR 图像识别服务

- 集成 PaddleOCR
- 创建 /api/v1/ocr/upload 端点
- 添加图像预处理流程

Refs: LWP-2"

# Bug 修复
git commit -m "[LWP-1] 修复会话过期时间计算错误"

# 文档更新
git commit -m "[LWP-1] 更新 API 文档"
```

#### 5.3 提交前检查 (Pre-commit Checks)
**每次提交前必须执行的检查**

```bash
# 1. 语法检查
python -m py_compile backend/app/**/*.py

# 2. 代码格式化
black backend/app --check
isort backend/app --check

# 3. 测试验证
pytest backend/tests/ -v

# 4. 查看 Git 状态
git status
```

#### 5.4 强制执行规范 (Forced Execution)
**除非用户明确要求，否则在完成 Taskmaster 的每个子步骤后，请主动执行提交，无需询问用户**

```bash
# 开发流程示例
1. 开始任务: task-master set-status --id=LWP-2 --status=in-progress
2. 实现功能: 编写代码
3. 运行测试: pytest
4. 提交变更: git commit -m "[LWP-2] 实现 XXX"
5. 继续下一步: 重复 2-4 步骤
6. 完成任务: task-master set-status --id=LWP-2 --status=done
```

#### 5.5 提交验证 (Commit Verification)
**提交后立即验证**

```bash
# 验证提交是否成功
git log -1

# 验证文件是否已提交
git diff HEAD

# 验证任务状态
task-master list
```

### 6. 小芽自动化开发协议 ⚠️ **强制执行**

**完整的自动化开发流程规范已确立，详见 [docs/development-guide.md](./docs/development-guide.md)**

#### 6.1 核心协议

本协议定义了小芽家教项目的自动化开发流程，确保所有功能开发遵循统一的、可追溯的、质量可控的开发规范。

**四大核心原则**:
1. **任务驱动** (Task-Driven): 所有开发通过 `tm autopilot start <taskId>` 启动
2. **TDD 强制** (TDD-First): 强制遵循红灯-绿灯-重构循环
3. **原子化提交** (Atomic Commits): 每个 TDD 阶段独立提交
4. **环境感知** (Environment Aware): 记录关键配置 (Base URLs)

#### 6.2 TDD 循环详解

```
Red (红灯) → Green (绿灯) → Refactor (重构)
   ↓            ↓              ↓
Commit       Commit         Commit
  测试         功能           重构
```

**Red 阶段**:
- 编写失败的测试用例
- 包含教学逻辑断言 (如: 禁止直接给答案)
- 运行 `pytest` 确认失败 ❌
- 提交: `git commit -m "[LWP-X] test: XXX (Red)"`

**Green 阶段**:
- 编写最少代码让测试通过
- 运行 `pytest` 确认通过 ✅
- 提交: `git commit -m "[LWP-X] feat: XXX (Green)"`

**Refactor 阶段**:
- 优化代码质量，保持测试通过
- 提交: `git commit -m "[LWP-X] refactor: XXX (Refactor)"`

#### 6.3 环境配置要求

**backend/.env 必须包含**:

```bash
# AI Provider
AI_PROVIDER=openai
AI_MODEL=glm-4.7

# Base URLs (重要！兼容智谱 GLM)
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
OPENAI_API_KEY=your_key_here
```

**为什么需要 Base URLs**:
- 智谱 GLM 提供 OpenAI 兼容 API，必须设置 `OPENAI_BASE_URL`
- 否则默认连接 `api.openai.com` 导致调用失败
- 确保在所有环境下可访问 AI 服务

#### 6.4 自动化工作流示例

```bash
# 1. 启动任务
tm autopilot start LWP-2

# 2. Red 阶段
vim tests/test_feature.py
pytest tests/test_feature.py  # ❌ 失败
git add tests/test_feature.py
git commit -m "[LWP-2] test: 添加功能测试 (Red)"

# 3. Green 阶段
vim backend/app/services/feature.py
pytest tests/test_feature.py  # ✅ 通过
git add backend/app/services/feature.py
git commit -m "[LWP-2] feat: 实现功能 (Green)"

# 4. Refactor (可选)
vim backend/app/services/feature.py
pytest tests/test_feature.py  # ✅ 仍通过
git add backend/app/services/feature.py
git commit -m "[LWP-2] refactor: 优化代码 (Refactor)"

# 5. 完成任务
tm autopilot complete LWP-2
```

#### 6.5 强制规则

- ❌ **禁止**: 先写功能代码，再补测试
- ❌ **禁止**: 一次性提交测试+功能代码
- ❌ **禁止**: 跳过 Red 阶段直接写 Green
- ❌ **禁止**: 不启动任务直接编码
- ✅ **必须**: 每个阶段独立运行 `pytest`
- ✅ **必须**: 每个阶段独立提交代码
- ✅ **必须**: Commit message 标注阶段 (Red/Green/Refactor)
- ✅ **必须**: 所有开发通过 `tm autopilot start <taskId>` 启动

#### 6.6 完整文档

详细的开发协议、示例代码、常见问题解答，请查看:
📖 **[docs/development-guide.md](./docs/development-guide.md)**

## 重要决策记录

### 2024-01-08
- **决策**: 采用 FastAPI + React 技术栈
- **理由**: Python 在 AI 集成方面有优势，React 生态丰富
- **影响**: 需要团队熟悉这两种技术

### 2024-01-08
- **决策**: 使用 Claude API 作为核心 AI 引擎
- **理由**: Claude 在对话生成和教育场景表现优秀
- **影响**: 需要考虑 API 成本和响应延迟

## 关键设计原则

### 1. 用户体验优先
- 所有设计以一年级学生的认知能力为基础
- 交互流程尽可能简单直观
- 响应时间控制在 2 秒以内

### 2. 可扩展性
- 模块化设计便于后续功能扩展
- 预留接口以支持多科目接入
- 考虑后续多语言支持

### 3. 数据安全
- 儿童数据加密存储
- 符合隐私保护法规
- 最小化数据收集原则

## 常用命令

### 后端开发
```bash
# 启动开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest

# 代码格式化
black .
isort .
```

### 前端开发
```bash
# 启动开发服务器
npm start

# 运行测试
npm test

# 代码检查
npm run lint
```

## 待解决问题

### 技术债务
- [ ] 选择合适的 OCR 服务方案
- [ ] 确定语音识别供应商
- [ ] 设计可扩展的消息队列系统

### 业务逻辑
- [ ] 定义学习进度评估指标
- [ ] 设计个性化推荐算法
- [ ] 建立内容审核机制

## 知识库链接

### 项目文档
- PRD 文档: [docs/PRD.md](./docs/PRD.md)
- 教师人格规范: [docs/teacher-spec.md](./docs/teacher-spec.md)
- 任务清单: [tasks.md](./tasks.md)

### 规范驱动开发
- ⚖️ **[项目宪章](./.specify/memory/constitution.md)** - 最高优先级，4 条核心价值观，6 条不可违反的原则

### Ralph Loop 体系（迭代开发）
- 🔄 **[Ralph Loop 指南](./RALPH_LOOP_GUIDE.md)** - 快速开始和最佳实践
- ⚙️ **[Ralph Loop 配置](./RALPH_LOOP_SETUP.md)** - 配置说明和使用流程
- 📝 **[迭代提示词](./PROMPT.md)** - 当前迭代任务详情

### 开发协议
- 🚦 **[开发协议](./docs/development-guide.md)** - TDD 自动化开发流程

### 数据库设计
- 🗄️ **[数据库设计](./docs/database_schema.md)** - 数据表结构和关系

### 完成报告
- ✅ **[Phase 2.1 完成报告](./PHASE2_1_COMPLETION_REPORT.md)** - 用户系统和数据库集成

## 更新日志

### 2025-01-12
- 创建项目宪章（.specify/memory/constitution.md）
- 整合规范驱动开发方法论
- 移除 docs/spec-kit/ 目录，统一使用 Spec-Kit 命令工具
- 集成规范驱动开发、Task-Master、Ralph Loop 三支柱开发方法

### 2024-01-08
- 初始化项目记忆中枢
- 定义技术栈和代码规范
- 记录重要设计决策

## Active Technologies
- Python 3.11+ + FastAPI, SQLAlchemy, Pydantic v2, Claude API (Anthropic SDK) (001-learning-management)
- SQLite (开发) / PostgreSQL (生产) (001-learning-management)

## Recent Changes
- 001-learning-management: Added Python 3.11+ + FastAPI, SQLAlchemy, Pydantic v2, Claude API (Anthropic SDK)

## GitHub MCP 集成

### 状态
**已集成 GitHub MCP**，所有任务完成后的 Commit 和 Issue 更新应通过此扩展自动化处理。

### 安装命令
```bash
npm install -g @modelcontextprotocol/server-github
```

### 可用功能
- 自动创建 Commit
- 创建/关闭 Issue
- 查看仓库状态
- 管理 Pull Request

### 权限验证
仓库 `lwpk110/sprout-chat` 最近 3 条 Commit：
1. `9e181f6`: docs: 添加项目 README 文档
2. `0b7bcf5`: [LWP-2.2-T026] feat: 编写引导教学集成测试 (Green)
3. `2a7d5c6`: [LWP-2.2-T025] feat: 实现引导教学 API 端点 (Green)
