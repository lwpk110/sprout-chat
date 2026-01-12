---
name: git-commit
description: 定义小芽家教项目的 Git 提交规范，包含 Type 类型、任务关联和原子提交原则。
---

# Git 提交技能

## 核心原则

### 原子提交
> **每次提交仅包含一个逻辑变更，禁止批量提交。**

### 正确示例
```bash
git add backend/app/api/conversations.py
git commit -m "[LWP-1] 实现会话创建 API"
```

### 错误示例
```bash
git add .
git commit -m "LWP-1 完成"  # 违反原子提交原则
```

---

## 提交信息格式

```
[TYPE](任务ID): 简短描述

详细说明（可选）
- 完成项 1
- 完成项 2

Refs: 任务ID
```

---

## TYPE 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加用户注册功能` |
| `fix` | Bug 修复 | `fix: 修复会话超时问题` |
| `docs` | 文档更新 | `docs: 更新 API 文档` |
| `refactor` | 代码重构 | `refactor: 优化对话引擎` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖版本` |

---

## 任务关联
- 所有提交必须附带对应的 Task ID
- Task ID 格式：`LWP-X`（如 LWP-1）

---

## 相关技能
- `tdd-cycle` - TDD 开发流程
- `github-sync` - GitHub 和 Taskmaster 同步
