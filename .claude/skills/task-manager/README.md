# Task Manager Skill - 使用指南

小芽家教项目的任务管理统一接口，简化 Task-Master MCP 操作。

## 快速开始

### 安装

task-manager skill 已经集成到项目中，无需额外安装。

### 基本用法

```bash
# 查看可领取任务
/task-manager list --status=pending --unclaimed

# 领取任务
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1

# 完成任务
/task-manager status LWP-2.2-T004 --status=done
```

## 常见场景

### 场景 1: PM Agent 创建任务

```bash
@pm:

# 1. 生成规范文档
/speckit.specify "实现学习记录功能"

# 2. 创建实施计划
/speckit.plan

# 3. 生成任务清单
/speckit.tasks

# 4. 🆖 自动导入到 Task-Master（speckit.tasks 自动调用）
# /task-manager import 001-learning-management --tag=learning-management

# 5. 验证导入
/task-manager list --tag=learning-management --status=pending

# 输出：
# ✅ 30 个任务已就绪，可以开始领取
```

### 场景 2: Backend Dev Agent 领取任务

```bash
@backend-dev-1:

# 1. 查询可领取任务
/task-manager list --status=pending --unclaimed

# 输出：
# 📋 可领取任务（5 个）：
# 1. LWP-2.2-T001 [P0] 配置 Claude API 集成环境
# 2. LWP-2.2-T002 [P0] 安装 Python 依赖包
# ...

# 2. 领取任务
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1

# 输出：
# ✅ 任务 LWP-2.2-T004 已被 backend-dev-1 领取

# 3. 阅读实施细节
cat specs/001-learning-management/tasks.md | grep -A 20 "T004"

# 4. 按照 TDD 循环实施
/tdd-cycle red
/tdd-cycle green
/tdd-cycle refactor

# 5. 提交代码
/git-commit [LWP-2.2-T004] feat: 实现学习记录模型

# 6. 更新任务状态
/task-manager status LWP-2.2-T004 --status=done

# 输出：
# ✅ 任务 LWP-2.2-T004 状态已更新为 done
```

### 场景 3: 多 Agent 并行开发

```bash
# 同时有 3 个 Dev Agent 工作

@backend-dev-1:
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1
✅ 领取成功

@backend-dev-2:
/task-manager claim LWP-2.2-T005 --agent=backend-dev-2
✅ 领取成功

@backend-dev-3:
/task-manager claim LWP-2.2-T004 --agent=backend-dev-3
❌ 失败，任务已被 backend-dev-1 领取

/task-manager claim LWP-2.2-T006 --agent=backend-dev-3
✅ 领取成功
```

## 命令参考

### /task-manager claim

领取任务，防止多 Agent 冲突。

```bash
/task-manager claim <task-id> --agent=<agent-id> [--tag=<tag-name>]
```

**示例**：
```bash
/task-manager claim LWP-2.2-T004 --agent=backend-dev-1
```

### /task-manager release

释放任务锁。

```bash
/task-manager release <task-id> --agent=<agent-id> [--tag=<tag-name>]
```

**示例**：
```bash
/task-manager release LWP-2.2-T004 --agent=backend-dev-1
```

### /task-manager status

更新任务状态。

```bash
/task-manager status <task-id> --status=<new-status> [--tag=<tag-name>]
```

**状态值**：`pending`, `in-progress`, `done`, `blocked`, `cancelled`

**示例**：
```bash
/task-manager status LWP-2.2-T004 --status=done
```

### /task-manager list

查询任务列表。

```bash
/task-manager list [--status=<status>] [--agent=<agent-id>] [--unclaimed] [--tag=<tag-name>]
```

**示例**：
```bash
# 查询可领取任务
/task-manager list --status=pending --unclaimed

# 查询我的任务
/task-manager list --agent=backend-dev-1

# 查询所有进行中任务
/task-manager list --status=in-progress
```

### /task-manager import

从 Spec-Kit 批量导入任务。

```bash
/task-manager import <spec-id> --tag=<tag-name> [--project-root=<path>]
```

**示例**：
```bash
/task-manager import 001-learning-management --tag=learning-management
```

### /task-manager sync

同步 Spec-Kit 与 Task-Master。

```bash
/task-manager sync <spec-id> [--tag=<tag-name>]
```

**示例**：
```bash
/task-manager sync 001-learning-management --tag=learning-management
```

## 集成工作流

### Spec-Kit 完整流程

```bash
# ========== 阶段 1: 规范创建 ==========

@pm:
1. /speckit.specify "实现学习记录功能"
2. /speckit.plan
3. /speckit.tasks
   → 🆖 自动调用 /task-manager import
   → ✅ 任务已导入

# ========== 阶段 2: 任务领取 ==========

@backend-dev-1:
1. /task-manager list --status=pending --unclaimed
2. /task-manager claim LWP-2.2-T004 --agent=backend-dev-1

# ========== 阶段 3: 执行实施 ==========

@backend-dev-1:
1. 阅读 tasks.md
2. /tdd-cycle red
3. /tdd-cycle green
4. /tdd-cycle refactor

# ========== 阶段 4: 完成任务 ==========

@backend-dev-1:
1. /git-commit [LWP-2.2-T004] feat: 实现学习记录模型
2. /task-manager status LWP-2.2-T004 --status=done
```

## 技术细节

### MCP 集成

task-manager skill 底层调用 Task-Master MCP API：

```python
# claim 操作的底层调用
mcp__task-master-ai__set_task_status({
    "id": "LWP-2.2-T004",
    "status": "in-progress",
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management"
})
```

### ID 映射规则

```
tasks.md     →  Task-Master
T001         →  LWP-2.2-T001
T002         →  LWP-2.2-T002
...
```

规则：`<spec-tag>-T<序号>`

## 故障排查

### 无法领取任务

**检查清单**：
1. 任务 ID 是否正确？
2. 任务是否已被其他 Agent 领取？
3. Tag 是否正确？

**调试命令**：
```bash
/task-manager list --tag=learning-management
```

### 任务导入失败

**检查清单**：
1. tasks.md 文件是否存在？
2. 格式是否正确？
3. Task-Master MCP 是否可用？

**调试命令**：
```bash
# 测试 MCP 连接
mcp__task-master-ai__get_tasks({
    "projectRoot": "/home/luwei/workspace/github/sprout-chat"
})
```

## 更多资源

- [SKILL.md](./SKILL.md) - 完整技能定义
- [examples/](./examples/) - 使用示例
- [项目任务管理设计](../../../docs/task-manager-skill-design.md) - 设计文档

---

**作者**: Claude Sonnet 4.5
**最后更新**: 2025-01-15
