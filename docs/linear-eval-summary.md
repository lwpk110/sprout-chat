# Linear 迁移可行性评估 - 执行摘要

**日期**: 2026-01-15
**决策者**: Principal Architect
**决策**: **不建议迁移到 Linear**
**完整报告**: [docs/adr-001-linear-eval.md](./adr-001-linear-eval.md)

---

## 执行摘要

经过全面调研 Linear API、成本效益分析和风险评估，**不建议将当前任务管理系统从 Taskmaster+Hamster 迁移到 Linear**。

### 关键发现

| 维度 | Linear vs Taskmaster+Hamster |
|------|----------------------------|
| **迁移成本** | 52-84 小时（1.5-2.5 周） |
| **优化现有方案** | 20-32 小时（1 周内） |
| **Spec-Kit 元信息** | ❌ 无原生支持，需自定义字段 |
| **TDD 循环集成** | ⚠️ 需通过 Labels/Description 模拟 |
| **本地优先** | ❌ 云服务，非 Git 版本控制 |
| **项目宪章兼容性** | ❌ 违反 P1（规范先于代码） |

---

## Linear 能力评估

### ✅ 优势

1. **GraphQL API** - 官方维护，灵活查询
2. **TypeScript SDK** - `@linear/sdk` npm 包，类型安全
3. **Webhooks** - 实时事件推送
4. **批量导入** - 支持 Jira, GitHub, Asana 等

### ❌ 关键限制

1. **无 Spec-Kit 元信息支持**
   - Phase (Phase 1, Phase 2)
   - User Story (US1, US2)
   - Commit Message
   - TDD 状态 (Red/Green)

2. **自定义字段需额外开发**
   - 无 `metadata` 字段
   - 需通过 Labels 或 Description 存储
   - 标签爆炸风险

3. **无 Spec-Kit 直接导入**
   - 需开发 Markdown → Linear 转换器
   - 无法保留层级结构

---

## 成本效益分析

### 迁移到 Linear

| 项目 | 工作量 |
|------|--------|
| Spec-Kit → Linear 转换器 | 16-24h |
| 自定义字段设计 | 8-12h |
| Webhook 集成 | 8-12h |
| Git Commit 集成 | 4-8h |
| 测试与调试 | 8-12h |
| 文档编写 | 4-8h |
| 团队培训 | 4-8h |
| **总计** | **52-84h** |

### 优化现有方案

| 项目 | 工作量 |
|------|--------|
| Hamster 自动同步 | 8-12h |
| Taskmaster UI 优化 | 8-12h |
| 文档编写 | 4-8h |
| **总计** | **20-32h** |

### ROI 对比

- **Linear 迁移**: 高成本（52-84h）< 中收益
- **优化现有方案**: 低成本（20-32h）> 中收益

**结论**: 优化现有方案的 ROI 显著更高。

---

## 风险评估

| 风险 | 概率 | 影响 | 说明 |
|------|------|------|------|
| Spec-Kit 元信息丢失 | 高 | 高 | Linear 无 metadata 字段 |
| TDD 流程集成失败 | 中 | 中 | 需修改 tdd-cycle skill |
| API 配额限制 | 低 | 中 | Linear 未公开配额 |
| 团队学习曲线 | 中 | 低 | 新 API 和工具链 |
| **回滚困难** | **高** | **高** | **无 Linear → Taskmaster 导出工具** |

---

## 推荐方案

### 方案 A：优化 Taskmaster + Hamster ⭐⭐⭐⭐⭐

**核心思路**: 保持现有架构，自动化同步链路

#### 优化措施

1. **自动化 Hamster 同步**
   ```bash
   # 监听 tasks.json 变化，自动推送
   scripts/auto-sync-to-hamster.py --watch --daemon
   ```

2. **Taskmaster UI 增强**
   - `tm visualize` - 任务树形图
   - `tm stats` - 进度统计

3. **文档优化**
   - Taskmaster 最佳实践
   - Ralph Loop 集成指南

#### 成本: 20-32 小时
#### 风险: 低
#### 兼容性: ✅ 符合宪章

---

### 方案 B：迁移到 GitHub Issues ⭐⭐⭐

**备选方案**，适合开源项目

#### 优势

- ✅ 原生 Git 集成
- ✅ 无需额外工具
- ✅ 社区友好

#### 劣势

- ❌ 无 Spec-Kit 元信息支持
- ❌ 需 Labels 模拟 Phase/US
- ❌ UI 复杂度

#### 成本: 32-52 小时

---

## 项目宪章兼容性检查

### 宪章要求

1. **规范先于代码 (P1)**
2. **质量不可妥协** - TDD 红-绿-重构循环
3. **透明可追溯** - 任务追溯到规范
4. **本地优先** - Git 版本控制

### Linear 兼容性

| 原则 | 兼容性 | 说明 |
|------|--------|------|
| 规范先于代码 | ⚠️ 部分兼容 | 需自定义字段保留元信息 |
| 质量不可妥协 | ⚠️ 部分兼容 | TDD 信息需 Labels 标记 |
| 透明可追溯 | ❌ 不兼容 | 无法追溯到 `specs/*/tasks.md` |
| 本地优先 | ❌ 不兼容 | 云服务，数据不在 Git |

### Taskmaster 兼容性

| 原则 | 兼容性 | 说明 |
|------|--------|------|
| 规范先于代码 | ✅ 完全兼容 | `metadata` 字段保留规范 |
| 质量不可妥协 | ✅ 完全兼容 | `testStrategy` 字段支持 TDD |
| 透明可追溯 | ✅ 完全兼容 | `file` 字段指向源文件 |
| 本地优先 | ✅ 完全兼容 | JSON 文件，Git 版本控制 |

**结论**: Taskmaster 完全符合项目宪章，Linear 不符合。

---

## 最终决策

### 不建议迁移到 Linear

**理由**：

1. **成本 > 收益** - 52-84h 迁移成本，收益有限
2. **违反宪章** - 不符合本地优先和可追溯性原则
3. **高风险** - 回滚困难，Spec-Kit 元信息丢失风险
4. **有更优方案** - 优化现有方案只需 20-32h

### 推荐行动

1. **立即**: 开始方案 A 实施
   - 编写 Hamster 自动同步脚本
   - 增强 Taskmaster UI
   - 更新文档

2. **短期** (1-2 周):
   - 完成自动化同步
   - 测试和优化
   - 团队培训

3. **长期** (6 个月后):
   - 复审决策
   - 评估新的需求
   - 考虑 GitHub Issues（如开源）

---

## 下一步

请确认是否批准**方案 A - 优化 Taskmaster + Hamster**，我将立即开始实施。

---

## 参考资料

- **完整 ADR**: [docs/adr-001-linear-eval.md](./adr-001-linear-eval.md)
- **Linear API**: [https://linear.app/developers](https://linear.app/developers)
- **Linear Importer**: [https://linear.app/docs/import-issues](https://linear.app/docs/import-issues)
- **对比文章**: [Jira vs Linear vs GitHub Issues](https://medium.com/@samurai.stateless.coder/jira-vs-linear-vs-github-issues-in-2025-what-real-web-dev-teams-actually-use-and-why-d808740317e6)

---

**报告作者**: Principal Architect (Claude Sonnet 4.5)
**日期**: 2026-01-15
**签名**: Architect
