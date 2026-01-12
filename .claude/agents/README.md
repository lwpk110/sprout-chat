# Sub-Agents 配置

本目录包含小芽家教项目的自定义 Sub-Agents 配置。

## 角色列表

| Agent | 文件 | 职责 |
|-------|------|------|
| PM | [pm.md](pm.md) | 项目经理：任务分发、进度跟踪、Issue 闭环 |
| Librarian | [librarian.md](librarian.md) | 馆长：规范维护、需求分析、合规验证 |
| Backend Dev | [backend-dev.md](backend-dev.md) | 后端开发：FastAPI、Python、AI 集成 |
| Frontend Dev | [frontend-dev.md](frontend-dev.md) | 前端开发：React、Tailwind CSS |
| QA | [qa.md](qa.md) | 质量保障：测试设计、红绿测试、覆盖率验证 |
| SRE | [sre.md](sre.md) | 运维专家：环境配置、Docker、CI/CD |

## 使用方法

在对话中通过 `@agent-name` 调用：
- `@pm 分发一个新任务`
- `@librarian 审查这个规范`
- `@backend-dev 实现用户认证`

## 配置格式

每个 Agent 配置包含：
- `name`: Agent 名称
- `description`: 职责描述
- `skills`: 关联的 Skills
- System Prompt: 详细指令

---

创建日期: 2026-01-12
