# Task-Master Skill 设计方案

**日期**: 2025-01-15
**状态**: 设计阶段

---

## 现状分析

### 发现

1. ✅ **PM Agent 已经意识到 Task-Master 集成**
   - PM Agent 职责第 45 行："通知 Taskmaster 更新项目进度"
   - 但**缺少具体实现机制**

2. ❌ **没有 task-manager skill**
   - 现有 skills：git-commit, github-sync, tdd-cycle, socratic-teaching...
   - **缺少**：统一的 Task-Master 操作封装

3. ⚠️ **Spec-Kit 与 Task-Master 不同步**
   - `/speckit.tasks` 生成 tasks.md（Spec-Kit）
   - **但没有自动导入到 Task-Master**
   - 需要手动操作，容易遗漏

### 问题

```bash
# 当前流程（不完整）

1. /speckit.tasks → 生成 tasks.md ✅
2. tasks.md 创建成功 ✅
3. ❌ 然后？任务没有导入到 Task-Master！
4. Agent 无法领取任务
5. 无法追踪进度
```

---

## 解决方案：创建 task-manager skill

### 目标

封装 Task-Master 的常用操作，便于 Agent 调用，统一任务管理流程。

### Skill 定义

#### 基本信息

```yaml
---
name: task-manager
description: 封装 Task-Master 任务管理操作，支持任务领取、释放、状态更新、批量导入等
version: 1.0
author: Claude Sonnet 4.5
---
```

#### 核心功能

##### 1. 任务领取（Claim）

```markdown
## task-manager claim

**描述**：领取任务，防止多 Agent 冲突

**用法**：
```bash
/task-manager claim <task-id> --agent=<agent-id>
```

**示例**：
```bash
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1
```

**行为**：
1. 检查任务状态（必须是 pending）
2. 检查任务是否已被领取
3. 设置 claimed_by 和 claimed_at
4. 更新状态为 in-progress

**返回**：
```
✅ 任务 LWP-2.2-T004 已被 backend-dev-1 领取
```
```

##### 2. 任务释放（Release）

```markdown
## task-manager release

**描述**：释放任务，允许其他 Agent 领取

**用法**：
```bash
/task-manager release <task-id> --agent=<agent-id>
```

**示例**：
```bash
/task-manager release LWP-2.2-T004 --agent=backend-dev-1
```

**行为**：
1. 验证 agent 是否是当前领取者
2. 清除 claimed_by 和 claimed_at
3. 更新状态为 pending（如果未完成）

**返回**：
```
✅ 任务 LWP-2.2-T004 已释放
```
```

##### 3. 状态更新（Update Status）

```markdown
## task-manager status

**描述**：更新任务状态

**用法**：
```bash
/task-manager status <task-id> --status=<new-status>
```

**状态值**：
- `pending`：待处理
- `in-progress`：进行中
- `done`：已完成
- `blocked`：阻塞
- `cancelled`：取消

**示例**：
```bash
/task-manager status LWP-2.2-T004 --status=done
```

**行为**：
1. 验证状态转换是否合法
2. 更新状态和 updated_at
3. 如果是 done，自动释放 claimed_by

**返回**：
```
✅ 任务 LWP-2.2-T004 状态已更新为 done
```
```

##### 4. 批量导入（Import from Spec-Kit）

```markdown
## task-manager import

**描述**：从 Spec-Kit tasks.md 导入任务到 Task-Master

**用法**：
```bash
/task-manager import <spec-id> --tag=<tag-name>
```

**示例**：
```bash
/task-manager import 001-learning-management --tag=learning-management
```

**行为**：
1. 读取 `specs/<spec-id>/tasks.md`
2. 解析任务列表（T001, T002, T003...）
3. 生成 Task-Master 格式的任务
4. 批量创建到指定 tag
5. 保留依赖关系和优先级

**任务 ID 映射**：
```
tasks.md: T001 → Task-Master: LWP-2.2-T001
tasks.md: T002 → Task-Master: LWP-2.2-T002
```

**返回**：
```
✅ 已导入 30 个任务到 learning-management tag
- T001: 配置 Claude API 集成环境
- T002: 安装 Python 依赖包
- T003: 创建数据加密服务
...
- T030: 集成测试与验证

⚠️ 依赖关系已保留，5 个任务可并行执行
```
```

##### 5. 查询可领取任务（List Available）

```markdown
## task-manager list

**描述**：查询可领取的任务

**用法**：
```bash
/task-manager list --status=<status> --unclaimed
```

**示例**：
```bash
# 查询所有待领取任务
/task-manager list --status=pending --unclaimed

# 查询我的任务
/task-manager list --agent=backend-dev-1
```

**返回**：
```
📋 可领取任务列表（5 个）：

1. LWP-2.2-T001 [P0] 配置 Claude API 集成环境
   - 依赖：无
   - 预估时间：30 分钟

2. LWP-2.2-T002 [P0] 安装 Python 依赖包
   - 依赖：T001
   - 预估时间：15 分钟

3. LWP-2.2-T004 [P1] 创建学习记录扩展模型
   - 依赖：T003
   - 预估时间：2 小时
   - ⚠️ 等待 T003 完成

...
```
```

##### 6. 同步进度（Sync Progress）

```markdown
## task-manager sync

**描述**：同步任务进度（从 Spec-Kit tasks.md 到 Task-Master）

**用法**：
```bash
/task-manager sync <spec-id>
```

**行为**：
1. 对比 tasks.md 和 Task-Master 中的任务
2. 识别新增/删除/修改的任务
3. 更新 Task-Master 以匹配 tasks.md
4. 保留已完成任务的状态

**返回**：
```
✅ 同步完成
- 新增任务：2 个
- 更新描述：3 个
- 删除任务：0 个
- 保持状态：5 个（已完成）
```
```

---

## 增强 /speckit.tasks 集成

### 当前问题

```bash
# /speckit.tasks 只做了这一步
1. 读取 plan.md, spec.md, data-model.md
2. 生成 tasks.md
3. ❌ 结束（没有导入到 Task-Master）
```

### 改进方案

#### 方案 A：自动调用 task-manager skill（推荐）

```bash
# /speckit.tasks 完整流程

1. 读取 plan.md, spec.md, data-model.md ✅
2. 生成 tasks.md ✅
3. 🆕 自动调用：/task-manager import <spec-id> --tag=<spec-id>
4. 🆕 验证导入结果
5. 输出任务摘要
```

**实现**：在 `/speckit.tasks` skill 的最后一步添加：

```markdown
## 6. 导入到 Task-Master（自动）

**触发条件**：tasks.md 生成成功

**执行操作**：
```python
Skill(
    skill="task-manager",
    args=f"import {spec_id} --tag={spec_id}"
)
```

**验证**：
- 检查 Task-Master 中的任务数量
- 对比 tasks.md 和 Task-Master 任务列表
- 输出同步报告
```

#### 方案 B：手动调用（备选）

```bash
# PM Agent 需要手动执行

1. /speckit.tasks
2. /task-manager import 001-learning-management --tag=learning-management
```

**优点**：更灵活
**缺点**：容易遗忘

---

## 完整工作流

### 带有 task-manager skill 的完整流程

```bash
# ========== 阶段 1：规范创建 ==========

@pm:
1. /speckit.specify "实现学习记录功能"
   → 生成 spec.md

2. /speckit.analyze
   → 验证规范完整性

3. /speckit.plan
   → 生成 plan.md

4. /speckit.tasks
   → 生成 tasks.md
   → 🆕 自动调用 /task-manager import 001-learning-management
   → ✅ 30 个任务已导入到 Task-Master

# ========== 阶段 2：任务领取 ==========

@backend-dev-1:
1. /task-manager list --status=pending --unclaimed
   → 查看可领取任务

2. /task-manager claim LWP-2.2-T004 --agent=backend-dev-1
   → 领取任务

# ========== 阶段 3：执行实施 ==========

@backend-dev-1:
1. 阅读 specs/001-learning-management/tasks.md
2. 按照 TDD 循环实施
3. 遵循 /git-commit 规范提交

# ========== 阶段 4：完成 ==========

@backend-dev-1:
1. /task-manager status LWP-2.2-T004 --status=done
   → 更新任务状态

2. /task-manager release LWP-2.2-T004
   → 释放任务锁
```

---

## Skill 文件结构

```
.claude/skills/task-manager/
├── SKILL.md              # 主技能定义
├── README.md             # 使用文档
└── examples/
    ├── claim.md          # 领取任务示例
    ├── release.md        # 释放任务示例
    ├── import.md         # 批量导入示例
    └── workflow.md       # 完整工作流示例
```

---

## MCP 集成

task-manager skill 底层调用 Task-Master MCP：

```python
# task-manager claim LWP-2.2-T004 --agent=backend-dev-1

# 实际执行的 MCP 调用
mcp__task-master-ai__set_task_status({
    "id": "LWP-2.2-T004",
    "status": "in-progress",
    "projectRoot": "/path/to/project",
    "tag": "learning-management"
})

# 本地记录领取信息
update_claim_record({
    "task_id": "LWP-2.2-T004",
    "claimed_by": "backend-dev-1",
    "claimed_at": datetime.now()
})
```

---

## 与其他 Skills 的协作

### 与 git-commit skill

```bash
# 完整的开发循环

1. /task-manager claim LWP-2.2-T004 --agent=backend-dev-1
2. （实施代码）
3. /git-commit [LWP-2.2-T004] feat: 实现学习记录模型
4. /task-manager status LWP-2.2-T004 --status=done
```

### 与 tdd-cycle skill

```bash
# TDD 循环 + Task-Master

1. /task-manager claim LWP-2.2-T004 --agent=backend-dev-1

2. /tdd-cycle red
   → 编写测试
   → /git-commit [LWP-2.2-T004] test: 添加学习记录测试 (Red)

3. /tdd-cycle green
   → 实现功能
   → /git-commit [LWP-2.2-T004] feat: 实现学习记录模型 (Green)

4. /tdd-cycle refactor
   → 重构代码
   → /git-commit [LWP-2.2-T004] refactor: 优化代码 (Refactor)

5. /task-manager status LWP-2.2-T004 --status=done
```

### 与 github-sync skill

```bash
# 完成后同步到 GitHub

1. /task-manager status LWP-2.2-T004 --status=done
2. /github-sync close-issue LWP-2.2-T004
3. /github-sync create-commit "任务 LWP-2.2-T004 已完成"
```

---

## PM Agent 更新

### 新增职责

```markdown
### 6. 任务同步与进度管理

- **职责**：确保 Spec-Kit 任务与 Task-Master 保持同步
- **操作**：
  - `/speckit.tasks` 执行后，验证任务已导入到 Task-Master
  - 监控任务进度，识别阻塞问题
  - 协调多 Agent 并行开发

**工作流**：
```
/speckit.tasks
    ↓
验证：/task-manager list --tag=<spec-id>
    ↓
确认导入成功
    ↓
通知 Dev Agent 可以开始领取任务
```
```

---

## 实施计划

### Phase 1: 创建 task-manager skill（1小时）

- [ ] 创建 `.claude/skills/task-manager/SKILL.md`
- [ ] 定义核心功能（claim, release, status, list, import）
- [ ] 编写使用示例
- [ ] 测试 MCP 集成

### Phase 2: 增强 /speckit.tasks（30分钟）

- [ ] 修改 `/speckit.tasks` skill
- [ ] 添加自动导入逻辑
- [ ] 验证导入结果
- [ ] 输出同步报告

### Phase 3: 更新 PM Agent（30分钟）

- [ ] 更新 PM Agent 职责定义
- [ ] 添加任务同步流程
- [ ] 更新工作流文档

### Phase 4: 文档与测试（1小时）

- [ ] 编写使用指南
- [ ] 编写完整工作流示例
- [ ] 测试端到端流程

---

## 预期效果

### Before（当前）

```bash
@pm:
/speckit.tasks
✅ tasks.md 生成成功

@backend-dev-1:
❓ 我该做什么？
🤔 不知道，任务没有在 Task-Master 中

@pm:
😅 等等，我忘记导入到 Task-Master 了
# 手动操作，容易遗漏
```

### After（改进后）

```bash
@pm:
/speckit.tasks
✅ tasks.md 生成成功
🆖 自动导入到 Task-Master
✅ 30 个任务已就绪

@backend-dev-1:
/task-manager list --status=pending --unclaimed
✅ 看到可领取任务列表

/task-manager claim LWP-2.2-T004 --agent=backend-dev-1
✅ 任务已领取，开始实施
```

---

## 风险与缓解

### 风险

1. **Spec-Kit 与 Task-Master ID 冲突**
   - tasks.md: T001
   - Task-Master: LWP-2.2-T001
   - **缓解**：建立 ID 映射规则

2. **依赖关系自动识别错误**
   - tasks.md 中的依赖可能无法正确解析
   - **缓解**：提供手动修正机制

3. **批量导入导致 Task-Master 性能问题**
   - 30+ 任务同时创建
   - **缓解**：分批导入，每批 10 个

---

## 总结

### 核心价值

1. ✅ **自动化**：Spec-Kit 生成 tasks.md 后自动导入 Task-Master
2. ✅ **标准化**：统一的任务管理接口，所有 Agent 调用方式一致
3. ✅ **可追溯**：从规范到任务到执行的完整链路
4. ✅ **支持并行**：多 Agent 安全地领取和释放任务

### 关键创新

- **双向同步**：Spec-Kit ↔ Task-Master
- **自动导入**：`/speckit.tasks` 完成后自动调用 `/task-manager import`
- **Skill 封装**：统一的任务管理接口

---

**作者**: Claude Sonnet 4.5
**版本**: 1.0
**状态**: 待评审
