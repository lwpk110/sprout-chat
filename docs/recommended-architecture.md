# 推荐架构：优化后的 Taskmaster + Hamster 方案

**日期**: 2026-01-15
**状态**: 推荐
**相关 ADR**: [ADR-001](./adr-001-linear-eval.md)

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Spec-Kit (规范层)                         │
│  specs/001-learning-management/{spec.md, plan.md, tasks.md} │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ 自动同步（watchdog）
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                 Taskmaster AI (任务层)                       │
│  .taskmaster/tasks/tasks.json (本地 JSON, Git 版本控制)      │
│  - 元信息保留 (Phase, User Story, TDD 状态)                 │
│  - metadata 字段指向源文件                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ 自动推送（Webhook）
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Hamster (协作层)                          │
│  https://tryhamster.com/.../plan (远程协作平台)             │
│  - 团队协作                                                 │
│  - 进度可视化                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据流

### 1. Spec-Kit → Taskmaster (自动)

```bash
# scripts/auto-sync-to-taskmaster.py
from watchdog.observers import Observer

# 监听 specs/*/tasks.md 变化
observer.schedule(TaskmasterWatcher(), 'specs/', recursive=True)

# 自动解析并同步到 .taskmaster/tasks/tasks.json
```

**保留的元信息**：
```json
{
  "id": "LWP-2.2-T001",
  "title": "配置 Claude API 集成环境",
  "description": "...",
  "metadata": {
    "source": "speckit",
    "phase": "Phase 1",
    "user_story": "US1",
    "original_id": "T001",
    "file": "specs/001-learning-management/tasks.md",
    "commit_message": "[LWP-2.2-T001] feat: 配置 Claude API",
    "test_strategy": "TDD 绿灯阶段：运行 pytest 确认测试通过"
  }
}
```

### 2. Taskmaster → Hamster (自动)

```bash
# scripts/auto-sync-to-hamster.py
import time

# 监听 .taskmaster/tasks/tasks.json 变化
observer.schedule(HamsterWatcher(), '.taskmaster/tasks/', recursive=False)

# 自动生成 Markdown 并推送
# 1. 生成 Hamster Markdown 格式
# 2. 复制到剪贴板（xclip/pbcopy）
# 3. 发送通知到团队
```

**推送格式**：
```markdown
### LWP-2.2-T001: 配置 Claude API 集成环境

**状态**: ⏳ pending
**优先级**: 🔴 high
**Phase**: Phase 1
**User Story**: US1
**Commit**: `[LWP-2.2-T001] feat: 配置 Claude API`

**描述**:
配置 Claude API 集成环境，包括环境变量、依赖安装和密钥管理。

**测试策略**: TDD 绿灯阶段：运行 pytest 确认测试通过
```

---

## 开发工作流

### 1. 规范创建

```bash
# 1. 创建规范
/speckit.specify "学习管理系统"
→ 生成 specs/001-learning-management/spec.md

# 2. 分析规范
/speckit.analyze
→ ✅ 验证通过

# 3. 创建计划
/speckit.plan
→ 生成 specs/001-learning-management/plan.md

# 4. 生成任务
/speckit.tasks
→ 生成 specs/001-learning-management/tasks.md
```

### 2. 任务同步（自动）

```bash
# auto-sync-to-taskmaster.py 自动检测 tasks.md 变化
→ 同步到 .taskmaster/tasks/tasks.json
→ 保留 Spec-Kit 元信息
```

### 3. 任务执行

```bash
# 启动任务
tm autopilot start LWP-2.2-T001

# Red 阶段
vim tests/test_claude_api.py
pytest tests/test_claude_api.py  # ❌ 失败
git add tests/test_claude_api.py
git commit -m "[LWP-2.2-T001] test: 添加 Claude API 测试 (Red)"

# Green 阶段
vim backend/app/services/claude.py
pytest tests/test_claude_api.py  # ✅ 通过
git add backend/app/services/claude.py
git commit -m "[LWP-2.2-T001] feat: 实现 Claude API (Green)"

# 完成任务
tm autopilot complete LWP-2.2-T001
→ 状态更新为 done
→ 触发 Hamster 同步
```

### 4. 团队协作（自动）

```bash
# auto-sync-to-hamster.py 检测到 tasks.json 变化
→ 生成 Hamster Markdown
→ 复制到剪贴板
→ 发送通知：任务 LWP-2.2-T001 已完成
→ 团队成员粘贴到 Hamster
```

---

## 自动化脚本

### scripts/auto-sync-to-taskmaster.py

```python
#!/usr/bin/env python3
"""自动同步 Spec-Kit → Taskmaster"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time

class SpecKitWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('tasks.md'):
            print(f"[INFO] 检测到 Spec-Kit 任务变更: {event.src_path}")
            time.sleep(1)  # 等待文件写入完成
            subprocess.run(['python', 'scripts/speckit-to-taskmaster.py'])
            print("[SUCCESS] 已同步到 Taskmaster")

# 监听 specs/ 目录
observer = Observer()
observer.schedule(SpecKitWatcher(), 'specs/', recursive=True)
observer.start()

print("[INFO] Spec-Kit 监听已启动，按 Ctrl+C 停止")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

### scripts/auto-sync-to-hamster.py

```python
#!/usr/bin/env python3
"""自动同步 Taskmaster → Hamster"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import shutil

class TaskmasterWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('tasks.json'):
            print(f"[INFO] 检测到 Taskmaster 任务变更: {event.src_path}")
            time.sleep(1)

            # 1. 生成 Hamster Markdown
            subprocess.run(['python', 'scripts/taskmaster-to-hamster.py'])
            print("[SUCCESS] 已生成 Hamster Markdown")

            # 2. 自动复制到剪贴板
            hamster_md = '.taskmaster/docs/hamster-sync.md'
            with open(hamster_md, 'r') as f:
                content = f.read()

            if shutil.which('xclip'):
                subprocess.run(
                    ['xclip', '-selection', 'clipboard'],
                    input=content.encode('utf-8')
                )
                print("[SUCCESS] 已复制到剪贴板 (xclip)")

            # 3. 发送通知（可选）
            # subprocess.run(['notify-send', 'Hamster 同步完成'])

# 监听 .taskmaster/tasks/ 目录
observer = Observer()
observer.schedule(TaskmasterWatcher(), '.taskmaster/tasks/', recursive=False)
observer.start()

print("[INFO] Taskmaster 监听已启动，按 Ctrl+C 停止")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

---

## UI 增强

### tm visualize (任务树形图)

```bash
$ tm visualize --tree

LWP-2.2 (Phase 2.2: 学习管理系统)
├── T001: 配置 Claude API ✅
├── T002: 安装 Python 依赖 ✅
├── T003: 创建数据加密服务 ✅
├── US1: 学习记录
│   ├── T011: 编写测试 🔄 (in-progress)
│   ├── T012: 实现 API ⏳
│   └── T013: 学习追踪服务 ⏳
├── US2: 苏格拉底教学
│   ├── T021: 编写测试 ⏳
│   ├── T022: 错误分类器 ⏳
│   └── T023: 响应验证 ⏳
└── US3: 错题本
    ├── T031: 编写测试 ⏳
    └── T032: 推荐服务 ⏳

进度: 3/30 (10%)
```

### tm stats (进度统计)

```bash
$ tm stats

📊 Phase 2.2 学习管理系统 - 进度统计

总任务数: 30
已完成: 3 (10%)
进行中: 1 (3%)
待办: 26 (87%)

按优先级:
  🔴 高 (P0-P1): 20 个
  🟡 中 (P2): 10 个

按 User Story:
  US1 (学习记录): 12 个
  US2 (苏格拉底): 10 个
  US3 (错题本): 8 个

按 Phase:
  Phase 1: 3 个 (✅ 100%)
  Phase 2: 20 个 (🔄 15%)
  Phase 3: 7 个 (⏳ 0%)

TDD 状态:
  Red: 0
  Green: 3
  Refactor: 0
```

---

## 实施计划

### Phase 1: 自动化同步 (8-12 小时)

- [ ] 实现 `auto-sync-to-taskmaster.py`
  - [ ] 监听 `specs/*/tasks.md` 变化
  - [ ] 自动触发同步
  - [ ] 保留 Git Commit 集成

- [ ] 实现 `auto-sync-to-hamster.py`
  - [ ] 监听 `.taskmaster/tasks/tasks.json` 变化
  - [ ] 自动生成 Markdown
  - [ ] 自动复制到剪贴板
  - [ ] 发送通知

### Phase 2: UI 增强 (8-12 小时)

- [ ] 实现 `tm visualize` 命令
  - [ ] 树形图显示
  - [ ] 状态标记
  - [ ] 进度百分比

- [ ] 实现 `tm stats` 命令
  - [ ] 按优先级统计
  - [ ] 按 User Story 统计
  - [ ] 按 Phase 统计
  - [ ] TDD 状态统计

### Phase 3: 文档和培训 (4-8 小时)

- [ ] 更新 `docs/development-guide.md`
- [ ] 编写 `docs/taskmaster-best-practices.md`
- [ ] 创建 Ralph Loop + Taskmaster 教程
- [ ] 录制演示视频（可选）

---

## 成本效益

| 项目 | 工作量 | 收益 |
|------|--------|------|
| 自动化同步 | 8-12h | 消除手动同步，减少错误 |
| UI 增强 | 8-12h | 提升可视化，改善体验 |
| 文档培训 | 4-8h | 降低学习曲线，提高效率 |
| **总计** | **20-32h** | **高 ROI，低风险** |

---

## 对比 Linear

| 维度 | Taskmaster+Hamster | Linear |
|------|-------------------|--------|
| **成本** | 20-32h | 52-84h |
| **风险** | 低 | 高 |
| **Spec-Kit 元信息** | ✅ 原生支持 | ❌ 需自定义字段 |
| **TDD 循环** | ✅ testStrategy 字段 | ⚠️ 需 Labels |
| **本地优先** | ✅ JSON + Git | ❌ 云服务 |
| **可追溯性** | ✅ metadata.file | ❌ 无法追溯 |
| **项目宪章** | ✅ 完全兼容 | ❌ 不兼容 |

---

## 结论

优化后的 Taskmaster + Hamster 方案具有以下优势：

1. **成本更低**: 20-32h vs Linear 52-84h
2. **风险更小**: 无需重构，保持现有架构
3. **符合宪章**: 完全兼容项目宪章原则
4. **可渐进式**: 分阶段实施，可随时调整
5. **可逆性**: 可随时回退，无锁定风险

**推荐立即实施**。

---

**架构师**: Principal Architect (Claude Sonnet 4.5)
**日期**: 2026-01-15
**相关文档**:
- [ADR-001: Linear 迁移评估](./adr-001-linear-eval.md)
- [Linear 评估摘要](./linear-eval-summary.md)
