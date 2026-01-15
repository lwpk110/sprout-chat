# ADR-001: 评估 Linear 替换 Taskmaster+Hamster 的可行性

**状态**: 已提议
**日期**: 2026-01-15
**决策者**: Principal Architect (Claude Sonnet 4.5)
**相关文档**: [docs/task-management-plan.md](../docs/task-management-plan.md)

---

## 上下文

### 当前架构

项目当前使用三层任务管理架构：

```
Spec-Kit (Markdown 规范)
    ↓
Taskmaster AI (JSON 本地任务)
    ↓
Hamster (远程协作平台)
```

**自动化脚本**：
- `scripts/speckit-to-taskmaster.py` - Spec-Kit → Taskmaster 双向同步
- `scripts/taskmaster-to-hamster.py` - Taskmaster → Hamster Markdown 导出
- `scripts/push-to-hamster.py` - Taskmaster CLI 批量推送到 Hamster

### 问题点

1. **任务脱节**: LWP 任务显示 100% 完成，但实际开发还在进行
2. **同步链路冗长**: Spec-Kit → Taskmaster → Hamster，三个环节
3. **工具碎片化**: 需要维护三个系统的一致性
4. **协作限制**: Hamster 需要手动复制粘贴 Markdown

### 迁移动机

简化任务管理架构，减少同步链路，提升开发效率。

---

## 决策

**不建议迁移到 Linear，继续使用 Taskmaster + Hamster 方案。**

---

## 原因

### 1. Linear 能力评估

#### 优势

| 特性 | Linear | 说明 |
|------|--------|------|
| **GraphQL API** | ✅ | 灵活查询，官方维护 |
| **TypeScript SDK** | ✅ | `@linear/sdk` npm 包，类型安全 |
| **Webhooks** | ✅ | 支持 Issues, Comments, Projects 等事件推送 |
| **批量导入** | ✅ | 支持 Jira, GitHub, Asana 等直接导入 |
| **自定义字段** | ⚠️ | 需通过 CLI 或 API 扩展，非原生支持 |

#### API 能力

```graphql
# Linear GraphQL API 示例
mutation createIssue {
  issueCreate(
    input: {
      title: "实现 OCR 服务"
      description: "集成 PaddleOCR..."
      teamId: "TEAM_ID"
      # ⚠️ 无原生 Spec-Kit 元数据字段
    }
  ) {
    issue {
      id
      title
      # 需要通过自定义字段存储 Phase, User Story
    }
  }
}
```

#### 关键限制

1. **无原生 Spec-Kit 元信息支持**
   - Phase (Phase 1, Phase 2)
   - User Story (US1, US2)
   - Commit Message
   - TDD 信息 (Red/Green 标记)

2. **自定义字段需额外开发**
   - 需要通过 CLI Importer 或 API 创建自定义字段
   - 无 `metadata` 字段，需存储在 Description 或 Labels
   - 标签系统与 Spec-Kit 元数据映射复杂

3. **批量导入限制**
   - 官方 Importer 支持的工具：Jira, GitHub, Asana, Shortcut, Linear
   - 通用 CSV 导入需要手动格式化，无法直接转换 Spec-Kit Markdown
   - 导入后无法保留 Spec-Kit 的层级结构 (Phase → User Story → Task)

---

### 2. 迁移可行性分析

#### 技术可行性：中等（30%）

| 维度 | 评分 | 说明 |
|------|------|------|
| API 能力 | ⭐⭐⭐⭐ | GraphQL API 完善，SDK 丰富 |
| 批量导入 | ⭐⭐ | 无 Spec-Kit 直接导入，需开发转换器 |
| 自定义字段 | ⭐⭐ | 需通过 API 创建，存储在 Description/Labels |
| Webhook 集成 | ⭐⭐⭐⭐ | 支持实时同步 |
| 本地优先 | ⭐ | Linear 是云服务，非本地优先 |

#### 阻断因素

1. **Spec-Kit 元信息保留**
   ```json
   // Taskmaster JSON 格式（当前）
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

   Linear 无 `metadata` 字段，需通过以下方式模拟：
   - **Labels**: `phase-1`, `us1`, `speckit` - 导致标签爆炸
   - **Description**: 在 Markdown 前言添加元信息 - 难以查询
   - **自定义字段**: 需通过 API 创建，增加复杂度

2. **TDD 红绿重构循环集成**
   - Taskmaster 支持 `testStrategy` 字段，标记 TDD 阶段
   - Linear 需通过 Labels 或 Description 标记，无法自动化检查

3. **Git Commit 集成**
   - Taskmaster 自动生成 Commit Message 格式
   - Linear 需通过 Webhook 或自定义脚本集成

4. **本地优先 vs 云服务**
   - Taskmaster 是本地 JSON，Git 版本控制
   - Linear 是云服务，需 API 访问，增加网络依赖

---

### 3. 成本效益分析

#### 迁移成本

| 项目 | 工作量 | 说明 |
|------|--------|------|
| **Spec-Kit → Linear 转换器** | 16-24 小时 | 解析 tasks.md，映射 Linear API |
| **自定义字段设计** | 8-12 小时 | 设计 Phase, User Story, TDD 字段 |
| **Webhook 集成** | 8-12 小时 | 同步状态变更到本地 |
| **Git Commit 集成** | 4-8 小时 | 修改 `tdd-cycle` skill |
| **测试与调试** | 8-12 小时 | 端到端测试 |
| **文档编写** | 4-8 小时 | 更新开发协议 |
| **团队培训** | 4-8 小时 | 学习 Linear API |
| **总计** | **52-84 小时** | 约 1.5-2.5 周 |

#### 收益分析

| 收益 | 量化 | 说明 |
|------|------|------|
| 减少同步链路 | 节省 2 个环节 | Spec-Kit → Linear（vs Spec-Kit → Taskmaster → Hamster） |
| UI 友好度 | ⭐⭐⭐⭐ vs ⭐⭐ | Linear UI 更现代 |
| 团队协作 | ⭐⭐⭐⭐ | 内置评论、@提及、通知 |
| API 丰富度 | ⭐⭐⭐⭐ vs ⭐⭐⭐ | Linear API 更强大 |
| 本地控制 | ⭐⭐ vs ⭐⭐⭐⭐ | Linear 云服务，无本地控制 |

#### ROI（投资回报率）

- **成本**: 52-84 小时
- **收益**: 节省 2 个同步环节，但增加 API 集成复杂度
- **净收益**: 负值（成本 > 收益）

---

### 4. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **Spec-Kit 元信息丢失** | 高 | 高 | 通过自定义字段保留（增加复杂度） |
| **TDD 流程集成失败** | 中 | 中 | 修改 `tdd-cycle` skill 支持 Linear |
| **API 配额限制** | 低 | 中 | Linear 未公开配额，需确认 |
| **团队学习曲线** | 中 | 低 | 编写文档和培训 |
| **回滚困难** | 高 | 高 | 无官方 Linear → Taskmaster 导出工具 |

---

### 5. 与项目宪章的兼容性

#### 宪章要求

1. **规范先于代码 (P1)**: Spec-Kit 规范是核心，任务管理必须保留规范元信息
2. **质量不可妥协**: TDD 红绿重构循环必须可追踪
3. **透明可追溯**: 所有任务必须追溯到规范文件
4. **本地优先**: 项目采用 Git 版本控制，任务数据应 Git 友好

#### Linear 兼容性

| 宪章原则 | Linear 兼容性 | 说明 |
|----------|---------------|------|
| 规范先于代码 | ⚠️ 部分兼容 | 需通过自定义字段保留 Spec-Kit 元信息 |
| 质量不可妥协 | ⚠️ 部分兼容 | TDD 信息需通过 Labels 或 Description 标记 |
| 透明可追溯 | ❌ 不兼容 | Linear 无 `metadata` 字段，难以追溯到源文件 |
| 本地优先 | ❌ 不兼容 | Linear 是云服务，任务数据不在 Git 版本控制 |

---

## 后果

### 正面影响

无（不建议迁移）

### 负面影响（如果迁移）

1. **增加技术债务**
   - 需维护 Spec-Kit → Linear 转换器
   - 自定义字段管理复杂度
   - Webhook 集成稳定性依赖 Linear 服务

2. **降低可追溯性**
   - Linear 任务无法直接追溯到 `specs/*/tasks.md`
   - 元信息分散在 Labels/Description/自定义字段
   - Git Commit 集成需额外开发

3. **增加成本**
   - Linear 可能收费（未公开定价）
   - API 调用延迟
   - 团队学习成本

---

## 替代方案

### 方案 A：优化 Taskmaster + Hamster（推荐 ⭐⭐⭐⭐⭐）

**核心思路**: 保持现有架构，优化同步链路

#### 优化措施

1. **自动化 Hamster 同步**
   ```bash
   # 使用 Webhook 自动推送任务更新
   scripts/auto-sync-to-hamster.py --watch --daemon
   ```

2. **改进 Taskmaster UI**
   - 添加 `tm visualize` 命令，生成任务树形图
   - 集成 `tm stats` 命令，显示进度统计

3. **增强 Spec-Kit 集成**
   - 添加 `scripts/speckit-sync-watch.py`，监听 tasks.md 变化
   - 自动触发 Taskmaster 同步

4. **文档优化**
   - 编写 Taskmaster 最佳实践
   - 创建 Ralph Loop + Taskmaster 使用指南

#### 成本

| 项目 | 工作量 |
|------|--------|
| Hamster 自动同步 | 8-12 小时 |
| Taskmaster UI 优化 | 8-12 小时 |
| 文档编写 | 4-8 小时 |
| **总计** | **20-32 小时** |

#### 收益

- ✅ 保留 Spec-Kit 元信息
- ✅ 本地优先，Git 版本控制
- ✅ 低成本，低风险
- ✅ 兼容项目宪章

---

### 方案 B：迁移到 GitHub Issues（备选 ⭐⭐⭐）

**核心思路**: 利用 GitHub Issues 和 Projects

#### 优势

1. **原生 Git 集成**
   - Issues 与 Commit/PR 关联
   - 自动更新任务状态
   - 内置 Markdown 支持

2. **无需额外工具**
   - 无需 Taskmaster
   - 无需 Hamster
   - 团队已熟悉 GitHub

3. **开源友好**
   - 适合开源项目
   - 社区贡献者友好

#### 劣势

1. **无 Spec-Kit 元信息支持**
   - 需通过 Labels 或 Issues Templates 模拟
   - 无法自动同步 `specs/*/tasks.md`

2. **UI 复杂度**
   - GitHub Projects 学习曲线
   - 无专用任务管理功能

#### 迁移成本

| 项目 | 工作量 |
|------|--------|
| Spec-Kit → GitHub 转换器 | 16-24 小时 |
| Issues Templates 设计 | 8-12 小时 |
| Projects 配置 | 4-8 小时 |
| 文档编写 | 4-8 小时 |
| **总计** | **32-52 小时** |

---

## 推荐方案

### 最终决策：方案 A - 优化 Taskmaster + Hamster

**理由**：

1. **成本最低**: 20-32 小时 vs Linear 52-84 小时
2. **风险最小**: 无需重构现有架构
3. **兼容宪章**: 保留 Spec-Kit 元信息，本地优先
4. **渐进式**: 可逐步优化，无需一次性迁移

### 实施计划

#### Phase 1: 自动化 Hamster 同步（8-12 小时）

```python
# scripts/auto-sync-to-hamster.py
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TaskmasterWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('tasks.json'):
            print("[INFO] 检测到任务变更，同步到 Hamster...")
            subprocess.run(['python', 'scripts/taskmaster-to-hamster.py'])
            # 自动复制到剪贴板
            # 发送通知到团队

# 监听 .taskmaster/tasks/tasks.json
observer = Observer()
observer.schedule(TaskmasterWatcher(), '.taskmaster/tasks/', recursive=False)
observer.start()
```

#### Phase 2: Taskmaster UI 优化（8-12 小时）

```bash
# tm visualize 命令
tm visualize --tree
# 输出：
# LWP-2.2 (Phase 2.2)
# ├── T001: 配置 Claude API ✅
# ├── T002: 安装依赖 ✅
# └── US1: 学习记录
#     ├── T011: 编写测试 🔄
#     └── T012: 实现 API ⏳
```

#### Phase 3: 文档和培训（4-8 小时）

- [ ] 更新 `docs/development-guide.md`
- [ ] 编写 `docs/taskmaster-best-practices.md`
- [ ] 创建 Ralph Loop + Taskmaster 教程

---

## 参考资料

### Linear API 文档

- [Linear Developers](https://linear.app/developers)
- [API and Webhooks](https://linear.app/docs/api-and-webhooks)
- [Importer](https://linear.app/docs/import-issues)
- [Linear API Schema](https://studio.apollography.com/public/Linear-API/variant/current/schema)

### 对比文章

- [Jira vs Linear vs GitHub Issues in 2025](https://medium.com/@samurai.stateless.coder/jira-vs-linear-vs-github-issues-in-2025-what-real-web-dev-teams-actually-use-and-why-d808740317e6)
- [Compare GitHub vs. Linear](https://www.g2.com/compare/github-vs-linear)
- [Why Linear is the best task management tool for devs](https://www.linkedin.com/posts/alexandre-zajac_softwareengineering-productivity-programming-activity-7357069115653517312-oWHQ)

### 项目文档

- [docs/task-management-plan.md](../docs/task-management-plan.md)
- [CLAUDE.md](../CLAUDE.md)
- [.specify/memory/constitution.md](../.specify/memory/constitution.md)

---

## 决策记录

| 日期 | 决策 | 决策者 | 理由 |
|------|------|--------|------|
| 2026-01-15 | 不迁移到 Linear | Principal Architect | 成本 > 收益，违反宪章原则 |

---

**签名**: Principal Architect (Claude Sonnet 4.5)
**生效日期**: 2026-01-15
**复审日期**: 2026-07-15（6 个月后）
