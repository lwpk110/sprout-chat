# 小芽自动化开发协议 (Sprout Autopilot Development Protocol)

**版本**: v1.0
**生效日期**: 2026-01-08
**状态**: 强制执行 ⚠️

---

## 协议概述

本协议定义了小芽家教项目的自动化开发流程，确保所有功能开发遵循统一的、可追溯的、质量可控的开发规范。

### 核心原则

1. **任务驱动** (Task-Driven): 所有开发必须通过 Taskmaster 任务 ID 启动
2. **隔离开发** (Isolated Development): 使用 Git Worktrees 创建隔离工作空间
3. **TDD 强制** (TDD-First): 强制遵循红灯-绿灯-重构循环
4. **原子化提交** (Atomic Commits): 每个 TDD 阶段独立提交
5. **环境感知** (Environment Aware): 记录关键环境配置

---

## 1. 任务驱动开发 (Task-Driven Development)

### 1.1 启动任务

**所有功能开发必须通过以下命令启动**:

```bash
tm autopilot start <taskId>
```

**示例**:
```bash
# 启动拍照识别功能开发
tm autopilot start LWP-2

# 启动家长监控功能开发
tm autopilot start LWP-4
```

### 1.2 任务状态验证

**启动前验证**:
```bash
# 检查任务状态
tm list

# 确认任务为 pending 或 in-progress
tm show LWP-2
```

**启动后确认**:
```bash
# 验证任务状态已更新为 in-progress
tm status LWP-2
```

### 1.3 强制规则

- ❌ **禁止**: 直接开始编码而不启动任务
- ❌ **禁止**: 使用未在 Taskmaster 中注册的任务 ID
- ✅ **必须**: 每次开发前执行 `tm autopilot start <taskId>`
- ✅ **必须**: 记录任务 ID 到 Git Commit 信息

### 1.4 创建隔离工作空间

**任务启动后，必须使用 Git Worktrees 创建隔离的开发环境**：

```bash
# 使用 using-git-worktrees 技能
# Agent 会自动：
# 1. 检查现有 worktree 目录
# 2. 验证 .gitignore 配置
# 3. 创建新的 worktree
# 4. 运行项目设置
# 5. 验证测试基线
```

**示例流程**：

```bash
# 1. Agent 启动任务
tm autopilot start LWP-2

# 2. Agent 调用 using-git-worktrees 技能
# 自动执行：
# - 检测 .worktrees/ 或 worktrees/ 目录
# - 验证目录被 .gitignore 忽略
# - 创建 worktree: git worktree add .worktrees/feature-ocr -b feature/ocr
# - 运行: npm install 或 pip install -r requirements.txt
# - 验证: pytest 或 npm test

# 3. Agent 切换到 worktree 目录
cd .worktrees/feature-ocr

# 4. 开始 TDD 开发流程...
```

**为什么需要 Worktrees**：

| 优势 | 说明 |
|------|------|
| **并行开发** | 同时在多个分支工作，无需频繁切换 |
| **隔离环境** | 每个功能独立工作空间，避免依赖冲突 |
| **干净基线** | 验证测试从干净状态开始，区分新 bug 与既有问题 |
| **安全验证** | 技能强制检查 .gitignore，防止意外提交 worktree 内容 |

**强制规则**：

- ❌ **禁止**: 在主分支直接开发功能
- ❌ **禁止**: 跳过 worktree 创建直接编码
- ✅ **必须**: 每个功能使用独立 worktree
- ✅ **必须**: 验证目录被 .gitignore 忽略
- ✅ **必须**: 运行测试验证干净基线

---

## 2. TDD 强制约束 (TDD Mandatory Cycle)

### 2.1 红灯-绿灯-重构循环

**所有功能开发必须严格遵循以下循环**:

```
┌─────────────────────────────────────────────────────┐
│                   TDD 开发循环                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│  │  Red    │ -> │  Green  │ -> │ Refactor│        │
│  │  (红灯) │    │  (绿灯) │    │ (重构)  │        │
│  └────┬────┘    └────┬────┘    └────┬────┘        │
│       │              │              │              │
│       v              v              v              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│  │ 编写    │    │ 实现    │    │ 优化    │        │
│  │ 失败    │    │ 功能    │    │ 代码    │        │
│  │ 测试    │    │ 代码    │    │ 质量    │        │
│  └────┬────┘    └────┬────┘    └────┬────┘        │
│       │              │              │              │
│       v              v              v              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│  │ Commit  │    │ Commit  │    │ Commit  │        │
│  │ 测试    │    │ 功能    │    │ 重构    │        │
│  └─────────┘    └─────────┘    └─────────┘        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2.2 Red 阶段 (红灯)

**目标**: 编写失败的测试用例

**执行步骤**:
1. **分析需求**: 理解功能要求
2. **编写测试**: 创建 `tests/test_*.py` 文件
3. **教学逻辑断言**:
   - 禁止行为测试 (如: "不能直接给答案")
   - 必须行为测试 (如: "必须使用比喻")
   - 边界条件测试
4. **运行测试**: 确认测试失败 (❌ Red)
5. **提交测试**: `git commit -m "[LWP-X] test: 添加 XXX 测试 (Red)"`

**示例**:
```python
# tests/test_pedagogy.py
def test_no_direct_answer():
    """测试：小芽绝不能直接给答案"""
    response = sprout.generate_response("5 + 3 = ?")

    # 禁用语断言
    assert "答案是8" not in response
    assert "等于8" not in response
```

**验收标准**:
- ✅ 测试文件已创建
- ✅ 运行 `pytest` 失败
- ✅ Git commit 已完成
- ✅ Commit message 包含 "(Red)" 标记

### 2.3 Green 阶段 (绿灯)

**目标**: 编写最少代码让测试通过

**执行步骤**:
1. **分析失败原因**: 理解为什么测试失败
2. **编写功能代码**: 修改/创建功能代码
3. **运行测试**: 确认测试通过 (✅ Green)
4. **提交功能**: `git commit -m "[LWP-X] feat: 实现 XXX 功能 (Green)"`

**原则**:
- 编写**最少**代码让测试通过
- 不过度设计
- 不考虑未来扩展

**示例**:
```python
# backend/app/services/sprout_persona.py
SPROUT_SYSTEM_PROMPT = """
你是小芽老师，绝对不能直接给答案。

## 禁用语（绝对不能说）
- "答案是..."
- "等于8"
- ...
"""
```

**验收标准**:
- ✅ 功能代码已实现
- ✅ 运行 `pytest` 全部通过
- ✅ Git commit 已完成
- ✅ Commit message 包含 "(Green)" 标记

### 2.4 Refactor 阶段 (重构 - 可选)

**目标**: 优化代码质量，保持测试通过

**执行步骤**:
1. **识别坏味道**: 重复代码、长函数、魔法数字等
2. **重构代码**: 提取方法、引入常量、优化结构
3. **验证测试**: 确保测试仍然通过
4. **提交重构**: `git commit -m "[LWP-X] refactor: 优化 XXX 代码 (Refactor)"`

**原则**:
- 测试必须保持通过
- 不改变功能行为
- 只优化代码结构

**验收标准**:
- ✅ 代码质量提升
- ✅ 运行 `pytest` 全部通过
- ✅ Git commit 已完成
- ✅ Commit message 包含 "(Refactor)" 标记

### 2.5 TDD 强制规则

- ❌ **禁止**: 先写功能代码，再补测试
- ❌ **禁止**: 一次性提交测试+功能代码
- ❌ **禁止**: 跳过 Red 阶段直接写 Green
- ❌ **禁止**: 测试失败时继续 Green 阶段
- ✅ **必须**: 每个阶段独立运行 `pytest`
- ✅ **必须**: 每个阶段独立提交代码
- ✅ **必须**: Commit message 标注阶段 (Red/Green/Refactor)

---

## 3. 原子化提交规范 (Atomic Commit Protocol)

### 3.1 提交频率

**每个 TDD 阶段完成后必须立即提交**:

```bash
# Red 阶段完成
git add tests/test_xxx.py
git commit -m "[LWP-X] test: 添加 XXX 测试 (Red)"

# Green 阶段完成
git add backend/app/services/xxx.py
git commit -m "[LWP-X] feat: 实现 XXX 功能 (Green)"

# Refactor 阶段完成
git add backend/app/services/xxx.py
git commit -m "[LWP-X] refactor: 优化 XXX 代码 (Refactor)"
```

### 3.2 Commit Message 格式

**格式**:
```
[Task-ID] type: description (Phase)

- 完成项 1
- 完成项 2

Refs: Task-ID

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Type 类型**:
- `test`: 测试相关 (Red 阶段)
- `feat`: 新功能 (Green 阶段)
- `refactor`: 代码重构 (Refactor 阶段)
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `chore`: 构建/工具相关

**Phase 标记**:
- `(Red)` - 红灯阶段
- `(Green)` - 绿灯阶段
- `(Refactor)` - 重构阶段

**示例**:
```bash
# Red 阶段提交
git commit -m "[LWP-2] test: 添加小芽教学法测试 (Red)

- 测试小芽不给答案
- 验证引导式提问
- 检查 System Prompt

Refs: LWP-2"

# Green 阶段提交
git commit -m "[LWP-2] feat: 优化 System Prompt (Green)

- 强化禁用语规则
- 添加比喻关键词
- 优化引导式提问

Refs: LWP-2"

# Refactor 阶段提交
git commit -m "[LWP-2] refactor: 提取 Prompt 模板 (Refactor)

- 将 Prompt 提取到独立模块
- 减少代码重复
- 提升可维护性

Refs: LWP-2"
```

### 3.3 强制规则

- ❌ **禁止**: 批量提交多个阶段的代码
- ❌ **禁止**: 提交信息缺少 Task-ID
- ❌ **禁止**: 提交信息缺少 Phase 标记
- ✅ **必须**: 每个 TDD 阶段独立提交
- ✅ **必须**: 提交前运行 `pytest` 验证
- ✅ **必须**: 提交信息遵循统一格式

---

## 4. 环境感知配置 (Environment Awareness)

### 4.1 关键环境变量

**backend/.env 必须记录以下配置**:

```bash
# AI Provider 配置
AI_PROVIDER=openai                    # 或 anthropic
AI_MODEL=glm-4.7                      # 或 claude-3-5-sonnet-20241022

# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Base URLs (重要！)
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ANTHROPIC_BASE_URL=https://api.anthropic.com

# 应用配置
SESSION_TIMEOUT_MINUTES=30
MAX_CONVERSATION_HISTORY=10
```

### 4.2 Base URLs 必要性

**为什么需要记录 Base URLs**:

1. **智谱 GLM 兼容性**:
   - 智谱 GLM 提供 OpenAI 兼容 API
   - 必须设置 `OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/`
   - 否则默认连接 `api.openai.com` 导致调用失败

2. **Claude API 可访问性**:
   - 某些网络环境需要代理
   - 可能需要设置 `ANTHROPIC_BASE_URL`
   - 确保在所有环境下可访问

3. **环境切换**:
   - 开发环境 vs 生产环境
   - 不同区域可能有不同 Base URL
   - 通过 `.env` 灵活配置

### 4.3 配置验证

**启动开发前必须验证**:

```bash
# 1. 检查 .env 文件存在
ls -la backend/.env

# 2. 验证关键配置
grep "OPENAI_BASE_URL" backend/.env
grep "AI_PROVIDER" backend/.env

# 3. 测试 API 连接
cd backend
python -c "from app.core.config import settings; print(settings.openai_base_url)"
```

### 4.4 强制规则

- ❌ **禁止**: 硬编码 Base URL 在代码中
- ❌ **禁止**: 将 `.env` 提交到 Git
- ✅ **必须**: 使用 `.env.example` 记录配置模板
- ✅ **必须**: 在 `CLAUDE.md` 中记录 Base URLs 重要性
- ✅ **必须**: 新开发环境启动时配置 `.env`

---

## 5. 自动化工作流示例 (Automated Workflow Example)

### 5.1 完整开发流程

**场景**: 开发"拍照识别功能" (LWP-2)

```bash
# 1. 启动任务
tm autopilot start LWP-2

# 2. 创建隔离工作空间 (using-git-worktrees 技能)
# Agent 自动执行：
# - 检测 .worktrees/ 目录
# - 验证 .gitignore 配置
# - 创建 worktree
git worktree add .worktrees/feature-ocr -b feature/ocr
cd .worktrees/feature-ocr

# - 运行项目设置
pip install -r requirements.txt

# - 验证测试基线
pytest  # 确保现有测试通过 ✅

# 3. Red 阶段
vim tests/test_ocr.py
# 编写测试...

pytest tests/test_ocr.py  # 应该失败 ❌

git add tests/test_ocr.py
git commit -m "[LWP-2] test: 添加 OCR 图像识别测试 (Red)"

# 4. Green 阶段
vim backend/app/services/ocr.py
# 实现 OCR 功能...

pytest tests/test_ocr.py  # 应该通过 ✅

git add backend/app/services/ocr.py
git commit -m "[LWP-2] feat: 实现 OCR 图像识别 (Green)"

# 5. Refactor 阶段 (可选)
vim backend/app/services/ocr.py
# 重构代码...

pytest tests/test_ocr.py  # 仍然通过 ✅

git add backend/app/services/ocr.py
git commit -m "[LWP-2] refactor: 优化 OCR 代码结构 (Refactor)"

# 6. 完成任务
tm autopilot complete LWP-2

# 7. 清理 worktree (可选)
cd ..
git worktree remove .worktrees/feature-ocr
```

### 5.2 自动化脚本

**创建 `scripts/autopilot.sh`**:

```bash
#!/bin/bash
# 小芽自动化开发脚本

TASK_ID=$1

if [ -z "$TASK_ID" ]; then
    echo "Usage: ./autopilot.sh <Task-ID>"
    exit 1
fi

echo "🚀 启动 Autopilot: $TASK_ID"
tm autopilot start $TASK_ID

echo "📝 进入 Red 阶段..."
# 自动创建测试文件模板
echo "✅ Red 阶段完成，请编写测试后运行: pytest"

echo "💡 提示: 完成后执行 git commit -m '[$TASK_ID] test: XXX (Red)'"
```

---

## 6. 质量保证 (Quality Assurance)

### 6.1 测试覆盖率要求

- **最低覆盖率**: 80%
- **核心模块**: 90%+
- **关键业务逻辑**: 100%

**检查命令**:
```bash
pytest --cov=app --cov-report=html
```

### 6.2 代码质量检查

**每次提交前必须执行**:

```bash
# 1. 语法检查
python -m py_compile backend/app/**/*.py

# 2. 代码格式化
black backend/app --check
isort backend/app --check

# 3. 类型检查 (可选)
mypy backend/app

# 4. 安全检查 (可选)
bandit -r backend/app
```

### 6.3 CI/CD 集成

**GitHub Actions 自动验证**:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest --cov=app
```

---

## 7. 违规处理 (Violation Handling)

### 7.1 违规类型

1. **轻度违规**:
   - Commit message 格式不完整
   - 缺少 Phase 标记

2. **中度违规**:
   - 跳过 Red 阶段
   - 批量提交多个阶段

3. **重度违规**:
   - 不启动任务直接编码
   - 不写测试直接提交功能

### 7.2 处理措施

- **轻度**: 警告，要求补充 Commit message
- **中度**: 要求拆分提交，补充 Red 阶段
- **重度**: 拒绝合并，要求重新遵循 TDD 流程

---

## 8. 自动化任务管理工具 (Automated Task Management)

### 8.1 工具概述

项目提供了一套完整的自动化任务管理工具链，实现 Spec-Kit → Taskmaster → Hamster 的自动化同步和可视化管理。

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Spec-Kit   │───▶│ Taskmaster  │───▶│   Hamster   │
│ (Markdown)  │    │   (JSON)    │    │  (Remote)   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   ▼
       │                   │            tryhamster.com
       │                   │                   │
       ▼                   ▼                   ▼
  tasks.md          tasks.json          任务管理平台
       │                   │                   │
       └─────────自动同步────┴─────────自动同步──┘
                   监听模式              推送模式
```

### 8.2 自动同步工具

#### 8.2.1 Spec-Kit → Taskmaster 同步

**脚本**: `scripts/auto-sync-to-taskmaster.py`

**功能**:
- 解析 `specs/*/tasks.md`
- 生成 Taskmaster JSON 格式
- 保留 Spec-Kit 元信息（Phase, User Story, TDD 状态）
- 智能合并：保留现有任务状态

**使用方法**:

```bash
# 单次同步
python3 scripts/auto-sync-to-taskmaster.py

# 监听模式（前台）
python3 scripts/auto-sync-to-taskmaster.py --watch

# 监听模式（后台）
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon

# 指定配置文件
python3 scripts/auto-sync-to-taskmaster.py \
  --speckit specs/001-learning-management/tasks.md \
  --taskmaster .taskmaster/tasks/tasks.json
```

**监听模式工作流程**:

1. 启动监听：`python3 scripts/auto-sync-to-taskmaster.py --watch`
2. 检测 `tasks.md` 变化（防抖 2 秒）
3. 自动解析并同步到 `tasks.json`
4. 保留现有任务状态（不覆盖 in-progress/done）
5. 显示同步结果

**后台模式日志**:

```bash
# 查看后台日志
tail -f /tmp/auto-sync-to-taskmaster.log

# 停止后台进程
kill $(cat /tmp/auto-sync-to-taskmaster.pid)
```

#### 8.2.2 Taskmaster → Hamster 同步

**脚本**: `scripts/auto-sync-to-hamster.py`

**功能**:
- 监听 `tasks.json` 变化
- 自动推送到 Hamster（使用 `task-master add-task`）
- 批处理：每批 5 个任务，避免速率限制
- 任务已存在时自动跳过

**前置条件**:

```bash
# 1. 安装 Taskmaster CLI
npm install -g task-master-ai

# 2. 登录 Hamster
task-master auth login

# 3. 验证登录
task-master list
```

**使用方法**:

```bash
# 单次同步
python3 scripts/auto-sync-to-hamster.py

# 监听模式（前台）
python3 scripts/auto-sync-to-hamster.py --watch

# 监听模式（后台）
python3 scripts/auto-sync-to-hamster.py --watch --daemon

# 指定配置文件
python3 scripts/auto-sync-to-hamster.py \
  --config .taskmaster/tasks/tasks.json
```

**监听模式工作流程**:

1. 启动监听：`python3 scripts/auto-sync-to-hamster.py --watch`
2. 检测 `tasks.json` 变化（防抖 2 秒）
3. 调用 `task-master add-task` 批量推送
4. 显示推送进度和统计
5. 任务已存在时跳过（不报错）

### 8.3 Taskmaster CLI 增强工具

**脚本**: `scripts/tm-cli.py`

**提供命令**:
- `tm-cli visualize`: 显示任务树形图
- `tm-cli stats`: 显示任务进度统计

#### 8.3.1 visualize 命令

**功能**:
- ASCII 树形结构，支持所有终端
- 显示状态图标（⭕🔄✅🚫❌⏸️👀）
- 显示优先级标识（🔥🟡🟢）

**使用方法**:

```bash
# 显示任务树形图
python3 scripts/tm-cli.py visualize

# 指定配置文件
python3 scripts/tm-cli.py visualize \
  --config .taskmaster/tasks/tasks.json

# 指定 Tag
python3 scripts/tm-cli.py visualize --tag my-feature
```

**输出示例**:

```
[INFO] 已加载 34 个任务（Tag: learning-management）
└─ ⭕ LWP-2.2-T001: 配置 Claude API 集成环境 🔥
└─ ⭕ LWP-2.2-T002: 安装 Python 依赖包 🔥
└─ ✅ LWP-2.2-T003: 创建数据加密服务 🔥
  └─ 🔄 LWP-2.2-T004: 创建学习记录扩展模型 🟡
```

#### 8.3.2 stats 命令

**功能**:
- 总览：总任务数、进度百分比
- 状态分布：条形图可视化
- 优先级分布：数量和占比
- Spec-Kit 元信息：Phase 和 User Story 分布
- 支持 JSON 输出

**使用方法**:

```bash
# 文本格式输出
python3 scripts/tm-cli.py stats

# JSON 格式输出
python3 scripts/tm-cli.py stats --format json

# 指定配置文件和 Tag
python3 scripts/tm-cli.py stats \
  --config .taskmaster/tasks/tasks.json \
  --tag my-feature
```

**输出示例**:

```
======================================================================
Taskmaster 任务统计
======================================================================

📊 总览
----------------------------------------------------------------------
总任务数: 34
进度: 25.0%

📋 状态分布
----------------------------------------------------------------------
  ⭕ 待办            20 ( 58.8%) [████████████░░░░░░░░]
  🔄 进行中          10 ( 29.4%) [███████████░░░░░░░░]
  ✅ 已完成           4 ( 11.8%) [███░░░░░░░░░░░░░░░]

🎯 优先级分布
----------------------------------------------------------------------
  🔥 高     25 ( 73.5%)
  🟡 中      9 ( 26.5%)

📚 Phase 分布
----------------------------------------------------------------------
  Phase 1: 12
  Phase 2: 14
  Phase 3: 8

======================================================================
```

### 8.4 完整自动化工作流

**推荐工作流**:

```bash
# ===== 阶段 1: 启动自动同步 =====

# Terminal 1: Spec-Kit → Taskmaster 自动同步
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon

# Terminal 2: Taskmaster → Hamster 自动同步
python3 scripts/auto-sync-to-hamster.py --watch --daemon

# ===== 阶段 2: 开发工作流 =====

# 1. 编辑 Spec-Kit tasks.md
vim specs/001-learning-management/tasks.md

# 2. 自动同步到 Taskmaster（检测到变化）
# [INFO] 检测到 tasks.md 变化
# [SUCCESS] 已同步 34 个任务到 Taskmaster

# 3. 自动推送到 Hamster（检测到变化）
# [INFO] 检测到 tasks.json 变化
# [SUCCESS] 已推送 34 个任务到 Hamster

# 4. 查看任务统计
python3 scripts/tm-cli.py stats

# 5. 查看任务树形图
python3 scripts/tm-cli.py visualize

# ===== 阶段 3: 任务开发 =====

# 启动任务
tm autopilot start LWP-2.2-T001

# 创建 worktree（using-git-worktrees 技能）
# Agent 自动执行...

# TDD 开发流程...
```

### 8.5 工具依赖安装

**必需依赖**:

```bash
# 安装 watchdog（文件监听）
pip install watchdog

# 或使用 requirements.txt
pip install -r requirements.txt
```

**可选依赖**:

```bash
# 安装 Taskmaster CLI（用于 Hamster 同步）
npm install -g task-master-ai

# 登录 Hamster
task-master auth login
```

### 8.6 故障排查

#### 问题 1: watchdog 未安装

**错误信息**:
```
[ERROR] 未安装 watchdog 库
请运行: pip install watchdog
```

**解决方案**:
```bash
pip install watchdog
```

#### 问题 2: Hamster 登录失败

**错误信息**:
```
[ERROR] 未登录或登录失败
```

**解决方案**:
```bash
# 重新登录
task-master auth login

# 验证登录
task-master list
```

#### 问题 3: 后台进程停止

**错误信息**:
```
[ERROR] 无法连接到后台进程
```

**解决方案**:
```bash
# 查看日志
tail -f /tmp/auto-sync-to-taskmaster.log

# 重启后台进程
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon
```

### 8.7 最佳实践

#### 1. 定期检查同步状态

```bash
# 每日检查任务统计
python3 scripts/tm-cli.py stats

# 每周查看任务树形图
python3 scripts/tm-cli.py visualize
```

#### 2. 后台模式日志管理

```bash
# 定期清理日志
> /tmp/auto-sync-to-taskmaster.log
> /tmp/auto-sync-to-hamster.log

# 或使用 logrotate
```

#### 3. Git hooks 集成

**添加 `.git/hooks/post-commit`**:

```bash
#!/bin/bash
# Commit 后自动推送到 Hamster

python3 scripts/auto-sync-to-hamster.py
```

#### 4. IDE 集成

**VS Code tasks.json**:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Sync Taskmaster",
      "type": "shell",
      "command": "python3 scripts/auto-sync-to-taskmaster.py"
    },
    {
      "label": "Sync Hamster",
      "type": "shell",
      "command": "python3 scripts/auto-sync-to-hamster.py"
    },
    {
      "label": "Show Stats",
      "type": "shell",
      "command": "python3 scripts/tm-cli.py stats"
    }
  ]
}
```

---

## 9. 附录 (Appendix)

### 9.1 常用命令速查

```bash
# Taskmaster 命令
tm list                              # 列出所有任务
tm show <Task-ID>                    # 查看任务详情
tm autopilot start <Task-ID>         # 启动任务
tm autopilot complete <Task-ID>      # 完成任务

# Git 命令
git status                           # 查看状态
git add <files>                      # 添加文件
git commit -m "message"              # 提交
git log -1                           # 查看最近提交

# 测试命令
pytest                               # 运行所有测试
pytest tests/test_xxx.py             # 运行指定测试
pytest -v                            # 详细输出
pytest --cov=app                     # 测试覆盖率

# 代码质量
black . --check                      # 检查格式
isort . --check                      # 检查导入排序
```

### 8.2 模板文件

**测试模板**: `tests/test_feature_template.py`
**功能模板**: `backend/app/services/feature_template.py`
**Commit 模板**: `.gitmessage`

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v1.0 | 2026-01-08 | 初始版本，确立 TDD 强制流程 |
| v1.1 | 2026-01-15 | 添加自动化任务管理工具章节 |

---

**协议维护**: 本协议由项目架构师维护，任何修改需要团队讨论并通过。

**强制执行**: 所有参与小芽家教项目的开发者必须遵守本协议。

**协议生效**: 自 2026-01-08 起，所有新功能开发必须遵循本协议。

---

**最后更新**: 2026-01-15
**文档维护者**: Claude Sonnet 4.5
**审核状态**: ✅ 已通过团队审核
