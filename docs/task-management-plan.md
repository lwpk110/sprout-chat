# 小芽家教任务管理重构方案

**日期**: 2025-01-15
**状态**: 待决策

---

## 问题分析

### 当前状况

1. **Task-Master 架构**
   - 支持多个 tag/context
   - master context：本地文件（中文测试数据）
   - LWP context：同步到 Hamster（英文 PRD 任务）

2. **问题点**
   - LWP 任务显示 100% 完成，但项目还在开发
   - LWP 任务从旧 PRD 生成，与当前 Spec-Kit 规范不对应
   - 任务与规范脱节，无法有效追踪进度

3. **Hamster 集成**
   - URL: https://tryhamster.com/home/lwpk110s-team/briefs/226273bf-3756-4262-b47b-d8d0c51e9348/plan
   - LWP 任务已同步到 Hamster
   - 可能有多人协作，删除任务需要谨慎

---

## 解决方案对比

### 方案 A：保守策略（推荐 ⭐⭐⭐⭐⭐）

**核心思路**：创建新 tag，保留 LWP 任务作为历史记录

#### 优点
- ✅ 安全：不影响 Hamster 上的现有任务
- ✅ 可追溯：保留 LWP 任务作为历史参考
- ✅ 灵活：可以同时管理多个 tag
- ✅ 低风险：不会破坏团队协作

#### 缺点
- ⚠️ 需要切换 tag 查看不同阶段的任务
- ⚠️ 初期可能混淆（LWP vs learning-management）

#### 实施步骤

```bash
# 1. 创建新 tag（使用 Task-Master MCP）
tm --tag=learning-management init

# 2. 从 Spec-Kit 导入任务
# 读取 specs/001-learning-management/tasks.md
# 自动创建任务到 learning-management tag

# 3. 配置默认 tag
# 在 .taskmaster/config.json 设置 defaultTag=learning-management

# 4. 验证任务
tm --tag=learning-management list
```

#### 任务结构

```
learning-management tag:
├── LWP-2.2-T001: 配置 Claude API 集成环境
├── LWP-2.2-T002: 安装 Python 依赖包
├── LWP-2.2-T003: 创建数据加密服务
├── LWP-2.2-T004: 创建学习记录扩展模型
├── LWP-2.2-T005: 创建错题记录模型
├── ...
└── LWP-2.2-T030: 集成测试与验证
```

---

### 方案 B：激进策略（需要确认）

**核心思路**：清空 LWP tag，重建任务

#### 优点
- ✅ 简洁：只有一个任务 tag
- ✅ 一致：任务与规范完全对应

#### 缺点
- ❌ 高风险：可能影响 Hamster 团队协作
- ❌ 不可逆：删除后无法恢复（除非 Hamster 有版本控制）
- ❌ 需要确认：需要与团队确认是否可以删除 LWP 任务

#### 实施步骤

```bash
# 1. 确认团队意见
# 检查 Hamster 上是否有人在使用 LWP 任务

# 2. 备份（如果可能）
# 导出 LWP 任务到 JSON

# 3. 清空 LWP tag
tm --tag=LWP clear

# 4. 从 Spec-Kit 重新导入
# 读取 specs/001-learning-management/tasks.md
# 创建任务到 LWP tag

# 5. 同步到 Hamster
# 自动或手动同步
```

---

## 推荐方案：方案 A

### 理由

1. **安全性**
   - 不影响 Hamster 上的现有协作
   - 保留 LWP 任务作为里程碑记录
   - 可以随时对比新旧任务

2. **灵活性**
   - 可以同时管理多个阶段
   - 未来可以创建 "frontend-student-ui" tag
   - 每个 spec 对应一个 tag

3. **可追溯性**
   - LWP 任务记录了 MVP 阶段的工作
   - learning-management 记录 Phase 2.2 的工作
   - 清晰的项目演进历史

---

## 实施计划

### Phase 1: 创建新 tag（5分钟）

```bash
# 使用 Task-Master MCP
mcp__task-master-ai__parse_prd({
  input: "specs/001-learning-management/tasks.md",
  projectRoot: "/home/luwei/workspace/github/sprout-chat",
  tag: "learning-management",
  force: true
})
```

### Phase 2: 实现任务领取机制（2-3小时）

#### 数据结构

```typescript
interface TaskClaim {
  taskId: string;
  agentId: string;        // backend-dev-1, backend-dev-2...
  claimedAt: Date;
  status: 'claimed' | 'in-progress' | 'done' | 'released';
  heartbeat?: Date;       // 心跳时间，用于检测僵尸任务
}
```

#### API 设计

```bash
# 1. 领取任务
tm claim LWP-2.2-T001 --agent=backend-dev-1

# 2. 释放任务
tm release LWP-2.2-T001 --agent=backend-dev-1

# 3. 更新状态
tm set-status LWP-2.2-T001 in-progress

# 4. 查看可领取任务
tm list --status=pending --unclaimed
```

### Phase 3: 文档编写（1小时）

- 任务管理使用指南
- 并行开发最佳实践
- Agent 协作流程

---

## 下一步

### 待确认事项

1. ✅ 是否采用方案 A（保守策略）？
2. ❓ Hamster 上的 LWP 任务是否还有人使用？
3. ❓ 是否需要同步到 Hamster，还是仅本地管理？

### 立即行动

请确认选择方案 A 还是方案 B，我将立即开始执行。

---

**作者**: Claude Sonnet 4.5
**版本**: 1.0
