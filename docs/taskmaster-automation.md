# Taskmaster 完全自动化使用指南

## 概述

本文档说明如何使用 Taskmaster 的命令行工具和 MCP 工具实现**完全自动化**的任务管理，无需手动操作。

**核心优势**:
- ✅ 无需手动复制粘贴
- ✅ 使用 Taskmaster 原生命令
- ✅ 支持 CLI 和 MCP 两种方式
- ✅ 完全集成到开发流程

## 快速开始

### 方法 1: 使用自动化脚本（推荐）

```bash
# 一键同步 Spec-Kit → Taskmaster
python3 scripts/auto-sync-to-taskmaster.py

# 查看任务列表
tm list --tag=learning-management

# 开始任务
tm autopilot start LWP-2.2-T001
```

### 方法 2: 使用 Taskmaster CLI

```bash
# 查看所有任务
tm list

# 查看特定 tag 的任务
tm list --tag=learning-management

# 查看任务详情
tm get LWP-2.2-T001

# 更新任务状态
tm set-status --id=LWP-2.2-T001 --status=in-progress

# 完成任务
tm set-status --id=LWP-2.2-T001 --status=done
```

### 方法 3: 使用 MCP 工具（在 Claude Code 中）

```python
# 查询任务
mcp__task-master-ai__get_tasks({
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management",
    "withSubtasks": false
})

# 更新状态
mcp__task-master-ai__set_task_status({
    "id": "LWP-2.2-T001",
    "status": "in-progress",
    "projectRoot": "/home/luwei/workspace/github/sprout-chat"
})

# 查找下一个任务
mcp__task-master-ai__next_task({
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management"
})
```

## Taskmaster 命令参考

### 1. 任务查询

```bash
# 列出所有任务
tm list

# 列出特定 tag 的任务
tm list --tag=learning-management

# 按状态过滤
tm list --status=pending
tm list --status=in-progress
tm list --status=done

# 组合过滤
tm list --tag=learning-management --status=pending
```

### 2. 任务详情

```bash
# 查看单个任务详情
tm get LWP-2.2-T001

# 查看多个任务（逗号分隔）
tm get LWP-2.2-T001,LWP-2.2-T002,LWP-2.2-T003
```

### 3. 任务状态管理

```bash
# 开始任务（设置为 in-progress）
tm set-status --id=LWP-2.2-T001 --status=in-progress

# 完成任务（设置为 done）
tm set-status --id=LWP-2.2-T001 --status=done

# 阻塞任务
tm set-status --id=LWP-2.2-T001 --status=blocked

# 取消任务
tm set-status --id=LWP-2.2-T001 --status=cancelled
```

### 4. 任务创建（从 PRD）

```bash
# 从 PRD 文件生成任务
tm parse-prd \
  --input=.taskmaster/docs/prd.txt \
  --output=.taskmaster/tasks/tasks.json \
  --tag=learning-management \
  --force
```

### 5. 任务扩展

```bash
# 展开任务为子任务
tm expand-task \
  --id=LWP-2.2 \
  --num=5 \
  --prompt="添加学习记录 API 的子任务" \
  --tag=learning-management
```

## 完整工作流

### 开发流程（完全自动化）

```bash
# ===== 阶段 1: 规范准备 =====
# 1. 编写 Spec-Kit 规范
/speckit.specify "实现学习管理系统"

# 2. 生成 Spec-Kit 任务
/speckit.tasks

# ===== 阶段 2: 任务同步 =====
# 3. 同步到 Taskmaster（自动化）
python3 scripts/auto-sync-to-taskmaster.py

# ===== 阶段 3: 任务执行 =====
# 4. 查看待办任务
tm list --tag=learning-management --status=pending

# 5. 开始任务
tm set-status --id=LWP-2.2-T001 --status=in-progress

# 6. 执行 TDD 开发
# Red → Green → Refactor

# 7. 完成任务
tm set-status --id=LWP-2.2-T001 --status=done

# ===== 阶段 4: 同步到 Hamster（可选）=====
# 8. 导出 Hamster Markdown
python3 scripts/taskmaster-to-hamster.py

# 9. 粘贴到 Hamster（已自动复制到剪贴板）
```

## MCP 工具详解

### 可用的 MCP 工具

| 工具 | 用途 | 输入参数 | 返回值 |
|------|------|----------|--------|
| `parse_prd` | 从 PRD 生成任务 | input, output, tag, force | 任务数量 |
| `get_tasks` | 获取任务列表 | projectRoot, tag, status, withSubtasks | 任务列表 |
| `get_task` | 获取单个任务 | id, projectRoot, tag, status | 任务详情 |
| `set_task_status` | 更新任务状态 | id, status, projectRoot, tag | 更新结果 |
| `expand_task` | 展开子任务 | id, num, prompt, projectRoot, tag, force | 子任务列表 |
| `next_task` | 查找下一个任务 | projectRoot, file, tag | 任务信息 |
| `update_subtask` | 更新子任务 | id, prompt, projectRoot, file, tag | 更新结果 |

### MCP 工具使用示例

#### 1. parse_prd - 从 PRD 生成任务

```python
mcp__task-master-ai__parse_prd({
    "input": "specs/001-learning-management/tasks.md",
    "output": ".taskmaster/tasks/tasks.json",
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "force": True
})
```

**返回**:
```
成功解析 PRD 并生成了 34 个任务
```

#### 2. get_tasks - 获取任务列表

```python
mcp__task-master-ai__get_tasks({
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management",
    "status": "pending",
    "withSubtasks": False
})
```

**返回**:
```json
{
  "tasks": [
    {
      "id": "LWP-2.2-T001",
      "title": "配置 Claude API 集成环境",
      "status": "pending",
      ...
    }
  ]
}
```

#### 3. set_task_status - 更新任务状态

```python
mcp__task-master-ai__set_task_status({
    "id": "LWP-2.2-T001",
    "status": "in-progress",
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management"
})
```

#### 4. next_task - 查找下一个任务

```python
mcp__task-master-ai__next_task({
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",
    "tag": "learning-management"
})
```

**返回**:
```
下一个待办任务: LWP-2.2-T001
```

## 自动化脚本对比

### 脚本 1: auto-sync-to-taskmaster.py

**用途**: Spec-Kit → Taskmaster 自动同步

**特点**:
- ✅ 直接修改 Taskmaster JSON
- ✅ 保留现有任务状态
- ✅ 无需手动操作

**使用**:
```bash
python3 scripts/auto-sync-to-taskmaster.py
```

### 脚本 2: speckit-to-taskmaster.py

**用途**: Spec-Kit → Taskmaster 同步（详细版）

**特点**:
- ✅ 完整的 Spec-Kit 元信息保留
- ✅ 生成同步报告
- ✅ 智能状态合并

**使用**:
```bash
python3 scripts/speckit-to-taskmaster.py
```

### 脚本 3: sync-all.sh

**用途**: 一键完整同步（Spec-Kit → Taskmaster → Hamster）

**特点**:
- ✅ 完整同步链路
- ✅ 自动复制到剪贴板

**使用**:
```bash
./scripts/sync-all.sh
```

## 最佳实践

### 1. 定期同步任务

```bash
# 添加到 git hooks（pre-commit）
#!/bin/bash
python3 scripts/auto-sync-to-taskmaster.py
git add .taskmaster/tasks/tasks.json
```

### 2. 使用 tm autopilot

```bash
# tm autopilot 会自动：
# 1. 设置任务状态为 in-progress
# 2. 创建 Git worktree（如果配置了）
# 3. 运行项目设置

tm autopilot start LWP-2.2-T001

# 完成后：
tm autopilot complete LWP-2.2-T001
```

### 3. Git Commit 格式

```bash
# 推荐：包含 Taskmaster ID 和 Spec-Kit ID
git commit -m "[LWP-2.2-T001][T001] feat: 配置 Claude API

- 添加 AI_PROVIDER、AI_MODEL 配置
- 测试 API 连接

Refs: LWP-2.2-T001, T001"
```

## 故障排查

### 问题 1: tm 命令不可用

**原因**: Taskmaster CLI 未安装或不在 PATH 中

**解决方案**:
```bash
# 检查 Taskmaster 安装
which tm

# 如果未安装，使用 npx
npx @tm/cli list

# 或使用 Python 脚本
python3 scripts/auto-sync-to-taskmaster.py
```

### 问题 2: 任务同步失败

**原因**: JSON 格式错误或文件权限问题

**解决方案**:
```bash
# 验证 JSON 格式
jq . .taskmaster/tasks/tasks.json

# 检查文件权限
ls -la .taskmaster/tasks/tasks.json

# 手动修复
python3 scripts/auto-sync-to-taskmaster.py
```

### 问题 3: MCP 工具调用失败

**原因**: projectRoot 路径不正确

**解决方案**:
```python
# 使用绝对路径
mcp__task-master-ai__get_tasks({
    "projectRoot": "/home/luwei/workspace/github/sprout-chat",  # 绝对路径
    "tag": "learning-management"
})
```

## 相关文档

| 文档 | 用途 |
|------|------|
| `scripts/auto-sync-to-taskmaster.py` | 自动同步脚本 |
| `scripts/speckit-to-taskmaster.py` | 详细同步脚本 |
| `scripts/sync-all.sh` | 一键同步脚本 |
| `docs/speckit-taskmaster-sync.md` | Spec-Kit 同步指南 |
| `.claude/skills/task-manager/SKILL.md` | Taskmanager Skill |

## 维护者

- **脚本作者**: Claude (Sonnet 4.5)
- **文档维护**: PM Agent
- **最后更新**: 2026-01-15
- **版本**: 2.1.0

---

**状态**: ✅ 生产就绪
**自动化级别**: 完全自动化（无需手动操作）
**支持方式**: CLI / MCP / 脚本
