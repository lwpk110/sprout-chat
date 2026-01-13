# 个人笔记

## 历史指令记录

### Git 版本控制规范指令

**指令内容：**
```
请更新 CLAUDE.md，增加一个 Git Version Control 章节，明确以下策略：

原子化提交：禁止大批量修改后一次性提交。每完成一个独立的功能点（如：创建一个 API 路由、修复一个逻辑 Bug、更新一个文档）必须立即提交。

关联任务：每个 Commit Message 必须以 feat(task-1): 或 fix(task-2): 这种格式开头，关联 Taskmaster 的 ID。

预检查：在 Git Commit 之前，必须确保代码没有明显的语法错误。

强制执行：除非我明确要求，否则在完成 Taskmaster 的每个子步骤后，请主动执行提交，无需询问我。
```

**执行结果：**
该指令已执行，相关内容已整合到 `CLAUDE.md` 的 "Git 版本控制规范" 章节（第 5 节）。

---

## MCP 配置说明

### Taskmaster MCP 配置

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "TASK_MASTER_TOOLS": "core",
        "OPENAI_API_KEY": "*** (已移除敏感信息) ***",
        "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/"
      }
    }
  }
}
```

**说明：**
- Taskmaster 使用智谱 GLM API
- API Key 已从本文档移除，请查看环境变量或配置文件
- Base URL 必须设置为智谱 API 地址

---

**最后更新**: 2026-01-13
**原始文件**: Note.md (根目录)
