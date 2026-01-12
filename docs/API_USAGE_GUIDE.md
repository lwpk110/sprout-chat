# 小芽家教 API 使用指南

## 概述

小芽家教 API 提供完整的 AI-First 个性化家教功能，包括学习记录追踪、苏格拉底式教学、错题本管理和知识点图谱。

## 基础信息

- **Base URL**: `http://localhost:8000` (开发环境)
- **API 版本**: v1
- **认证方式**: Bearer Token
- **数据格式**: JSON

## 认证

### 获取 Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "parent1",
    "password": "securepass123",
    "email": "parent@example.com"
  }'
```

### 使用 Token

```bash
curl -X GET "http://localhost:8000/api/v1/learning/records?student_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 核心功能使用

### 1. 学习记录追踪

#### 创建学习记录

```bash
curl -X POST "http://localhost:8000/api/v1/learning/records" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "question_content": "3 + 5 = ?",
    "question_type": "addition",
    "subject": "math",
    "difficulty_level": 1,
    "student_answer": "7",
    "correct_answer": "8",
    "time_spent_seconds": 15
  }'
```

**响应** (201 Created):
```json
{
  "id": 123,
  "student_id": 1,
  "question_content": "3 + 5 = ?",
  "question_type": "addition",
  "subject": "math",
  "difficulty_level": 1,
  "student_answer": "7",
  "correct_answer": "8",
  "is_correct": false,
  "answer_result": "incorrect",
  "time_spent_seconds": 15,
  "created_at": "2026-01-12T10:30:00Z"
}
```

#### 获取学习进度

```bash
curl -X GET "http://localhost:8000/api/v1/learning/progress?student_id=1&time_range=week"
```

**响应**:
```json
{
  "student_id": 1,
  "total_questions": 50,
  "correct_count": 42,
  "wrong_count": 8,
  "accuracy_rate": 84.0,
  "current_streak": 5,
  "longest_streak": 10,
  "total_time_spent_seconds": 750
}
```

### 2. 苏格拉底式教学

#### 生成引导式反馈

```bash
curl -X POST "http://localhost:8000/api/v1/teaching/guidance" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "你有 3 个苹果，妈妈又给了你 5 个，现在一共有几个苹果？",
    "student_answer": "7",
    "correct_answer": "8",
    "attempts": 1
  }'
```

**响应**:
```json
{
  "guidance_type": "hint",
  "content": "让我来帮你检查一下。你一开始有 3 个苹果，妈妈又给了你 5 个，你能用手指或画图的方式数一数，一共有多少个苹果吗？",
  "metadata": {
    "error_type": "calculation",
    "attempts": 1
  }
}
```

#### 验证引导响应

```bash
curl -X POST "http://localhost:8000/api/v1/teaching/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "response": "让我来帮你检查一下。你一开始有 3 个苹果，妈妈又给了你 5 个...",
    "question": "3 + 5 = ?",
    "correct_answer": "8"
  }'
```

**响应**:
```json
{
  "valid": true,
  "reason": "响应不包含直接答案，通过验证",
  "layer": 3
}
```

### 3. 错题本管理

#### 获取错题列表

```bash
curl -X GET "http://localhost:8000/api/v1/wrong-answers?student_id=1&page=1&page_size=10"
```

**响应**:
```json
{
  "total": 25,
  "page": 1,
  "page_size": 10,
  "wrong_answers": [
    {
      "id": 1,
      "student_id": 1,
      "question_content": "3 + 5 = ?",
      "student_answer": "7",
      "correct_answer": "8",
      "error_type": "calculation",
      "is_resolved": false,
      "attempts_count": 2,
      "created_at": "2026-01-12T10:30:00Z"
    }
  ]
}
```

#### 获取练习推荐

```bash
curl -X GET "http://localhost:8000/api/v1/wrong-answers/recommendations?student_id=1&limit=5"
```

**响应**:
```json
{
  "student_id": 1,
  "total_count": 25,
  "recommendations": [
    {
      "priority": "high",
      "wrong_answer_id": 1,
      "question_content": "3 + 5 = ?",
      "error_type": "calculation",
      "attempts_count": 3,
      "reason": "该题错误3次，属于高优先级练习"
    }
  ]
}
```

#### 获取错题统计

```bash
curl -X GET "http://localhost:8000/api/v1/wrong-answers/statistics?student_id=1"
```

**响应**:
```json
{
  "student_id": 1,
  "total_wrong_answers": 25,
  "resolved_count": 10,
  "unresolved_count": 15,
  "by_error_type": {
    "calculation": 12,
    "concept": 8,
    "understanding": 3,
    "careless": 2
  },
  "most_common_errors": ["calculation", "concept"]
}
```

### 4. 知识点图谱

#### 获取知识点列表

```bash
curl -X GET "http://localhost:8000/api/v1/knowledge-points?subject=math&difficulty_level=1"
```

**响应**:
```json
{
  "total": 10,
  "knowledge_points": [
    {
      "id": 1,
      "name": "加法基础",
      "subject": "math",
      "difficulty_level": 1,
      "description": "10 以内的加法运算",
      "parent_id": null
    }
  ]
}
```

#### 获取学习路径推荐

```bash
curl -X GET "http://localhost:8000/api/v1/knowledge-mastery/recommendations?student_id=1&subject=math"
```

**响应**:
```json
{
  "student_id": 1,
  "recommended_path": [
    {
      "order": 1,
      "knowledge_point": {
        "id": 1,
        "name": "加法基础",
        "difficulty_level": 1
      },
      "prerequisites_met": true,
      "reason": "前置知识点已掌握，可以开始学习"
    },
    {
      "order": 2,
      "knowledge_point": {
        "id": 3,
        "name": "进位加法",
        "difficulty_level": 2
      },
      "prerequisites_met": false,
      "reason": "需要先掌握加法基础"
    }
  ]
}
```

## 错误处理

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 400 | 请求参数错误 | 学生ID不存在 |
| 401 | 未授权 | Token 无效或过期 |
| 404 | 资源不存在 | 学习记录不存在 |
| 500 | 服务器错误 | 数据库连接失败 |

## 完整工作流示例

### 学生答题流程

```bash
# 1. 学生答题
RECORD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/learning/records" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "question_content": "3 + 5 = ?",
    "question_type": "addition",
    "subject": "math",
    "difficulty_level": 1,
    "student_answer": "7",
    "correct_answer": "8",
    "time_spent_seconds": 15
  }')

echo "记录创建: $RECORD_RESPONSE"

# 2. 如果答错，获取引导式反馈
GUIDANCE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/teaching/guidance" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "3 + 5 = ?",
    "student_answer": "7",
    "correct_answer": "8",
    "attempts": 1
  }')

echo "引导反馈: $GUIDANCE_RESPONSE"

# 3. 获取错题统计
STATS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/wrong-answers/statistics?student_id=1")

echo "错题统计: $STATS_RESPONSE"

# 4. 获取练习推荐
REC_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/wrong-answers/recommendations?student_id=1&limit=5")

echo "练习推荐: $REC_RESPONSE"
```

## 性能优化建议

1. **批量操作**: 尽量使用批量端点减少请求次数
2. **缓存**: 客户端缓存不常变化的数据（如知识点列表）
3. **分页**: 使用分页参数控制返回数据量
4. **异步**: 对于耗时操作（如AI生成），考虑异步处理

## 交互式文档

访问以下地址查看交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 支持

如有问题，请查看项目文档或提交 Issue。
