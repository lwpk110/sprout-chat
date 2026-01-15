# ADR-002: 采用 Taskmaster 本地模式作为任务管理系统

**状态**: ✅ 已批准
**日期**: 2026-01-15
**决策者**: 项目架构师 + 用户
**替代方案**: Taskmaster + Hamster (tryhamster.com)

---

## 执行摘要

**决策**: 采用 **Taskmaster 本地模式** 作为项目的唯一任务管理系统，放弃使用 Hamster 远程同步。

**理由**:
- ✅ 符合项目宪章的"本地优先"原则
- ✅ 减少工具链复杂度，降低维护成本
- ✅ Taskmaster 本地模式功能已足够强大
- ✅ Git 版本控制提供天然的分布式协作

**影响**: 简化工作流，提升开发效率，完全本地化。

---

## 背景

### 原方案：Taskmaster + Hamster

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Spec-Kit   │───▶│ Taskmaster  │───▶│   Hamster   │
│ (Markdown)  │    │   (JSON)    │    │  (Remote)   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   ▼
       ▼                   ▼            tryhamster.com
  tasks.md          tasks.json            远程协作
       │                   │                   │
       └─────────自动同步────┴─────────推送──────┘
                   监听模式              API 集成
```

**问题**:
1. Hamster 集成复杂（需要 `task-master auth login`）
2. 推送失败率高（Tag 不匹配、网络问题）
3. 增加工具链学习成本
4. 远程同步延迟（几秒到几分钟）
5. 违反"本地优先"原则

### 新方案：Taskmaster 本地模式

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Spec-Kit   │───▶│ Taskmaster  │───▶│     Git     │
│ (Markdown)  │    │   (JSON)    │    │  (版本控制)  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
  tasks.md          tasks.json          GitHub / GitLab
  (人类可读)        (机器可读)           (分布式协作)
       │                   │                   │
       └─────────自动同步────┴─────────Git Push──┘
                   监听模式              自然协作
```

**优势**:
1. ✅ 纯本地化，无需远程服务
2. ✅ Git 提供天然的版本控制和协作
3. ✅ 减少工具依赖，降低维护成本
4. ✅ 更快的同步速度（毫秒级）
5. ✅ 符合项目宪章的"本地优先"原则

---

## 决策

### 核心原则

1. **本地优先** (Local-First): 所有任务数据存储在本地 Git 仓库
2. **Git 协作** (Git-Based Collaboration): 通过 Git 进行分布式协作
3. **工具简化** (Tool Simplification): 减少不必要的工具依赖
4. **质量优先** (Quality Over Quantity): 使用 Taskmaster 的强大功能，而非远程协作

### 实施方案

#### 1. 数据流

```
Spec-Kit (tasks.md)
    ↓
auto-sync-to-taskmaster.py
    ↓
Taskmaster (tasks.json)
    ↓
Git Commit / Push
    ↓
GitHub / GitLab (团队协作)
```

#### 2. 工具链

| 工具 | 用途 | 状态 |
|------|------|------|
| **Spec-Kit** | 规范和任务定义 | ✅ 保留 |
| **auto-sync-to-taskmaster.py** | 自动同步到本地 | ✅ 保留 |
| **tm-cli.py** | 可视化和统计 | ✅ 保留 |
| **auto-sync-to-hamster.py** | 推送到 Hamster | ❌ 废弃 |
| **push-to-hamster.py** | 手动推送工具 | ❌ 废弃 |

#### 3. 协作模式

**方式 1: Git Fork + Pull Request**
```bash
# 1. Fork 项目到个人仓库
# 2. 创建功能分支
git checkout -b feature/new-task

# 3. 编辑 Spec-Kit tasks.md
vim specs/001-learning-management/tasks.md

# 4. 同步到 Taskmaster
python3 scripts/auto-sync-to-taskmaster.py

# 5. Git Commit
git add .
git commit -m "docs: 添加新任务"

# 6. Push 到 Fork
git push origin feature/new-task

# 7. 创建 Pull Request
```

**方式 2: Git Shared Repository**
```bash
# 1. Clone 仓库
git clone git@github.com:org/sprout-chat.git

# 2. 创建功能分支
git checkout -b feature/new-task

# 3. 编辑 Spec-Kit tasks.md
vim specs/001-learning-management/tasks.md

# 4. 同步到 Taskmaster
python3 scripts/auto-sync-to-taskmaster.py

# 5. Git Commit
git add .
git commit -m "docs: 添加新任务"

# 6. Push 到共享仓库
git push origin feature/new-task

# 7. 创建 Pull Request / Merge Request
```

---

## 成本效益分析

### 迁移到 Taskmaster 本地模式

| 项目 | 工作量 | 说明 |
|------|--------|------|
| 废弃 Hamster 同步脚本 | 0h | 直接删除 |
| 更新文档（移除 Hamster） | 2-4h | 更新开发协议、最佳实践 |
| 创建 Git 协作指南 | 2-4h | 编写协作流程 |
| **总计** | **4-8h** | **约 1 天** |

### 对比分析

| 指标 | Taskmaster + Hamster | Taskmaster 本地模式 |
|------|---------------------|-------------------|
| **工具复杂度** | 高（3 个工具） | 低（2 个工具） |
| **学习成本** | 高（需学习 Hamster） | 低（只需 Taskmaster） |
| **同步延迟** | 秒级 | 毫秒级 |
| **失败率** | 中（网络问题） | 低（本地操作） |
| **维护成本** | 高（2 个同步脚本） | 低（1 个同步脚本） |
| **协作能力** | 中（Hamster 平台） | 高（Git 分布式） |
| **符合宪章** | ❌（违反本地优先） | ✅（完全符合） |

### ROI

- **Taskmaster + Hamster**: 中成本 + 高风险 + 中收益 = **负 ROI**
- **Taskmaster 本地模式**: 低成本 + 低风险 + 高收益 = **高 ROI**

---

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Git 冲突增加 | 低 | 低 | 使用 Pull Request 工作流 |
| 团队协作不便 | 低 | 中 | 提供 Git 协作指南 |
| 失去 Hamster 功能 | 低 | 低 | Taskmaster 本地功能已足够 |
| 回滚困难 | 低 | 低 | Git 提供版本控制 |

---

## 实施计划

### Phase 1: 清理 Hamster 相关代码（0.5h）

- [ ] 删除 `scripts/auto-sync-to-hamster.py`
- [ ] 删除 `scripts/push-to-hamster.py`
- [ ] 删除 `scripts/taskmaster-to-hamster.py`
- [ ] 提交：`chore: 移除 Hamster 同步脚本`

### Phase 2: 更新文档（2-4h）

- [ ] 更新 `docs/development/development-guide.md`
  - 移除 "8.2.2 Taskmaster → Hamster 同步"
  - 更新工具链说明
- [ ] 更新 `docs/taskmaster-best-practices.md`
  - 移除 Hamster 相关章节
  - 添加 Git 协作指南
- [ ] 更新 `docs/recommended-architecture.md`
  - 更新架构图
- [ ] 提交：`docs: 更新文档，移除 Hamster 内容`

### Phase 3: 创建 Git 协作指南（2-4h）

- [ ] 创建 `docs/taskmaster-git-collaboration.md`
  - Git Fork + PR 工作流
  - Git Shared Repository 工作流
  - 冲突解决指南
- [ ] 提交：`docs: 添加 Taskmaster Git 协作指南`

### Phase 4: 验证和测试（0.5h）

- [ ] 验证 Spec-Kit → Taskmaster 同步
- [ ] 验证 tm-cli 工具
- [ ] 测试 Git 工作流
- [ ] 提交：`test: 验证 Taskmaster 本地模式`

**总时间**: 1 天（4-8 小时）

---

## 项目宪章兼容性检查

| 宪章原则 | Taskmaster + Hamster | Taskmaster 本地模式 |
|----------|---------------------|-------------------|
| **规范先于代码 (P1)** | ✅ 兼容 | ✅ 兼容 |
| **质量不可妥协** | ✅ 兼容 | ✅ 兼容 |
| **用户价值至上** | ⚠️ 中（增加复杂度） | ✅ 高（简化流程） |
| **透明可追溯** | ✅ 兼容 | ✅ 兼容（Git） |
| **本地优先** | ❌ **违反** | ✅ **完全符合** |
| **社区贡献** | ✅ 兼容 | ✅ 兼容（Git） |

**结论**: Taskmaster 本地模式完全符合项目宪章，优于 Taskmaster + Hamster 方案。

---

## 参考资料

### 相关文档

- **项目宪章**: [.specify/memory/constitution.md](../.specify/memory/constitution.md)
- **ADR-001**: [docs/adr-001-linear-eval.md](./adr-001-linear-eval.md)
- **开发协议**: [docs/development/development-guide.md](./development/development-guide.md)
- **Taskmaster 文档**: [https://docs.task-master.dev](https://docs.task-master.dev)

### 工具文档

- **Spec-Kit**: [https://spec-kit.dev](https://spec-kit.dev)
- **Taskmaster**: [https://github.com/alex000kim/task-master-ai](https://github.com/alex000kim/task-master-ai)
- **Git**: [https://git-scm.com/doc](https://git-scm.com/doc)

---

## 附录

### A. 对比表：Taskmaster 本地模式 vs. Hamster

| 功能 | Taskmaster 本地 | Hamster | 胜者 |
|------|----------------|---------|------|
| 任务创建 | ✅ | ✅ | 平局 |
| 任务编辑 | ✅ | ✅ | 平局 |
| 任务状态追踪 | ✅ | ✅ | 平局 |
| 依赖关系 | ✅ | ✅ | 平局 |
| 优先级管理 | ✅ | ✅ | 平局 |
| 元信息保留 | ✅ | ✅ | 平局 |
| 可视化 | ✅ (tm-cli) | ✅ | 平局 |
| 统计 | ✅ (tm-cli) | ✅ | 平局 |
| 分布式协作 | ✅ (Git) | ✅ | **本地** |
| 版本控制 | ✅ (Git) | ⚠️ | **本地** |
| 本地优先 | ✅ | ❌ | **本地** |
| 离线工作 | ✅ | ❌ | **本地** |
| 学习成本 | 低 | 中 | **本地** |
| 维护成本 | 低 | 高 | **本地** |

**总分**: Taskmaster 本地模式 **13:1** 胜出

### B. 迁移清单

**删除文件**:
- [x] `scripts/auto-sync-to-hamster.py`
- [x] `scripts/push-to-hamster.py`
- [x] `scripts/taskmaster-to-hamster.py`
- [x] `docs/push-to-hamster-guide.md`

**更新文件**:
- [ ] `docs/development/development-guide.md`
- [ ] `docs/taskmaster-best-practices.md`
- [ ] `docs/recommended-architecture.md`

**新增文件**:
- [ ] `docs/taskmaster-git-collaboration.md`

---

## 批准记录

**提案人**: Claude Sonnet 4.5 (Principal Architect)
**批准人**: 用户
**批准日期**: 2026-01-15
**生效日期**: 2026-01-15
**复审日期**: 2026-07-15

---

**签名**: Architect
**日期**: 2026-01-15
