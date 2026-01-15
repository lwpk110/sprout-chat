# SproutChat Agent Skills

本目录包含小芽家教项目的 Agent Skills，用于扩展 Claude 的能力。

## Skills 列表

| Skill | 说明 | 分配给 |
|-------|------|--------|
| [tdd-cycle](tdd-cycle/) | TDD 红-绿-重构循环 | backend-dev, frontend-dev, qa |
| [git-commit](git-commit/) | Git 提交规范 | backend-dev, frontend-dev, qa |
| [sprout-persona](sprout-persona/) | 小芽人格定义 | frontend-dev |
| [teaching-strategy](teaching-strategy/) | 教学策略选择 | - |
| [socratic-teaching](socratic-teaching/) | 苏格拉底引导 | - |
| [github-sync](github-sync/) | GitHub-Taskmaster 同步 | - |
| [using-git-worktrees](using-git-worktrees/) | Git Worktrees 隔离工作空间 | backend-dev, frontend-dev, qa |

## 目录结构

```
.claude/skills/
├── tdd-cycle/SKILL.md
├── git-commit/SKILL.md
├── sprout-persona/SKILL.md
├── teaching-strategy/SKILL.md
├── socratic-teaching/SKILL.md
├── github-sync/SKILL.md
├── using-git-worktrees/SKILL.md
└── README.md
```

## 使用方法

Skills 在 Claude Code 启动时自动加载。当对话内容匹配 Skill 的描述时，Claude 会自动应用相应的 Skill。

## 添加新 Skill

1. 在 `.claude/skills/` 下创建新目录
2. 添加 `SKILL.md` 文件，包含 YAML frontmatter 和说明
3. 参考 [Claude 官方文档](https://code.claude.com/docs/en/skills)

---

创建日期: 2026-01-12
