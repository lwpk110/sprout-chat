# Taskmaster → Hamster 同步指南

## 概述

本文档说明如何将本地 Taskmaster 任务同步到 Hamster (tryhamster.com)。

**核心价值**:
- ✅ 自动生成 Hamster Markdown 格式
- ✅ 保留 Spec-Kit 元信息（Phase、用户故事）
- ✅ 自动复制到剪贴板（Linux/macOS/Windows）
- ✅ 支持一键同步

## 快速开始

### 方法 1: 一键同步（推荐）

```bash
# 运行一键同步脚本
./scripts/sync-all.sh
```

**输出示例**:
```
======================================================================
🚀 一键同步：Spec-Kit → Taskmaster → Hamster
======================================================================

[步骤 1/2] 同步 Spec-Kit → Taskmaster
[SUCCESS] 已同步 34 个任务

[步骤 2/2] 同步 Taskmaster → Hamster
[SUCCESS] 已生成 12555 字符的 Markdown
[BONUS] ✅ 已自动复制到剪贴板 (xclip)

✅ 同步完成！
```

### 方法 2: 仅同步到 Hamster

```bash
# 只运行 Hamster 导出脚本
python3 scripts/taskmaster-to-hamster.py
```

## 复制到 Hamster

### 自动复制（已支持）

脚本会**自动复制**到剪贴板：
- ✅ **Linux**: 使用 `xclip`
- ✅ **macOS**: 使用 `pbcopy`
- ✅ **Windows**: 使用 `clip`

**粘贴到 Hamster**:
1. 打开 Hamster: https://tryhamster.com/home/lwpk110s-team/briefs/226273bf-3756-4262-b47b-d8d0c51e9348/plan
2. 粘贴内容: `Ctrl+V` (Linux/Windows) 或 `Cmd+V` (macOS)

### 手动复制（备选方案）

如果自动复制不可用：

#### Linux (使用 xclip)
```bash
cat .taskmaster/docs/hamster-sync.md | xclip -selection clipboard
```

#### macOS (使用 pbcopy)
```bash
cat .taskmaster/docs/hamster-sync.md | pbcopy
```

#### Windows (使用 clip)
```bash
cat .taskmaster/docs/hamster-sync.md | clip
```

#### 手动复制粘贴
1. 打开文件: `cat .taskmaster/docs/hamster-sync.md`
2. 全选复制: `Ctrl+Shift+A` (终端)
3. 打开 Hamster 网页粘贴

## Hamster Markdown 格式

### 文件结构

生成的 Markdown 包含以下部分：

```
# Phase 2.2 学习管理系统任务清单

## 📋 任务概览
- 总任务数
- 按优先级统计

## 🔴 高优先级任务 (P0-P1)
### LWP-2.2-T001: 任务标题
**描述**: ...
**状态**: ⏳ pending
**详情**: ...
**元信息**:
- **Phase**: Phase 1
- **原始 ID**: T001

## 🟡 中优先级任务 (P2)
...

## 📊 进度统计
- 按状态统计
- 按优先级统计
- 按 Phase 统计

## 🔗 相关链接
...
```

### 包含的信息

| 字段 | 说明 | 示例 |
|------|------|------|
| **任务 ID** | Taskmaster ID | `LWP-2.2-T001` |
| **标题** | 任务标题 | `Claude API 集成环境` |
| **描述** | 任务描述 | `配置 Claude API 集成环境` |
| **状态** | 任务状态 | `⏳ pending` |
| **详情** | Spec-Kit 元信息 | Phase, Commit Message, Source |
| **测试策略** | TDD 测试策略 | `TDD 绿灯阶段...` |
| **依赖** | 依赖关系 | `LWP-2.2-T002` |
| **元信息** | Spec-Kit 元信息 | Phase, User Story, 原始 ID |
| **标签** | 任务标签 | `Phase-1`, `tdd`, `speckit` |

## 完整工作流

### 开发 → 同步 → Hamster

```bash
# 1. 开发任务
tm autopilot start LWP-2.2-T001
# ... TDD 开发 ...
tm autopilot complete LWP-2.2-T001

# 2. 同步到 Hamster
./scripts/sync-all.sh

# 3. 粘贴到 Hamster
# - 脚本已自动复制到剪贴板
# - 打开 Hamster 网页
# - Ctrl+V 粘贴

# 4. 更新 Hamster 任务状态
# - 在 Hamster 网页上勾选完成的任务
```

## 高级用法

### 1. 自定义 Hamster URL

编辑 `scripts/taskmaster-to-hamster.py`:

```python
HAMSTER_URL = "https://tryhamster.com/home/your-team/briefs/your-brief-id/plan"
```

### 2. 筛选特定任务

编辑脚本，添加筛选逻辑：

```python
# 只同步高优先级任务
high_priority = [t for t in self.tasks if t.get("priority") == "high"]

# 只同步特定 Phase
phase_1_tasks = [t for t in self.tasks if "Phase-1" in t.get("tags", [])]
```

### 3. 定制 Markdown 格式

修改 `_format_task()` 方法：

```python
def _format_task(self, task: Dict) -> List[str]:
    # 自定义格式
    lines = [
        f"## {task['id']}",  # 改为二级标题
        f"- **{task['title']}**",
        # ...
    ]
```

## 故障排查

### 问题 1: 自动复制不工作

**原因**: 系统缺少剪贴板工具

**解决方案**:
```bash
# Linux: 安装 xclip
sudo apt-get install xclip

# macOS: pbcopy 已内置

# Windows: clip 已内置
```

### 问题 2: Hamster Markdown 格式错误

**原因**: 任务数据格式异常

**解决方案**:
```bash
# 检查 Taskmaster JSON
jq '.["learning-management"].tasks[0]' .taskmaster/tasks/tasks.json

# 验证生成的 Markdown
cat .taskmaster/docs/hamster-sync.md | head -50
```

### 问题 3: 任务数量不匹配

**原因**: Taskmaster JSON 中有多个 tag

**解决方案**:
- 脚本会**合并所有 tag** 的任务
- 查看同步统计确认任务数量
- 检查是否有重复任务

## 最佳实践

### 1. 定期同步

**建议同步时机**:
- 任务状态变更后
- Phase 开始前
- 里程碑完成后

### 2. 版本控制

**提交生成的 Markdown**:
```bash
git add .taskmaster/docs/hamster-sync.md
git commit -m "[LWP-2.2] chore: 同步任务到 Hamster"
```

### 3. 团队协作

**同步流程**:
1. 本地开发 → 更新 Taskmaster
2. 运行同步脚本 → 生成 Markdown
3. 复制到 Hamster → 团队查看
4. 在 Hamster 讨论任务 → 反馈到本地

## 相关文档

| 文档 | 用途 |
|------|------|
| `scripts/taskmaster-to-hamster.py` | Hamster 导出脚本 |
| `scripts/sync-all.sh` | 一键同步脚本 |
| `docs/speckit-taskmaster-sync.md` | Spec-Kit 同步指南 |
| `.taskmaster/docs/hamster-sync.md` | 生成的 Hamster Markdown |

## Hamster 链接

**团队 Brief**: https://tryhamster.com/home/lwpk110s-team/briefs/226273bf-3756-4262-b47b-d8d0c51e9348/plan

## 维护者

- **脚本作者**: Claude (Sonnet 4.5)
- **文档维护**: PM Agent
- **最后更新**: 2026-01-15
- **版本**: 1.0.0

---

**状态**: ✅ 生产就绪
**自动复制**: ✅ Linux/macOS/Windows
**测试**: 已验证 34 个任务同步
