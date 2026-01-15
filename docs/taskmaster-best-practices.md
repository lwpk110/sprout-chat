# Taskmaster 最佳实践指南

**版本**: v1.0
**更新日期**: 2026-01-15
**目标读者**: 开发者、项目经理

---

## 目录

1. [快速开始](#1-快速开始)
2. [核心概念](#2-核心概念)
3. [工作流程](#3-工作流程)
4. [最佳实践](#4-最佳实践)
5. [常见问题](#5-常见问题)
6. [进阶技巧](#6-进阶技巧)

---

## 1. 快速开始

### 1.1 环境准备

```bash
# 1. 安装依赖
pip install watchdog
npm install -g task-master-ai

# 2. 登录 Hamster（可选）
task-master auth login

# 3. 验证安装
python3 scripts/tm-cli.py stats
```

### 1.2 第一次使用

```bash
# 1. 从 Spec-Kit 同步到 Taskmaster
python3 scripts/auto-sync-to-taskmaster.py

# 2. 查看任务统计
python3 scripts/tm-cli.py stats

# 3. 查看任务树形图
python3 scripts/tm-cli.py visualize

# 4. 推送到 Hamster（可选）
python3 scripts/push-to-hamster.py
```

---

## 2. 核心概念

### 2.1 数据流向

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Spec-Kit   │───▶│ Taskmaster  │───▶│   Hamster   │
│  tasks.md   │    │ tasks.json  │    │  Remote     │
└─────────────┘    └─────────────┘    └─────────────┘
     人类可读          机器可读          团队协作
```

### 2.2 三大工具

| 工具 | 输入 | 输出 | 用途 |
|------|------|------|------|
| **auto-sync-to-taskmaster.py** | tasks.md | tasks.json | Spec-Kit → Taskmaster |
| **auto-sync-to-hamster.py** | tasks.json | Hamster | Taskmaster → Hamster |
| **tm-cli.py** | tasks.json | 终端输出 | 可视化和统计 |

### 2.3 Spec-Kit 元信息保留

**任务 ID 转换**:
- Spec-Kit: `T001`, `T002`, ...
- Taskmaster: `LWP-2.2-T001`, `LWP-2.2-T002`, ...

**元信息字段**:
```json
{
  "id": "LWP-2.2-T001",
  "metadata": {
    "source": "speckit",
    "phase": "Phase 1",
    "user_story": "US1",
    "original_id": "T001",
    "file": "specs/001-learning-management/tasks.md"
  }
}
```

---

## 3. 工作流程

### 3.1 日常开发流程

```bash
# ===== 早晨：启动自动同步 =====

# Terminal 1: 监听 Spec-Kit 变化
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon

# Terminal 2: 监听 Taskmaster 变化
python3 scripts/auto-sync-to-hamster.py --watch --daemon

# ===== 开发：编辑 Spec-Kit =====

vim specs/001-learning-management/tasks.md

# ===== 自动触发同步 =====

# [INFO] 检测到 tasks.md 变化
# [SUCCESS] 已同步 34 个任务到 Taskmaster
# [INFO] 检测到 tasks.json 变化
# [SUCCESS] 已推送 34 个任务到 Hamster

# ===== 查看进度 =====

python3 scripts/tm-cli.py stats
```

### 3.2 项目启动流程

```bash
# 1. 初始化 Spec-Kit
/speckit.specify "新功能"
/speckit.tasks

# 2. 同步到 Taskmaster
python3 scripts/auto-sync-to-taskmaster.py

# 3. 推送到 Hamster
python3 scripts/auto-sync-to-hamster.py

# 4. 启动任务
tm autopilot start LWP-2.2-T001

# 5. 创建 worktree（using-git-worktrees 技能）
# Agent 自动执行...

# 6. 开始 TDD 开发...
```

### 3.3 发布前检查清单

```bash
# ✅ 1. 检查任务状态
python3 scripts/tm-cli.py stats

# ✅ 2. 确认所有任务完成
# 查看进度是否 100%

# ✅ 3. 验证 Hamster 同步
task-master list

# ✅ 4. 检查未完成的任务
# 确保没有遗漏的 in-progress 任务

# ✅ 5. 停止后台监听
kill $(cat /tmp/auto-sync-to-taskmaster.pid)
kill $(cat /tmp/auto-sync-to-hamster.pid)
```

---

## 4. 最佳实践

### 4.1 使用监听模式

**推荐**: 开发时始终启用监听模式

```bash
# 启动后台监听
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon
python3 scripts/auto-sync-to-hamster.py --watch --daemon

# 验证后台进程
ps aux | grep auto-sync
```

**优点**:
- 自动同步，无需手动操作
- 实时推送，团队协作更顺畅
- 减少人为错误

### 4.2 定期查看统计

**每日**:
```bash
python3 scripts/tm-cli.py stats
```

**每周**:
```bash
python3 scripts/tm-cli.py visualize
```

**好处**:
- 及时发现进度偏差
- 识别阻塞任务
- 调整优先级

### 4.3 保留 Spec-Kit 元信息

**不要手动编辑 tasks.json**

❌ **错误做法**:
```bash
vim .taskmaster/tasks/tasks.json
# 手动修改任务...
```

✅ **正确做法**:
```bash
vim specs/001-learning-management/tasks.md
# 编辑 Spec-Kit 任务...
python3 scripts/auto-sync-to-taskmaster.py
# 自动同步
```

**原因**:
- Spec-Kit 是唯一真实来源（Single Source of Truth）
- tasks.json 由脚本自动生成
- 手动修改会在下次同步时被覆盖

### 4.4 任务状态管理

**使用 Taskmaster CLI 更新状态**:

```bash
# 开始任务
tm set-status --id=LWP-2.2-T001 --status=in-progress

# 完成任务
tm set-status --id=LWP-2.2-T001 --status=done

# 阻塞任务
tm set-status --id=LWP-2.2-T001 --status=blocked
```

**或者使用 MCP 工具**（在 Claude Code 中）:
```python
mcp__task-master-ai__set_task_status({
    "id": "LWP-2.2-T001",
    "status": "in-progress",
    "projectRoot": "/home/luwei/workspace/github/sprout-chat"
})
```

### 4.5 Git Commit 格式

**推荐格式**:
```bash
git commit -m "[LWP-2.2-T001] feat: 实现学习记录 API

- 添加 /api/v1/learning/records 端点
- 实现 CRUD 操作
- 添加单元测试

Refs: LWP-2.2-T001

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**关键字段**:
- `[Task-ID]`: 关联 Taskmaster 任务
- `type`: feat/fix/refactor/test/docs
- `Refs: Task-ID`: 可追溯性

### 4.6 后台进程管理

**启动**:
```bash
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon
python3 scripts/auto-sync-to-hamster.py --watch --daemon
```

**查看日志**:
```bash
tail -f /tmp/auto-sync-to-taskmaster.log
tail -f /tmp/auto-sync-to-hamster.log
```

**停止进程**:
```bash
# 查找进程 ID
ps aux | grep auto-sync

# 停止进程
kill <PID>

# 或使用 pkill
pkill -f auto-sync-to-taskmaster
pkill -f auto-sync-to-hamster
```

**重启进程**:
```bash
# 停止
pkill -f auto-sync-to-taskmaster

# 启动
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon
```

---

## 5. 常见问题

### 5.1 同步失败

**问题**: `tasks.json` 没有更新

**排查步骤**:

1. 检查文件权限
```bash
ls -la .taskmaster/tasks/tasks.json
```

2. 检查 Python 脚本
```bash
python3 scripts/auto-sync-to-taskmaster.py --verbose
```

3. 手动运行同步
```bash
python3 scripts/auto-sync-to-taskmaster.py
```

### 5.2 Hamster 推送失败

**问题**: 任务没有推送到 Hamster

**排查步骤**:

1. 验证登录状态
```bash
task-master list
```

2. 重新登录
```bash
task-master auth login
```

3. 手动推送
```bash
python3 scripts/push-to-hamster.py
```

### 5.3 任务状态丢失

**问题**: 同步后任务状态被重置

**原因**: Spec-Kit tasks.md 中的状态与 Taskmaster 不一致

**解决方案**: 脚本已实现智能合并，保留现有状态

```python
# auto-sync-to-taskmaster.py 中的逻辑
def _find_existing_task(self, task_id: str) -> Dict:
    """查找现有任务，保留状态"""
    if task_id in existing_tasks_map:
        return existing_tasks_map[task_id]
    return None
```

### 5.4 监听模式不工作

**问题**: 编辑 tasks.md 后没有自动同步

**排查步骤**:

1. 检查 watchdog 安装
```bash
pip show watchdog
```

2. 检查后台进程
```bash
ps aux | grep auto-sync
```

3. 查看日志
```bash
tail -f /tmp/auto-sync-to-taskmaster.log
```

4. 重启监听
```bash
pkill -f auto-sync-to-taskmaster
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon
```

### 5.5 可视化输出混乱

**问题**: `tm-cli visualize` 输出格式错乱

**原因**: 终端宽度不足

**解决方案**:

1. 增加终端宽度
```bash
# 调整终端窗口大小
```

2. 使用 JSON 格式（stats 命令）
```bash
python3 scripts/tm-cli.py stats --format json
```

---

## 6. 进阶技巧

### 6.1 多项目配置

**创建 `.tmrc` 配置文件**:

```json
{
  "projects": {
    "learning-management": {
      "speckit_file": "specs/001-learning-management/tasks.md",
      "taskmaster_file": ".taskmaster/tasks/tasks.json",
      "tag": "learning-management"
    },
    "ocr-module": {
      "speckit_file": "specs/002-ocr-module/tasks.md",
      "taskmaster_file": ".taskmaster/tasks/ocr.json",
      "tag": "ocr-module"
    }
  }
}
```

**使用配置**:
```bash
python3 scripts/auto-sync-to-taskmaster.py \
  --speckit specs/002-ocr-module/tasks.md \
  --tag ocr-module
```

### 6.2 Git Hooks 集成

**pre-commit hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# 同步到 Taskmaster
python3 scripts/auto-sync-to-taskmaster.py

# 检查是否有未完成的 in-progress 任务
IN_PROGRESS=$(python3 scripts/tm-cli.py stats --format json | jq '.status.in_progress')

if [ "$IN_PROGRESS" -gt 0 ]; then
  echo "⚠️  警告: 有 $IN_PROGRESS 个任务仍在进行中"
  read -p "是否继续提交? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi
```

**post-commit hook**:
```bash
#!/bin/bash
# .git/hooks/post-commit

# 推送到 Hamster
python3 scripts/auto-sync-to-hamster.py
```

### 6.3 IDE 集成

**VS Code `tasks.json`**:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Taskmaster: Sync",
      "type": "shell",
      "command": "python3 scripts/auto-sync-to-taskmaster.py",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Taskmaster: Stats",
      "type": "shell",
      "command": "python3 scripts/tm-cli.py stats",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Taskmaster: Visualize",
      "type": "shell",
      "command": "python3 scripts/tm-cli.py visualize",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
```

**使用**: `Ctrl+Shift+P` → `Tasks: Run Task` → 选择任务

### 6.4 CI/CD 集成

**GitHub Actions workflow**:
```yaml
name: Taskmaster Sync

on:
  push:
    paths:
      - 'specs/**/tasks.md'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install watchdog

      - name: Sync to Taskmaster
        run: |
          python3 scripts/auto-sync-to-taskmaster.py

      - name: Show stats
        run: |
          python3 scripts/tm-cli.py stats

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .taskmaster/tasks/tasks.json
          git commit -m "chore: sync Taskmaster tasks"
          git push
```

### 6.5 自定义脚本别名

**添加到 `.bashrc` 或 `.zshrc`**:
```bash
# Taskmaster 别名
alias tmsync='python3 scripts/auto-sync-to-taskmaster.py'
alias tmsp='python3 scripts/push-to-hamster.py'
alias tmstats='python3 scripts/tm-cli.py stats'
alias tmviz='python3 scripts/tm-cli.py visualize'
alias tmwatch='python3 scripts/auto-sync-to-taskmaster.py --watch --daemon'
```

**使用**:
```bash
tmsync    # 同步到 Taskmaster
tmstats   # 查看统计
tmviz     # 查看树形图
tmwatch   # 启动监听
```

### 6.6 性能优化

**批量操作**:
```bash
# 批量更新任务状态
for task in LWP-2.2-T001 LWP-2.2-T002 LWP-2.2-T003; do
  tm set-status --id=$task --status=done
done
```

**减少同步频率**:
```python
# 修改 DEBOUNCE_SECONDS 增加延迟
# auto-sync-to-taskmaster.py
DEBOUNCE_SECONDS = 5  # 默认 2 秒
```

**并行处理**:
```bash
# 并行启动监听
python3 scripts/auto-sync-to-taskmaster.py --watch --daemon &
python3 scripts/auto-sync-to-hamster.py --watch --daemon &
```

---

## 7. 参考资料

### 7.1 相关文档

- **开发协议**: [docs/development/development-guide.md](./development/development-guide.md)
- **项目宪章**: [.specify/memory/constitution.md](../.specify/memory/constitution.md)
- **Spec-Kit 文档**: [https://spec-kit.dev](https://spec-kit.dev)
- **Taskmaster 文档**: [https://docs.task-master.dev](https://docs.task-master.dev)

### 7.2 脚本位置

```
scripts/
├── auto-sync-to-taskmaster.py    # Spec-Kit → Taskmaster
├── auto-sync-to-hamster.py       # Taskmaster → Hamster
├── push-to-hamster.py            # 手动推送
└── tm-cli.py                     # CLI 工具
```

### 7.3 配置文件

```
.taskmaster/
└── tasks/
    └── tasks.json                # Taskmaster 数据

specs/
└── 001-learning-management/
    └── tasks.md                  # Spec-Kit 任务
```

---

## 附录

### A. 命令速查表

| 命令 | 用途 |
|------|------|
| `python3 scripts/auto-sync-to-taskmaster.py` | 单次同步 |
| `python3 scripts/auto-sync-to-taskmaster.py --watch` | 前台监听 |
| `python3 scripts/auto-sync-to-taskmaster.py --watch --daemon` | 后台监听 |
| `python3 scripts/auto-sync-to-hamster.py` | 单次推送 |
| `python3 scripts/auto-sync-to-hamster.py --watch` | 前台监听 |
| `python3 scripts/auto-sync-to-hamster.py --watch --daemon` | 后台监听 |
| `python3 scripts/tm-cli.py stats` | 查看统计 |
| `python3 scripts/tm-cli.py visualize` | 查看树形图 |
| `python3 scripts/tm-cli.py stats --format json` | JSON 输出 |

### B. 状态图标参考

| 图标 | 状态 |
|------|------|
| ⭕ | pending（待办） |
| 🔄 | in-progress（进行中） |
| ✅ | done（已完成） |
| 🚫 | blocked（阻塞） |
| ❌ | cancelled（已取消） |
| ⏸️ | deferred（延期） |
| 👀 | review（审查中） |

---

**文档维护**: 本指南由项目架构师维护，欢迎反馈建议。

**最后更新**: 2026-01-15
**文档维护者**: Claude Sonnet 4.5
**审核状态**: ✅ 已通过团队审核
