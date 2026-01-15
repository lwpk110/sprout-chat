# Spec-Kit 与 Taskmaster 同步指南

## 概述

本文档说明如何使用同步脚本将 Spec-Kit 生成的 `tasks.md` 同步到 Taskmaster，实现规范驱动的任务管理。

**核心价值**:
- ✅ 以 Spec-Kit 为源头（任务定义）
- ✅ Taskmaster 为执行层（进度追踪）
- ✅ 保留 Spec-Kit 元信息（Phase、用户故事、依赖）
- ✅ 双向状态同步（保留 Taskmaster 状态）

## 快速开始

### 一键同步

```bash
# 运行同步脚本
python3 scripts/speckit-to-taskmaster.py
```

**输出示例**:
```
======================================================================
Spec-Kit → Taskmaster 双向同步工具 v2.0
======================================================================

[步骤 1/4] 解析 Spec-Kit tasks.md
[SUCCESS] 已解析 34 个 Spec-Kit 任务

[步骤 2/4] 生成 Taskmaster 任务
[SUCCESS] 已生成 34 个 Taskmaster 任务

[步骤 3/4] 合并现有任务
[INFO] 保留任务状态: LWP-2.2-T001 -> pending
[SUCCESS] 已合并 34 个任务

[步骤 4/4] 保存到 Taskmaster
[SUCCESS] 已保存到 Taskmaster: .taskmaster/tasks/tasks.json

📄 同步报告: .taskmaster/docs/speckit-sync-report.md
```

## 任务 ID 映射规则

### Spec-Kit → Taskmaster

| Spec-Kit ID | Taskmaster ID | 说明 |
|-------------|---------------|------|
| `T001` | `LWP-2.2-T001` | Phase 2.2 的任务 T001 |
| `T012` | `LWP-2.2-T012` | Phase 2.2 的任务 T012 |

**格式**: `LWP-{Phase编号}-{T编号}`

## Spec-Kit 元信息保留

### 保留的元信息

| 元信息 | 存储位置 | 示例 |
|--------|----------|------|
| **Phase** | `tags`, `metadata.phase` | `"Phase-1"` |
| **User Story** | `tags`, `metadata.user_story` | `"US1"` |
| **原始 ID** | `metadata.original_id` | `"T001"` |
| **源文件** | `metadata.file` | `"/path/to/tasks.md"` |
| **TDD 标记** | `tags` | `"tdd"` |

### Taskmaster JSON 结构示例

```json
{
  "id": "LWP-2.2-T001",
  "title": "Claude API 集成环境",
  "description": "配置 Claude API 集成环境",
  "status": "pending",
  "priority": "high",
  "dependencies": [],
  "details": "**Phase**: Phase 1\n**Commit Message**: `[LWP-2.2-T001] feat: ...`\n**Source**: Spec-Kit tasks.md\n**Original ID**: T001",
  "testStrategy": "TDD 绿灯阶段：运行 pytest 确认测试通过",
  "tags": ["Phase-1", "tdd", "speckit"],
  "subtasks": [],
  "metadata": {
    "source": "speckit",
    "phase": "Phase 1",
    "user_story": null,
    "original_id": "T001",
    "file": "/path/to/specs/001-learning-management/tasks.md"
  }
}
```

## 同步策略

### 智能合并

脚本采用**智能合并策略**：

1. **首次同步**: 创建所有任务
2. **后续同步**: 保留 Taskmaster 中的任务状态
3. **增量更新**: 更新任务的 title、description 等字段
4. **状态保留**: `status` 字段始终保留 Taskmaster 的值

### 示例场景

**场景 1: 首次同步**
```
Spec-Kit: T001 (pending) → Taskmaster: LWP-2.2-T001 (pending) ✅
```

**场景 2: 状态已变更**
```
Spec-Kit: T001 (done) → Taskmaster: LWP-2.2-T001 (in-progress) ✅
                                     ↑ 保留 Taskmaster 状态
```

**场景 3: 依赖关系更新**
```
Spec-Kit: T002 依赖 T001 → Taskmaster: LWP-2.2-T002 依赖 LWP-2.2-T001 ✅
                              ↑ 自动转换 ID
```

## 完整工作流

### 开发流程

```bash
# 1. 编写 Spec-Kit 规范
/speckit.specify "实现学习管理系统"

# 2. 生成 Spec-Kit 任务
/speckit.tasks

# 3. 同步到 Taskmaster
python3 scripts/speckit-to-taskmaster.py

# 4. 查看同步报告
cat .taskmaster/docs/speckit-sync-report.md

# 5. 开始任务
tm autopilot start LWP-2.2-T001

# 6. 实施 TDD 开发
# Red → Green → Refactor

# 7. 完成任务
tm autopilot complete LWP-2.2-T001
```

### 验证同步结果

```bash
# 列出所有任务
tm list

# 查看任务详情（包含 Spec-Kit 元信息）
tm get LWP-2.2-T001

# 筛选特定 Phase 的任务
tm list | grep "Phase-1"

# 筛选特定用户故事的任务
tm list | grep "US1"
```

## 高级用法

### 1. 自定义 Phase 前缀

编辑 `scripts/speckit-to-taskmaster.py`:

```python
PHASE_PREFIX = "LWP-3.0"  # 修改为你的 Phase 编号
```

### 2. 筛选特定任务

```python
# 在脚本中修改
speckit_tasks = [t for t in parser.parse() if t.phase == "Phase 1"]
```

### 3. 批量操作

```bash
# 批量完成 Phase 1 的任务
for task in $(tm list | grep "LWP-2.2-T0[0-9]" | awk '{print $1}'); do
  tm autopilot complete $task
done
```

## 故障排查

### 问题 1: 同步后任务丢失

**原因**: Spec-Kit `tasks.md` 格式错误

**解决方案**:
```bash
# 1. 检查同步报告
cat .taskmaster/docs/speckit-sync-report.md

# 2. 查看脚本输出中的 [ERROR] 和 [WARNING]
python3 scripts/speckit-to-taskmaster.py 2>&1 | grep -E "\[ERROR\]|\[WARNING\]"

# 3. 验证 tasks.md 格式
# 确保每行格式：- [ ] T001 任务描述
```

### 问题 2: 任务 ID 冲突

**原因**: Taskmaster 中已存在相同 ID 的任务

**解决方案**:
- 脚本会**保留**现有任务的状态，不会覆盖
- 如需重置，手动删除 `.taskmaster/tasks/tasks.json` 中的对应任务

### 问题 3: 元信息丢失

**原因**: Taskmaster JSON 格式不兼容

**解决方案**:
```bash
# 检查 Taskmaster JSON 结构
jq '.["learning-management"].tasks[0].metadata' .taskmaster/tasks/tasks.json

# 应该看到 Spec-Kit 元信息
{
  "source": "speckit",
  "phase": "Phase 1",
  "original_id": "T001",
  ...
}
```

## Git Commit 格式

**推荐格式**（包含 Spec-Kit 和 Taskmaster ID）:

```bash
git commit -m "[LWP-2.2-T001][T001] feat: 配置 Claude API

- 添加 AI_PROVIDER、AI_MODEL 配置
- 测试 API 连接

Refs: LWP-2.2-T001, T001"
```

**格式说明**:
- `[LWP-2.2-T001]` - Taskmaster 任务 ID
- `[T001]` - Spec-Kit 任务 ID
- `Refs:` - 引用两个任务 ID

## 相关文档

- [Spec-Kit vs Taskmaster](./spec-vs-taskmaster.md) - 定位区别详解
- [项目宪章](../../.specify/memory/constitution.md) - ⚖️ 最高优先级
- [开发协议](../development/development-guide.md) - 🚦 TDD 自动化
- [任务管理计划](./task-management-plan.md) - Taskmaster 使用指南

## 维护者

- **脚本作者**: Claude (Sonnet 4.5)
- **文档维护**: PM Agent
- **最后更新**: 2026-01-15
- **版本**: 2.0.0

---

**状态**: ✅ 生产就绪
**测试**: 已验证 34 个任务同步
