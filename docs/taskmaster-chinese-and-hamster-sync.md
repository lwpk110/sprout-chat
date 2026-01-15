# Task-Master 中文化与 Hamster 同步方案

**日期**: 2025-01-15
**问题**: Task-Master 生成的任务是英文，且无法自动同步到 Hamster

---

## 问题分析

### 1. Task-Master 中文问题

**现象**：
- 配置文件中设置了 `"responseLanguage": "Chinese"`
- 但 parse_prd 生成的任务仍然是英文

**原因**：
- Task-Master 的 parse_prd 功能可能不完全支持 responseLanguage 配置
- 或者需要重启/重新加载配置

**解决方案**：
- 创建翻译脚本，将英文任务翻译为中文
- 或者直接从 tasks.md 导入中文任务

### 2. Hamster 同步问题

**现象**：
- Task-Master 没有直接的 Hamster 集成
- 需要手动同步任务到 Hamster

**Hamster URL**：
- https://tryhamster.com/home/lwpk110s-team/briefs/226273bf-3756-4262-b47b-d8d0c51e9348/plan

**解决方案**：
- 方案 A：创建同步脚本，定期推送任务到 Hamster API
- 方案 B：手动导出/导入任务
- 方案 C：使用 GitHub Issues 作为中间层（Hamster 可能支持 GitHub 集成）

---

## 方案 A：创建中文任务脚本

### 步骤 1: 从 tasks.md 提取任务

```python
import re
import json
from pathlib import Path

# 读取 tasks.md
tasks_md = Path("specs/001-learning-management/tasks.md").read_text()

# 提取任务
pattern = r'- \[ \] (T\d+)(?: \[P\])?(?: \[US\d+\])?\s+(.+)'
matches = re.findall(pattern, tasks_md)

# 生成任务列表
tasks = []
for task_id, title in matches:
    task = {
        "id": task_id,
        "title": title,
        "status": "pending",
        "priority": "high" if "Setup" in title or "创建" in title else "medium"
    }
    tasks.append(task)

# 保存为 JSON
with open(".taskmaster/docs/chinese-tasks.json", "w", encoding="utf-8") as f:
    json.dump({"tasks": tasks}, f, ensure_ascii=False, indent=2)
```

### 步骤 2: 更新 Task-Master JSON

```python
import json
from pathlib import Path

# 读取当前 Task-Master 任务
with open(".taskmaster/tasks/tasks.json", "r", encoding="utf-8") as f:
    tm_tasks = json.load(f)

# 读取中文任务
with open(".taskmaster/docs/chinese-tasks.json", "r", encoding="utf-8") as f:
    cn_tasks = json.load(f)

# 更新 learning-management tag 的任务
tm_tasks["learning-management"]["tasks"] = cn_tasks["tasks"]

# 保存
with open(".taskmaster/tasks/tasks.json", "w", encoding="utf-8") as f:
    json.dump(tm_tasks, f, ensure_ascii=False, indent=2)
```

---

## 方案 B：Hamster 同步脚本

### Hamster API 集成（假设）

```python
import requests
import json
from pathlib import Path

class HamsterSync:
    """同步 Task-Master 任务到 Hamster"""

    def __init__(self, hamster_url: str, api_token: str):
        self.base_url = "https://tryhamster.com/api/v1"
        self.api_token = api_token
        self.brief_id = "226273bf-3756-4262-b47b-d8d0c51e9348"

    def get_tasks_from_taskmaster(self) -> list:
        """从 Task-Master 读取任务"""
        with open(".taskmaster/tasks/tasks.json", "r") as f:
            data = json.load(f)
        return data["learning-management"]["tasks"]

    def sync_to_hamster(self, tasks: list):
        """同步任务到 Hamster"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        for task in tasks:
            # 创建或更新 Hamster 任务
            payload = {
                "brief_id": self.brief_id,
                "title": task["title"],
                "description": task.get("details", ""),
                "status": task["status"],
                "priority": task["priority"]
            }

            response = requests.post(
                f"{self.base_url}/tasks",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                print(f"✅ 同步任务: {task['title']}")
            else:
                print(f"❌ 同步失败: {task['title']}")
                print(f"   错误: {response.text}")

    def run(self):
        """执行同步"""
        tasks = self.get_tasks_from_taskmaster()
        self.sync_to_hamster(tasks)

# 使用示例
if __name__ == "__main__":
    sync = HamsterSync(
        hamster_url="https://tryhamster.com",
        api_token="YOUR_HAMSTER_API_TOKEN"
    )
    sync.run()
```

---

## 方案 C：使用 GitHub Issues 作为中间层

### 优势

- Hamster 可能支持 GitHub 集成
- Task-Master 可以通过 GitHub MCP 同步
- 双向同步更可靠

### 实施步骤

1. **创建 GitHub Issues**
```bash
# 从 Task-Master 创建 GitHub Issues
gh issue create --title "T001: 配置 Claude API 集成环境" \
  --body "任务描述..." \
  --label "learning-management,P0"
```

2. **Hamster 订阅 GitHub Issues**
   - 在 Hamster 中配置 GitHub 仓库集成
   - 自动同步 Issues 到 Hamster Brief

3. **双向同步**
   - Task-Master → GitHub Issues → Hamster
   - Hamster 更新 → GitHub Issues → Task-Master

---

## 立即可用的解决方案

### 1. 创建中文任务 JSON

```bash
# 手动创建简化的中文任务 JSON
cat > .taskmaster/docs/learning-management-cn.json << 'EOF'
{
  "learning-management": {
    "tasks": [
      {
        "id": "T001",
        "title": "配置 Claude API 集成环境",
        "description": "在 backend/.env 添加 AI_PROVIDER、AI_MODEL、OPENAI_API_KEY、OPENAI_BASE_URL",
        "status": "pending",
        "priority": "high",
        "dependencies": []
      },
      {
        "id": "T002",
        "title": "安装 Python 依赖包",
        "description": "添加 anthropic (Claude SDK) 和 cryptography (AES-256 加密) 到 requirements.txt",
        "status": "pending",
        "priority": "high",
        "dependencies": ["T001"]
      }
      // ... 更多任务
    ]
  }
}
EOF
```

### 2. 手动同步到 Hamster

```bash
# 方式 1: 导出为 Markdown，手动复制到 Hamster
python scripts/export_tasks_to_markdown.py

# 方式 2: 使用 Hamster CLI（如果支持）
hamster sync --source .taskmaster/tasks/tasks.json \
  --brief 226273bf-3756-4262-b47b-d8d0c51e9348

# 方式 3: 通过 GitHub Issues 中转
gh issue import tasks.csv
```

---

## 下一步行动

### 短期（今天）

1. ✅ 创建中文任务 JSON
2. ✅ 替换 Task-Master 中的英文任务
3. ✅ 导出任务为 Markdown 格式
4. ⏳ 手动复制到 Hamster（或寻找 API）

### 中期（本周）

1. 研究 Hamster API 文档
2. 创建自动同步脚本
3. 设置定期同步任务

### 长期（本月）

1. 实现双向同步
2. 添加冲突解决机制
3. 集成到 task-manager skill

---

## 需要您提供

1. **Hamster API Token**（如果支持 API）
2. **Hamster Brief ID**：226273bf-3756-4262-b47b-d8d0c51e9348
3. **同步频率**：实时？每小时？每天？
4. **同步方向**：单向（Task-Master → Hamster）还是双向？

---

**作者**: Claude Sonnet 4.5
**版本**: 1.0
**状态**: 待实施
