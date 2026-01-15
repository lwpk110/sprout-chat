---
name: task-manager
description: 封装 Task-Master 任务管理操作，支持任务领取、释放、状态更新、批量导入 Spec-Kit 任务等核心功能。统一多 Agent 任务管理接口，支持并行开发。
version: 1.0
author: Claude Sonnet 4.5
---

# Task Manager Skill

小芽家教项目的任务管理统一接口，封装 Task-Master MCP 操作，支持多 Agent 并行开发。

## 核心功能

### 1. 任务领取（Claim）

领取任务以防止多 Agent 冲突，设置任务锁定。

**用法**：
```bash
/task-manager claim <task-id> --agent=<agent-id> [--tag=<tag-name>]
```

**参数**：
- `task-id`: 任务 ID（如 LWP-2.2-T004）
- `--agent`: 领取任务的 Agent ID（如 backend-dev-1）
- `--tag`: Task-Master tag（可选，默认从项目配置读取）

**示例**：
```bash
# 领取单个任务
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1

# 领取特定 tag 的任务
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1 --tag=learning-management
```

**返回**：
```
✅ 任务 LWP-2.2-T004 已被 backend-dev-1 领取
   - 状态更新为 in-progress
   - 领取时间: 2025-01-15 10:30:00
```

**错误处理**：
- ❌ 任务已被其他 Agent 领取 → 返回冲突信息
- ❌ 任务状态不是 pending → 返回状态错误
- ❌ 任务不存在 → 返回未找到信息

---

### 2. 任务释放（Release）

释放任务锁，允许其他 Agent 领取。

**用法**：
```bash
/task-manager release <task-id> --agent=<agent-id> [--tag=<tag-name>]
```

**参数**：
- `task-id`: 任务 ID
- `--agent`: 当前领取者的 Agent ID
- `--tag`: Task-Master tag（可选）

**示例**：
```bash
# 释放任务
/task-manager release LWP-2.2-T004 --agent=backend-dev-1
```

**返回**：
```
✅ 任务 LWP-2.2-T004 已释放
   - 状态重置为 pending
   - 其他 Agent 现在可以领取
```

**自动触发**：
- 任务状态更新为 `done` 时自动释放
- Agent 异常中断时超时释放（需配置超时时间）

---

### 3. 状态更新（Status）

更新任务状态，支持状态转换验证。

**用法**：
```bash
/task-manager status <task-id> --status=<new-status> [--tag=<tag-name>]
```

**状态值**：
- `pending`: 待处理
- `in-progress`: 进行中
- `done`: 已完成
- `blocked`: 阻塞
- `cancelled`: 取消
- `deferred`: 延期
- `review`: 待审查

**示例**：
```bash
# 标记任务完成
/task-manager status LWP-2.2-T004 --status=done

# 标记任务阻塞
/task-manager status LWP-2.2-T004 --status=blocked

# 取消任务
/task-manager status LWP-2.2-T004 --status=cancelled
```

**返回**：
```
✅ 任务 LWP-2.2-T004 状态已更新为 done
   - 完成时间: 2025-01-15 12:30:00
   - 任务锁已自动释放
```

**状态转换规则**：
```
pending → in-progress → done
    ↓         ↓
blocked   cancelled
    ↓         ↓
pending ← pending
```

---

### 4. 查询任务（List）

查询任务列表，支持多种过滤条件。

**用法**：
```bash
/task-manager list [--status=<status>] [--agent=<agent-id>] [--unclaimed] [--tag=<tag-name>]
```

**过滤参数**：
- `--status`: 按状态过滤（pending, in-progress, done 等）
- `--agent`: 查询特定 Agent 的任务
- `--unclaimed`: 仅显示未领取的任务
- `--tag`: Task-Master tag（可选）

**示例**：
```bash
# 查询所有可领取任务
/task-manager list --status=pending --unclaimed

# 查询我的任务
/task-manager list --agent=backend-dev-1

# 查询所有进行中的任务
/task-manager list --status=in-progress

# 查询特定 tag 的任务
/task-manager list --tag=learning-management --status=pending
```

**返回**：
```
📋 可领取任务列表（5 个）：

1. LWP-2.2-T001 [P0] 配置 Claude API 集成环境
   - 依赖：无
   - 预估时间：30 分钟
   - 优先级：critical

2. LWP-2.2-T002 [P0] 安装 Python 依赖包
   - 依赖：LWP-2.2-T001
   - 预估时间：15 分钟
   - 优先级：critical
   - ⚠️ 等待依赖任务完成

3. LWP-2.2-T004 [P1] 创建学习记录扩展模型
   - 依赖：LWP-2.2-T003
   - 预估时间：2 小时
   - 优先级：high

...
```

---

### 5. 批量导入（Import）

从 Spec-Kit tasks.md 批量导入任务到 Task-Master。

**用法**：
```bash
/task-manager import <spec-id> --tag=<tag-name> [--project-root=<path>]
```

**参数**：
- `spec-id`: Spec-Kit 规范 ID（如 001-learning-management）
- `--tag`: 目标 Task-Master tag
- `--project-root`: 项目根路径（可选，默认当前目录）

**示例**：
```bash
# 导入学习管理任务
/task-manager import 001-learning-management --tag=learning-management

# 指定项目路径
/task-manager import 001-learning-management --tag=learning-management --project-root=/path/to/project
```

**返回**：
```
✅ 已导入 30 个任务到 learning-management tag

任务列表：
1. LWP-2.2-T001 [P0] 配置 Claude API 集成环境
2. LWP-2.2-T002 [P0] 安装 Python 依赖包
3. LWP-2.2-T003 [P0] 创建数据加密服务
...
30. LWP-2.2-T030 [P2] 集成测试与验证

⚠️ 依赖关系已保留，5 个任务可立即并行执行
📊 统计：
   - P0（critical）: 6 个
   - P1（high）: 15 个
   - P2（medium）: 9 个

📖 相关文档：
   - Spec: specs/001-learning-management/spec.md
   - Plan: specs/001-learning-management/plan.md
   - Tasks: specs/001-learning-management/tasks.md
```

**ID 映射规则**：
```
tasks.md 中的任务 ID    →  Task-Master 任务 ID
T001                    →  LWP-2.2-T001
T002                    →  LWP-2.2-T002
...
T030                    →  LWP-2.2-T030

规则：<spec-tag>-T<序号>
```

**依赖关系保留**：
- 自动解析 tasks.md 中的依赖声明
- 在 Task-Master 中设置 dependencies 字段
- 验证依赖闭环（防止循环依赖）

---

### 6. 同步进度（Sync）

同步 Spec-Kit tasks.md 与 Task-Master 的任务状态。

**用法**：
```bash
/task-manager sync <spec-id> [--tag=<tag-name>]
```

**示例**：
```bash
# 同步任务状态
/task-manager sync 001-learning-management --tag=learning-management
```

**返回**：
```
✅ 同步完成

变更摘要：
- 新增任务：2 个
  - LWP-2.2-T031: 添加性能监控
  - LWP-2.2-T032: 编写使用文档

- 更新描述：3 个
  - LWP-2.2-T004: 描述已更新
  - LWP-2.2-T015: 描述已更新
  - LWP-2.2-T020: 描述已更新

- 删除任务：0 个

- 保持状态：5 个（已完成任务不变）
  - LWP-2.2-T001: done
  - LWP-2.2-T002: done
  - LWP-2.2-T003: done
  - LWP-2.2-T004: in-progress
  - LWP-2.2-T005: done
```

**同步策略**：
- **新增任务**：tasks.md 中有但 Task-Master 中没有 → 创建
- **更新任务**：描述、优先级有变化 → 更新
- **删除任务**：tasks.md 中没有但 Task-Master 中有 → 标记为 cancelled
- **保留状态**：已完成（done）的任务保持状态

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

## MCP 集成

task-manager skill 底层调用 Task-Master MCP API。

### claim 操作的 MCP 调用

```python
# /task-manager claim LWP-2.2-T004 --agent=backend-dev-1

# 步骤 1: 检查任务状态
mcp__task-master-ai__get_task({
    "id": "LWP-2.2-T004",
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management"
})

# 步骤 2: 更新状态为 in-progress
mcp__task-master-ai__set_task_status({
    "id": "LWP-2.2-T004",
    "status": "in-progress",
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management"
})

# 步骤 3: 本地记录领取信息（如果需要持久化）
update_claim_record({
    "task_id": "LWP-2.2-T004",
    "claimed_by": "backend-dev-1",
    "claimed_at": "2025-01-15T10:30:00Z",
    "heartbeat_interval": 300  # 5 分钟心跳
})
```

### import 操作的 MCP 调用

```python
# /task-manager import 001-learning-management --tag=learning-management

# 步骤 1: 读取 tasks.md
tasks_md = read_file("specs/001-learning-management/tasks.md")

# 步骤 2: 解析任务列表
tasks = parse_tasks_markdown(tasks_md)
# 返回: [{"id": "T001", "title": "...", "priority": "P0", ...}, ...]

# 步骤 3: 批量创建到 Task-Master
for task in tasks:
    task_id = f"LWP-2.2-{task['id']}"  # T001 → LWP-2.2-T001
    mcp__task-master-ai__create_task({
        "title": task['title'],
        "description": task['description'],
        "priority": map_priority(task['priority']),  # P0 → critical
        "dependencies": task.get('dependencies', []),
        "projectRoot": "/home/luwei/workspace/github/sprout-chat",
        "tag": "learning-management"
    })

# 步骤 4: 验证导入结果
result = mcp__task-master-ai__get_tasks({
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management",
    "withSubtasks": false
})

# 步骤 5: 返回导入报告
return generate_import_report(result)
```

---

## 错误处理

### 任务已被领取

```
❌ 任务 LWP-2.2-T004 已被 backend-dev-2 领取
   - 领取时间: 2025-01-15 10:25:00
   - 心跳时间: 2025-01-15 10:30:00

💡 建议：
   - 等待任务完成或释放
   - 或联系 backend-dev-2 协调任务分配
```

### 状态转换非法

```
❌ 无法将任务状态从 done 更新为 in-progress
   - 任务已完成，不能重新开始

💡 建议：
   - 如果需要重新工作，请创建新任务
   - 或使用 /task-manager sync 同步状态
```

### 任务不存在

```
❌ 任务 LWP-2.2-T999 不存在
   - Tag: learning-management
   - Project: /home/luwei/workspace/github/sprout-chat

💡 建议：
   - 检查任务 ID 是否正确
   - 使用 /task-manager list 查看所有任务
```

---

## 配置

### 项目配置（.claude/config.json）

```json
{
  "task-manager": {
    "defaultTag": "learning-management",
    "heartbeatInterval": 300,
    "claimTimeout": 3600,
    "projectId": "LWP-2.2",
    "autoSync": true
  }
}
```

**配置说明**：
- `defaultTag`: 默认 Task-Master tag
- `heartbeatInterval`: 心跳间隔（秒），用于检测活跃 Agent
- `claimTimeout`: 领取超时（秒），超时后自动释放
- `projectId`: 项目 ID，用于生成任务 ID（如 LWP-2.2）
- `autoSync`: 是否自动同步 Spec-Kit 任务

---

## 使用场景

### 场景 1: 多 Agent 并行开发

```bash
# 3 个 Dev Agent 同时工作，无冲突

@backend-dev-1:
/task-manager list --status=pending --unclaimed
→ 看到可领取任务列表

/task-manager claim LWP-2.2-T004 --agent=backend-dev-1
→ 领取成功

@backend-dev-2:
/task-manager claim LWP-2.2-T005 --agent=backend-dev-2
→ 领取成功（不同任务）

@backend-dev-3:
/task-manager claim LWP-2.2-T004 --agent=backend-dev-3
→ ❌ 失败，任务已被 backend-dev-1 领取

/task-manager claim LWP-2.2-T006 --agent=backend-dev-3
→ 领取成功
```

### 场景 2: PM Agent 创建任务

```bash
@pm:
/speckit.tasks
→ 生成 tasks.md

/task-manager import 001-learning-management --tag=learning-management
→ 30 个任务已导入

/task-manager list --tag=learning-management --status=pending
→ 验证导入成功

通知 Dev Agent 可以开始领取任务
```

### 场景 3: Dev Agent 完整工作流

```bash
@backend-dev-1:

# 1. 查询可领取任务
/task-manager list --status=pending --unclaimed

# 2. 领取任务
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1

# 3. 阅读实施细节
cat specs/001-learning-management/tasks.md | grep -A 20 "T004"

# 4. 遵循 TDD 循环实施
/tdd-cycle red
/tdd-cycle green
/tdd-cycle refactor

# 5. 提交代码
/git-commit [LWP-2.2-T004] feat: 实现学习记录模型

# 6. 更新任务状态
/task-manager status LWP-2.2-T004 --status=done

# 7. 同步到 GitHub（可选）
/github-sync close-issue LWP-2.2-T004
```

---

## 最佳实践

### 1. 任务领取前先查询

```bash
# ✅ 好的做法
/task-manager list --status=pending --unclaimed
# 查看可领取任务
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1

# ❌ 不好的做法
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1
# 可能被拒绝（已被领取）
```

### 2. 完成任务后立即更新状态

```bash
# ✅ 好的做法
/git-commit [LWP-2.2-T004] feat: 实现学习记录模型
/task-manager status LWP-2.2-T004 --status=done
# 立即释放任务锁

# ❌ 不好的做法
/git-commit [LWP-2.2-T004] feat: 实现学习记录模型
# 忘记更新状态，任务一直被锁定
```

### 3. 使用批量导入而不是手动创建

```bash
# ✅ 好的做法
/speckit.tasks
# 自动调用 /task-manager import

# ❌ 不好的做法
# 手动在 Task-Master 中创建任务
# 容易遗漏或出错
```

---

## 故障排查

### 问题：无法领取任务

**检查清单**：
1. 任务 ID 是否正确？
2. 任务是否已被其他 Agent 领取？
3. 任务状态是否为 pending？
4. Tag 是否正确？

**调试命令**：
```bash
# 查看任务详情
/task-manager list --tag=learning-management

# 检查任务状态
mcp__task-master-ai__get_task({
    "id": "LWP-2.2-T004",
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management"
})
```

### 问题：任务导入失败

**检查清单**：
1. tasks.md 文件是否存在？
2. tasks.md 格式是否正确？
3. Task-Master MCP 是否可用？
4. Tag 名称是否有效？

**调试命令**：
```bash
# 手动解析 tasks.md
cat specs/001-learning-management/tasks.md | grep "^- \[ \] T"

# 测试 Task-Master MCP 连接
mcp__task-master-ai__get_tasks({
    "projectRoot": "/home/luwei/workspace/github/sprout-chat"
})
```

---

## 版本历史

- **v1.0** (2025-01-15): 初始版本
  - 支持任务领取、释放、状态更新
  - 支持从 Spec-Kit 批量导入
  - 支持任务查询和同步

---

**作者**: Claude Sonnet 4.5
**最后更新**: 2025-01-15
