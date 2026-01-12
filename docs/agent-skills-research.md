# Agent Skills 研究报告：小芽家教项目

## 1. 研究背景

根据 Anthropic 的 [Agent Skills 文档](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)，Agent Skills 是一种将专业领域知识打包成可复用、可组合的技能单元的方法。

### 1.1 Agent Skills 核心要素
- **SKILL.md**: 包含 YAML frontmatter（name, description）和详细指令
- **渐进式披露**: metadata → body → 额外资源文件
- **可包含代码**: 预写的脚本可供 Claude 执行

### 1.2 项目现状分析
小芽家教项目包含以下核心服务模块：

| 模块 | 文件 | 职责 | 可复用性 |
|------|------|------|----------|
| 对话引擎 | `engine.py` | AI 集成、会话管理 | ★★★ |
| 苏格拉底教学 | `socratic_teacher.py` | 引导式教学 | ★★★ |
| 教学策略 | `teaching_strategy.py` | 问题分类、策略选择 | ★★★ |
| 小芽人格 | `sprout_persona.py` | Prompt 模板 | ★★★ |
| 图像识别 | `vision.py` | OCR、题目提取 | ★★☆ |
| 学习追踪 | `learning_tracker.py` | 进度统计 | ★★☆ |
| 家长控制 | `parental_control.py` | 时间/内容控制 | ★★☆ |

---

## 2. 可抽象为 Agent Skills 的逻辑

### 2.1 TDD 开发流程 (高优先级)

**当前痛点**: TDD 流程复杂，需要频繁执行红-绿-重构循环

**可复用逻辑**:
- 测试文件命名规范
- pytest 执行模式
- git 提交时机
- 重构检查清单

**建议 Skill 结构**:
```
skills/
└── tdd-cycle/
    ├── SKILL.md          # TDD 流程指令
    ├── test-patterns.md  # 测试模式参考
    └── refactor-checklist.md
```

---

### 2.2 Git 提交规范 (高优先级)

**当前痛点**: 提交信息格式不统一，与 Taskmaster 关联易遗漏

**可复用逻辑**:
- Type 类型映射（feat/fix/docs/refactor）
- Task ID 提取规则
- Commit message 模板

**建议 Skill 结构**:
```
skills/
└── git-commit/
    ├── SKILL.md              # 提交规范
    └── commit-templates.md   # 各类提交模板
```

---

### 2.3 小芽人格 Prompt (核心业务)

**当前痛点**: 人格定义分散在多个文件

**可复用逻辑**:
- 温柔耐心的教学风格
- 具象比喻系统
- 苏格拉底式提问模板
- 一年级学生语言适配

**建议 Skill 结构**:
```
skills/
└── sprout-persona/
    ├── SKILL.md              # 人格定义
    ├── metaphors.md          # 比喻库
    ├── question-templates.md # 提问模板
    └── language-style.md     # 语言风格
```

---

### 2.4 教学策略选择 (核心业务)

**当前痛点**: 问题类型识别和策略选择逻辑复杂

**可复用逻辑**:
- 问题类型分类（加法/减法/应用题等）
- 关键短语匹配
- 策略模板选择
- 替代方案生成

**建议 Skill 结构**:
```
skills/
└── teaching-strategy/
    ├── SKILL.md              # 策略选择逻辑
    ├── problem-types.md      # 问题类型定义
    ├── strategy-templates.md # 策略模板
    └── metaphors.md          # 比喻资源
```

---

### 2.5 苏格拉底引导 (核心业务)

**当前痛点**: 引导类型与错误类型映射

**可复用逻辑**:
- 7 种引导类型（clarify/hint/break_down/visualize/check_work/alternative_method/encourage）
- 错误类型映射（calculation/concept/understanding/careless）
- 多次尝试策略升级

**建议 Skill 结构**:
```
skills/
└── socratic-teaching/
    ├── SKILL.md              # 引导逻辑
    ├── guidance-types.md     # 引导类型定义
    ├── error-mapping.md      # 错误-引导映射
    └── retry-strategy.md     # 重试策略
```

---

### 2.6 GitHub- Taskmaster 同步 (开发流程)

**当前痛点**: 容易遗漏同步步骤

**可复用逻辑**:
- Issue 创建 → Taskmaster 任务
- Issue 关闭 → 任务状态更新
- PR 合并 → 任务完成

**建议 Skill 结构**:
```
skills/
└── github-sync/
    ├── SKILL.md              # 同步规则
    └── sync-rules.md         # 详细规则
```

---

## 3. 建议实施的 Skills 优先级

| 优先级 | Skill 名称 | 预期收益 | 复杂度 |
|--------|-----------|----------|--------|
| P0 | `tdd-cycle` | 减少 TDD 流程错误 | 低 |
| P0 | `git-commit` | 提交信息规范化 | 低 |
| P1 | `sprout-persona` | 人格一致性保障 | 中 |
| P1 | `teaching-strategy` | 教学效果提升 | 中 |
| P1 | `socratic-teaching` | 引导质量提升 | 中 |
| P2 | `github-sync` | 流程自动化 | 低 |

---

## 4. SKILL.md 模板示例

### 4.1 TDD Cycle Skill

```markdown
---
name: tdd-cycle
description: Execute Test-Driven Development Red-Green-Refactor cycle for Python/FastAPI projects
---

# TDD Cycle Skill

## Overview
This skill enforces strict TDD discipline for SproutChat backend development.

## Red Phase (Write Failing Test)
1. Create test file in `backend/tests/`
2. Test must fail before implementation
3. Commit with message: `[TASK-ID] test: <description> (Red)`

## Green Phase (Minimal Implementation)
1. Write minimal code to pass test
2. No refactoring yet
3. Commit with message: `[TASK-ID] feat: <description> (Green)`

## Refactor Phase (Optional)
1. Improve code quality
2. Maintain test passing
3. Commit with message: `[TASK-ID] refactor: <description> (Refactor)`

## Verification
Always run `pytest` after each phase.
```

---

## 5. 实施建议

### 5.1 渐进式实施
1. **第一阶段**: 创建 `tdd-cycle` 和 `git-commit`（低风险、高频使用）
2. **第二阶段**: 创建业务相关 skills（`sprout-persona`, `teaching-strategy`）
3. **第三阶段**: 创建流程自动化 skills（`github-sync`）

### 5.2 验证方法
- 监控 Claude 使用 skills 的频率
- 观察任务完成质量变化
- 收集用户反馈

---

## 6. 参考资源

- [Agent Skills 官方文档](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Agent Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
- [Anthropic Engineering Blog](https://www.anthropic.com/engineering)

---

**报告生成日期**: 2026-01-12
**版本**: v1.0
