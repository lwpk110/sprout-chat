# Quick Start: Phase 2.2 学习管理系统

**Feature**: 小芽家教 Phase 2.2 学习管理系统
**Branch**: `001-learning-management`
**Date**: 2025-01-12

## 概述

本文档提供 Phase 2.2 学习管理系统的快速开始指南，包括开发环境设置、核心 API 使用示例和常见问题解答。

---

## 前置条件

### 必需软件

- **Python**: 3.11+
- **PostgreSQL**: 14+ (生产环境) / SQLite (开发环境)
- **FastAPI**: 0.104+
- **SQLAlchemy**: 2.0+
- **Anthropic API Key**: 用于 Claude API 调用

### 环境变量配置

在 `backend/.env` 文件中配置以下环境变量：

```bash
# AI Provider
AI_PROVIDER=openai
AI_MODEL=claude-3.5-sonnet
OPENAI_API_KEY=your_anthropic_api_key_here
OPENAI_BASE_URL=https://api.anthropic.com

# Database (开发环境使用 SQLite)
DATABASE_URL=sqlite:///./sproutchat.db

# Database (生产环境使用 PostgreSQL)
# DATABASE_URL=postgresql://user:password@localhost/sproutchat

# Security
ENCRYPTION_KEY=your_32_byte_base64_encoded_key_here
```

---

## 安装步骤

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或使用 SQLAlchemy 直接创建表
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### 3. 初始化知识点数据

```bash
# 运行知识点初始化脚本
python scripts/init_knowledge_points.py
```

### 4. 启动开发服务器

```bash
# 启动 FastAPI 开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 验证安装

访问 http://localhost:8000/docs 查看 API 文档。

---

## 核心 API 使用示例

### 1. 创建学习记录

```bash
curl -X POST "http://localhost:8000/api/v1/learning/records" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "question_content": "3 + 5 = ?",
    "question_type": "addition",
    "subject": "math",
    "difficulty_level": 1,
    "student_answer": "8",
    "correct_answer": "8",
    "time_spent_seconds": 15
  }'
```

**响应示例**：
```json
{
  "id": 123,
  "student_id": 1,
  "question_content": "3 + 5 = ?",
  "question_type": "addition",
  "subject": "math",
  "difficulty_level": 1,
  "student_answer": "8",
  "correct_answer": "8",
  "is_correct": true,
  "time_spent_seconds": 15,
  "created_at": "2025-01-12T10:30:00Z"
}
```

### 2. 生成苏格拉底式引导反馈

```bash
curl -X POST "http://localhost:8000/api/v1/teaching/guidance" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "question_content": "3 + 5 = ?",
    "question_type": "addition",
    "student_answer": "7",
    "correct_answer": "8",
    "error_type": "calculation",
    "recent_attempts": [
      {"answer": "6", "is_correct": false, "timestamp": "2025-01-12T10:25:00Z"}
    ]
  }'
```

**响应示例**：
```json
{
  "guidance_type": "hint",
  "guidance_content": "让我来帮你检查一下。你一开始有 3 个苹果，妈妈又给了你 5 个，你能用手指或画图的方式数一数，一共有多少个苹果吗？",
  "is_validated": true,
  "confidence_score": 0.95,
  "suggested_follow_up": "如果学生仍然困惑，建议使用可视化引导（画图或实物演示）"
}
```

### 3. 查询错题本

```bash
curl -X GET "http://localhost:8000/api/v1/wrong-answers?student_id=1&is_resolved=false" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**响应示例**：
```json
{
  "total": 15,
  "page": 1,
  "page_size": 20,
  "records": [
    {
      "id": 456,
      "learning_record_id": 123,
      "question_content": "3 + 5 = ?",
      "question_type": "addition",
      "subject": "math",
      "difficulty_level": 1,
      "student_answer": "7",
      "correct_answer": "8",
      "error_type": "calculation",
      "guidance_type": "hint",
      "guidance_content": "让我来帮你检查一下...",
      "is_resolved": false,
      "created_at": "2025-01-12T10:30:00Z"
    }
  ]
}
```

### 4. 获取学习路径推荐

```bash
curl -X GET "http://localhost:8000/api/v1/knowledge-mastery/recommendations?student_id=1&subject=math&limit=5" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**响应示例**：
```json
{
  "student_id": 1,
  "subject": "math",
  "recommendations": [
    {
      "knowledge_point": {
        "id": 5,
        "name": "20以内加法",
        "difficulty_level": 3
      },
      "priority": "high",
      "reason": "所有前置知识点已掌握，建议开始学习本知识点",
      "prerequisites_met": true,
      "estimated_difficulty": "moderate"
    }
  ]
}
```

---

## 开发指南

### 添加新的 API 端点

1. 在 `backend/app/api/` 下创建新的路由文件（如 `teaching.py`）
2. 定义 FastAPI 路由和 Pydantic 模型
3. 实现业务逻辑（调用 services 层）
4. 在 `backend/app/main.py` 中注册路由

### 添加新的 Service

1. 在 `backend/app/services/` 下创建新的服务文件
2. 实现业务逻辑方法
3. 在 API 端点中调用服务方法

### 编写测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_socratic_teacher.py

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```

---

## 常见问题

### Q1: Claude API 调用失败怎么办？

**A**: 检查以下几点：
1. 确认 `OPENAI_API_KEY` 环境变量已正确设置
2. 确认 API key 有效且有足够额度
3. 检查网络连接是否正常
4. 查看 FastAPI 日志获取详细错误信息

### Q2: 如何测试苏格拉底式引导功能？

**A**: 使用以下步骤：
1. 创建一个答错的学习记录
2. 调用 `/api/v1/teaching/guidance` 生成引导式反馈
3. 验证响应不包含直接答案（`is_validated = true`）

### Q3: 知识点数据如何初始化？

**A**: 运行初始化脚本：
```bash
python scripts/init_knowledge_points.py
```

该脚本会创建一年级数学的核心知识点（至少 20 个）并建立依赖关系。

### Q4: 如何确保儿童数据安全？

**A**: 系统已实现以下安全措施：
1. 字段级加密（AES-256）：学生答案等敏感数据加密存储
2. 访问控制：家长只能查看自己孩子的数据
3. JWT 认证：所有 API 端点需要认证
4. 数据保留：学习数据保留 6 个月后自动清理

### Q5: 性能如何优化？

**A**: 以下是性能优化建议：
1. 使用 Redis 缓存热点数据（如学习进度）
2. 对高频查询字段建立索引
3. 使用数据库连接池
4. 异步调用 Claude API（使用 FastAPI 的 `async/await`）

---

## 调试技巧

### 启用详细日志

在 `backend/app/core/config.py` 中设置：

```python
LOG_LEVEL = "DEBUG"
```

### 查看 SQL 查询

在 `backend/app/core/database.py` 中启用 SQL 日志：

```python
engine.echo = True
```

### 使用 FastAPI 自动文档

访问 http://localhost:8000/docs 查看交互式 API 文档。

---

## 下一步

1. 阅读 [data-model.md](./data-model.md) 了解数据模型
2. 阅读 [contracts/](./contracts/) 目录下的 API 契约文档
3. 查看 [research.md](./research.md) 了解技术决策
4. 开始实施：使用 `/speckit.tasks` 生成任务清单

---

## 参考资源

- **项目宪章**: [`.specify/memory/constitution.md`](../../.specify/memory/constitution.md)
- **功能规范**: [`spec.md`](./spec.md)
- **实施计划**: [`plan.md`](./plan.md)
- **API 文档**: http://localhost:8000/docs
