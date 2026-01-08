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
- PRD 文档: [docs/PRD.md](./docs/PRD.md)
- 教师人格规范: [docs/teacher-spec.md](./docs/teacher-spec.md)
- 任务清单: [tasks.md](./tasks.md)

## 更新日志
### 2024-01-08
- 初始化项目记忆中枢
- 定义技术栈和代码规范
- 记录重要设计决策