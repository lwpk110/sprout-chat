---
description: 守门人 - 检查开发流程前置条件，确保遵循项目宪章和规范驱动开发流程
---

# Gatekeeper Skill - 守门人

## 职责

确保所有开发类 Agent（Architect, Backend Dev, Frontend Dev, Dev）在开始工作前满足前置条件，防止违反项目宪章 P1（规范先于代码）。

## 核心原则

- **规范先于代码**：没有规范不设计架构，不编写代码
- **流程可追溯**：所有工作都能追溯到规范和任务
- **质量不可妥协**：确保测试覆盖率和 TDD 流程

## 检查逻辑

### 1. Architect Agent 前置条件

**检查项**：
- ✅ 存在对应的 Spec-Kit 规范文档（`specs/*/spec.md`）
- ✅ 规范必须通过 `/speckit.analyze` 验证
- ✅ 规范状态为 `Approved` 或 `In Planning`（非 `Draft`）

**拒绝条件**：
```bash
if [ ! -f "specs/*/spec.md" ]; then
  return REJECT_NO_SPEC
fi

if ! /speckit.analyze &>/dev/null; then
  return REJECT_SPEC_NOT_VALIDATED
fi
```

---

### 2. Backend/Frontend/Dev Agent 前置条件

**检查项**：
- ✅ 存在规范文档（`specs/*/spec.md`）
- ✅ 存在实施计划（`specs/*/plan.md`）
- ✅ 存在任务清单（`specs/*/tasks.md`）
- ✅ Taskmaster 中有对应的任务处于 `in-progress` 状态
- ✅ （前端额外）存在 UI 设计稿或交互说明

**拒绝条件**：
```bash
missing_files=()

if [ ! -f "specs/*/spec.md" ]; then
  missing_files+=("规范文档 (spec.md)")
fi

if [ ! -f "specs/*/plan.md" ]; then
  missing_files+=("实施计划 (plan.md)")
fi

if [ ! -f "specs/*/tasks.md" ]; then
  missing_files+=("任务清单 (tasks.md)")
fi

if ! tm list | grep -q "in-progress"; then
  missing_files+=("Taskmaster 任务 (in-progress)")
fi

if [ ${#missing_files[@]} -gt 0 ]; then
  return REJECT_MISSING_PREREQUISITES
fi
```

---

## 拒绝消息模板

### 模板 1: Architect Agent 拒绝消息

```markdown
## ⚠️ 架构设计请求被拒绝

**原因**：项目宪章要求"规范先于代码"（Constitution P1），当前缺少对应的规范文档。

**缺失项**：
- [ ] 规范文档（specs/*/spec.md）
- [ ] 规范通过 /speckit.analyze 验证

**正确流程**：
1. 创建规范：`/speckit.specify "功能描述"`
2. 分析规范：`/speckit.analyze`
3. 创建计划：`/speckit.plan`（此步骤会自动调用 Architect）
4. 生成任务：`/speckit.tasks`

**参考文档**：
- 项目宪章：`.specify/memory/constitution.md`
- Agent 调用顺序：`CLAUDE.md` → "Agent 调用顺序规范" 章节

请先完成规范创建，然后 Architect 将很乐意为您提供架构设计服务。
```

---

### 模板 2: Backend Dev Agent 拒绝消息

```markdown
## ⚠️ 后端开发请求被拒绝

**原因**：项目宪章要求"规范先于代码"（Constitution P1），当前缺少必要的前置条件。

**缺失项**：
- [ ] 规范文档（specs/*/spec.md）
- [ ] 实施计划（specs/*/plan.md）
- [ ] 任务清单（specs/*/tasks.md）
- [ ] Taskmaster 任务处于 in-progress 状态

**正确流程**：
1. 创建规范：`/speckit.specify "功能描述"`
2. 分析规范：`/speckit.analyze`
3. 创建计划：`/speckit.plan`
4. 生成任务：`/speckit.tasks`
5. 启动任务：`tm set-status --id=XXX --status=in-progress`
6. 开始开发：遵循 TDD 循环

请先完成上述步骤，然后 Backend Dev 将很乐意为您实现功能。
```

---

### 模板 3: Frontend Dev Agent 拒绝消息

```markdown
## ⚠️ 前端开发请求被拒绝

**原因**：项目宪章要求"规范先于代码"（Constitution P1），当前缺少必要的前置条件。

**缺失项**：
- [ ] 规范文档（specs/*/spec.md）
- [ ] 实施计划（specs/*/plan.md）
- [ ] 任务清单（specs/*/tasks.md）
- [ ] UI 设计稿或交互说明
- [ ] Taskmaster 任务处于 in-progress 状态

**正确流程**：
1. 创建规范：`/speckit.specify "功能描述"`
2. 分析规范：`/speckit.analyze`
3. 创建计划：`/speckit.plan`（包含 UI 设计）
4. 生成任务：`/speckit.tasks`
5. 启动任务：`tm set-status --id=XXX --status=in-progress`
6. 开始开发：遵循 TDD 循环

请先完成上述步骤，然后 Frontend Dev 将很乐意为您实现界面。
```

---

### 模板 4: Dev Agent 拒绝消息

```markdown
## ⚠️ 开发请求被拒绝

**原因**：项目宪章要求"规范先于代码"（Constitution P1），当前缺少必要的前置条件。

**缺失项**：
- [ ] 规范文档（specs/*/spec.md）
- [ ] 实施计划（specs/*/plan.md）
- [ ] 任务清单（specs/*/tasks.md）
- [ ] 架构决策记录（ADR）或 UI 设计稿
- [ ] Taskmaster 任务处于 in-progress 状态

**正确流程**：
1. 创建规范：`/speckit.specify "功能描述"`
2. 分析规范：`/speckit.analyze`
3. 创建计划：`/speckit.plan`（此步骤会生成 ADR）
4. 生成任务：`/speckit.tasks`
5. 启动任务：`tm set-status --id=XXX --status=in-progress`
6. 开始开发：遵循 TDD 循环

请先完成上述步骤，然后 Dev 将很乐意为您实现功能。
```

---

## 使用方式

### 在 Agent 中调用 Gatekeeper

```python
# architect.md 工作流程开始
## 工作流程

接收需求（来自 product-strategy）
    ↓
**调用 gatekeeper 检查前置条件**
    ↓
[检查失败] → 拒绝请求并返回引导消息
    ↓
[检查通过] → 继续架构设计
    ↓
分析技术约束与需求
    ↓
设计架构方案（包含 trade-off 分析）
    ↓
输出 ADR 和架构图
    ↓
与 product-strategy 确认
    ↓
交给 PM / dev 实施
    ↓
审查实现是否符合架构
```

---

## 配置选项

### 可自定义的检查项

```yaml
# 未来可以在项目中自定义
gatekeeper:
  strict_mode: true  # 严格模式：任何缺失都拒绝
  allow_bypass: false  # 是否允许绕过（需要特殊权限）
  log_all_requests: true  # 记录所有请求日志
  notification_channel: "team-chat"  # 拒绝时发送通知
```

---

## 测试用例

### 测试 1: Architect 无规范请求

```bash
# 输入
@gatekeeper check --agent=architect --feature="voice-service"

# 预期输出
❌ 检查失败：未找到规范文档 specs/voice-service/spec.md

# 建议操作
请先执行：/speckit.specify "voice-service"
```

---

### 测试 2: Backend Dev 缺少任务

```bash
# 输入
@gatekeeper check --agent=backend-dev --feature="user-auth"

# 预期输出
❌ 检查失败：缺少以下前置条件
- [x] 规范文档 (specs/user-auth/spec.md) ✅
- [x] 实施计划 (specs/user-auth/plan.md) ✅
- [x] 任务清单 (specs/user-auth/tasks.md) ✅
- [ ] Taskmaster 任务处于 in-progress 状态 ❌

# 建议操作
请先执行：tm set-status --id=XXX --status=in-progress
```

---

### 测试 3: Frontend Dev 完整前置条件

```bash
# 输入
@gatekeeper check --agent=frontend-dev --feature="chat-ui"

# 预期输出
✅ 检查通过
- [x] 规范文档 (specs/chat-ui/spec.md) ✅
- [x] 实施计划 (specs/chat-ui/plan.md) ✅
- [x] 任务清单 (specs/chat-ui/tasks.md) ✅
- [x] UI 设计稿 (specs/chat-ui/design.md) ✅
- [x] Taskmaster 任务 LWP-5.2 (in-progress) ✅

# 结果
Frontend Dev 可以开始工作
```

---

## 扩展性

### 添加新的检查规则

```python
# 未来可以轻松添加
def check_custom_rules(agent_type, feature):
    if agent_type == "backend-dev":
        # 检查数据库迁移脚本
        if not exists_migration_script(feature):
            return REJECT_NO_MIGRATION

    if agent_type == "frontend-dev":
        # 检查可访问性规范
        if not exists_a11y_doc(feature):
            return REJECT_NO_A11Y_DOC

    return CHECK_PASS
```

---

## 维护指南

### 更新检查逻辑

1. **修改 SKILL.md** - 更新检查项或拒绝消息
2. **更新相关 Agent** - 确保调用最新的 gatekeeper
3. **测试验证** - 运行测试用例确保逻辑正确
4. **更新文档** - 同步更新 CLAUDE.md 和 AGENT_FLOW_VALIDATION.md

---

## 版本历史

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|---------|------|
| 1.0.0 | 2025-01-14 | 初始版本，定义基础检查逻辑 | Claude |

---

**签名**: Gatekeeper v1.0.0
**生效日期**: 2025-01-14
