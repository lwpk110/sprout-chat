{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "TASK_MASTER_TOOLS": "core",
        "OPENAI_API_KEY": "2571fdfd899a4224a2ed97c6e9c6978b.Pk8x9c4nrtIitnWv",
        "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/"
      }
    }
  }
}

----
指令： “请更新 CLAUDE.md，增加一个 Git Version Control 章节，明确以下策略：

原子化提交：禁止大批量修改后一次性提交。每完成一个独立的功能点（如：创建一个 API 路由、修复一个逻辑 Bug、更新一个文档）必须立即提交。

关联任务：每个 Commit Message 必须以 feat(task-1): 或 fix(task-2): 这种格式开头，关联 Taskmaster 的 ID。

预检查：在 Git Commit 之前，必须确保代码没有明显的语法错误。

强制执行：除非我明确要求，否则在完成 Taskmaster 的每个子步骤后，请主动执行提交，无需询问我。”
---
