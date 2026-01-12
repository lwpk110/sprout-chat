# Data Model: Phase 2.2 学习管理系统

**Feature**: 小芽家教 Phase 2.2 学习管理系统
**Date**: 2025-01-12
**Status**: ✅ 设计完成

## Overview

本文档定义 Phase 2.2 学习管理系统的数据模型，包括学习记录、错题记录、知识点和知识点掌握度四个核心实体。

---

## Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   Student   │1       *│LearningRecord│         │WrongAnswerRecord│
│  (学生)     │─────────│  (学习记录)   │---------│   (错题记录)     │
└─────────────┘         └──────────────┘         └─────────────────┘
      |                                                    |
      |                                                    |
      |*                                                   |*
      |                    ┌──────────────┐               |
      └────────────────----│KnowledgePoint│←--------------┘
                          │  (知识点)     │
                          └──────────────┘
                                 |*
                                 |
                          ┌──────────────┐
                          │KnowledgeMastery│
                          │ (知识点掌握)   │
                          └──────────────┘
```

---

## Entities

### 1. LearningRecord (学习记录)

**Description**: 代表一次完整的答题活动，包含问题内容、学生答案、正确答案、是否正确、答题耗时等信息。

**Table Name**: `learning_records`

**Fields**:

| Field Name | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | 学习记录唯一标识 |
| student_id | Integer | FOREIGN KEY → students.id, NOT NULL, INDEX | 学生 ID |
| question_content | String(1000) | NOT NULL | 问题内容 |
| question_type | String(50) | NOT NULL | 题目类型（如：addition, subtraction, multiplication） |
| subject | String(50) | NOT NULL, DEFAULT 'math' | 科目（math, chinese, english） |
| difficulty_level | Integer | NOT NULL, DEFAULT 1 | 难度等级（1-5） |
| student_answer | String(500) | ENCRYPTED, NOT NULL | 学生答案（加密存储） |
| correct_answer | String(500) | NOT NULL | 正确答案 |
| is_correct | Boolean | NOT NULL, INDEX | 是否正确 |
| time_spent_seconds | Integer | NOT NULL, MIN=0 | 答题耗时（秒） |
| created_at | DateTime | NOT NULL, DEFAULT=NOW, INDEX | 创建时间 |
| updated_at | DateTime | NOT NULL, DEFAULT=NOW | 更新时间 |

**Relationships**:
- **Many-to-One** with `Student`: 一个学生可以有多条学习记录
- **One-to-One** with `WrongAnswerRecord`: 错误的学习记录可以有一条错题记录（当 is_correct = False）

**Indexes**:
- `idx_student_id`: 加速按学生查询学习记录
- `idx_is_correct`: 加速统计正确/错误数量
- `idx_created_at`: 加速按时间范围查询
- `idx_student_created`: 复合索引（student_id, created_at），加速学生学习进度查询

**Validation Rules**:
- `time_spent_seconds >= 0`: 答题耗时不能为负数
- `difficulty_level BETWEEN 1 AND 5`: 难度等级在 1-5 之间
- `is_correct = (student_answer = correct_answer)`: 正确性判断逻辑

---

### 2. WrongAnswerRecord (错题记录)

**Description**: 代表一次错误的答题活动，是学习记录的子集（当 is_correct = False 时），额外包含错误类型分类和引导式反馈内容。

**Table Name**: `wrong_answer_records`

**Fields**:

| Field Name | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | 错题记录唯一标识 |
| learning_record_id | Integer | FOREIGN KEY → learning_records.id, UNIQUE, NOT NULL | 学习记录 ID |
| error_type | String(50) | NOT NULL, INDEX | 错误类型（calculation, concept, understanding, careless） |
| guidance_type | String(50) | NOT NULL | 引导类型（clarify, hint, break_down, visualize, check_work, alternative_method, encourage） |
| guidance_content | Text | NOT NULL | 引导式反馈内容 |
| is_resolved | Boolean | NOT NULL, DEFAULT=FALSE, INDEX | 是否已解决（学生重新答对） |
| resolved_at | DateTime | NULLABLE | 解决时间 |
| created_at | DateTime | NOT NULL, DEFAULT=NOW | 创建时间 |

**Relationships**:
- **One-to-One** with `LearningRecord`: 一条错题记录对应一条学习记录

**Indexes**:
- `idx_learning_record_id`: 唯一索引，确保一条学习记录只有一条错题记录
- `idx_error_type`: 加速按错误类型筛选
- `idx_is_resolved`: 加速查询未解决/已解决的错题

**Validation Rules**:
- `error_type IN ('calculation', 'concept', 'understanding', 'careless')`: 错误类型必须是预定义的四种之一
- `guidance_type IN ('clarify', 'hint', 'break_down', 'visualize', 'check_work', 'alternative_method', 'encourage')`: 引导类型必须是预定义的七种之一
- `is_resolved = FALSE → resolved_at = NULL`: 未解决的错题不能有解决时间

**State Transitions**:
```
┌──────────┐     重新答对      ┌──────────┐
│ 未解决    │─────────────────→│ 已解决    │
│ (FALSE)  │                  │ (TRUE)   │
└──────────┘                  └──────────┘
```

---

### 3. KnowledgePoint (知识点)

**Description**: 代表一年级数学的一个知识点，包含名称、描述、科目、难度等级和前置知识点依赖关系。

**Table Name**: `knowledge_points`

**Fields**:

| Field Name | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | 知识点唯一标识 |
| name | String(100) | NOT NULL, UNIQUE | 知识点名称（如：10以内加法） |
| description | Text | NULLABLE | 知识点描述 |
| subject | String(50) | NOT NULL, INDEX | 科目（math, chinese, english） |
| difficulty_level | Integer | NOT NULL, DEFAULT=1 | 难度等级（1-5） |
| created_at | DateTime | NOT NULL, DEFAULT=NOW | 创建时间 |
| updated_at | DateTime | NOT NULL, DEFAULT=NOW | 更新时间 |

**Relationships**:
- **Many-to-Many** (self-reference): 一个知识点可以有多个前置知识点，也可以是多个知识点的前置
- **Many-to-Many** with `KnowledgeMastery`: 一个知识点可以被多个学生掌握

**Indexes**:
- `idx_name`: 唯一索引，确保知识点名称不重复
- `idx_subject`: 加速按科目查询知识点
- `idx_subject_difficulty`: 复合索引（subject, difficulty_level），加速按科目和难度查询

**Validation Rules**:
- `difficulty_level BETWEEN 1 AND 5`: 难度等级在 1-5 之间
- **DAG Constraint**: 知识点依赖关系必须形成有向无环图（DAG），不能存在循环依赖

**Sample Data (一年级数学)**:
```
1. 10以内数的认识 (difficulty: 1)
2. 10以内加法 (difficulty: 2, 前置: 1)
3. 10以内减法 (difficulty: 2, 前置: 1)
4. 20以内数的认识 (difficulty: 2, 前置: 1)
5. 20以内加法 (difficulty: 3, 前置: 2, 4)
6. 20以内减法 (difficulty: 3, 前置: 3, 4)
7. 乘法的意义 (difficulty: 4, 前置: 2)
8. 乘法表（2-5） (difficulty: 5, 前置: 7)
```

---

### 4. KnowledgeMastery (知识点掌握)

**Description**: 代表学生对某个知识点的掌握程度，包含掌握度百分比、已练习题数、正确题数、最近更新时间和掌握状态。

**Table Name**: `knowledge_mastery`

**Fields**:

| Field Name | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | 知识点掌握记录唯一标识 |
| student_id | Integer | FOREIGN KEY → students.id, NOT NULL, INDEX | 学生 ID |
| knowledge_point_id | Integer | FOREIGN KEY → knowledge_points.id, NOT NULL, INDEX | 知识点 ID |
| mastery_percentage | Decimal(5,2) | NOT NULL, MIN=0, MAX=100 | 掌握度百分比（0-100） |
| questions_practiced | Integer | NOT NULL, DEFAULT=0, MIN=0 | 已练习题数 |
| questions_correct | Integer | NOT NULL, DEFAULT=0, MIN=0 | 正确题数 |
| recent_performance | Decimal(5,2) | NULLABLE | 最近表现（最近10题的正确率） |
| mastery_status | String(50) | NOT NULL, DEFAULT='not_started', INDEX | 掌握状态（not_started, learning, mastered） |
| last_practiced_at | DateTime | NULLABLE | 最后练习时间 |
| created_at | DateTime | NOT NULL, DEFAULT=NOW | 创建时间 |
| updated_at | DateTime | NOT NULL, DEFAULT=NOW | 更新时间 |

**Relationships**:
- **Many-to-One** with `Student`: 一个学生可以掌握多个知识点
- **Many-to-One** with `KnowledgePoint`: 一个知识点可以被多个学生掌握

**Indexes**:
- `idx_student_knowledge`: 唯一复合索引（student_id, knowledge_point_id），确保每个学生对每个知识点只有一条掌握记录
- `idx_mastery_status`: 加速按掌握状态筛选
- `idx_last_practiced_at`: 加速查询最近练习的知识点

**Validation Rules**:
- `mastery_percentage BETWEEN 0 AND 100`: 掌握度在 0-100 之间
- `questions_correct <= questions_practiced`: 正确题数不能超过练习题数
- `mastery_status IN ('not_started', 'learning', 'mastered')`: 掌握状态必须是预定义的三种之一
- **Mastered Criteria**: `mastery_status = 'mastered'` 当且仅当 `mastery_percentage >= 85 AND questions_practiced >= 10`

**掌握度计算公式**:
```
mastery_percentage = (questions_correct / questions_practiced) * 100 * weight_factor

其中 weight_factor 考虑：
- 最近表现（最近10题的正确率）：权重 40%
- 历史表现（所有题目的正确率）：权重 40%
- 连续答对次数：权重 20%
```

**State Transitions**:
```
┌─────────────┐   开始练习   ┌──────────┐   掌握度 >= 85%   ┌──────────┐
│ 未开始       │────────────→│ 学习中    │────────────────→│ 已掌握    │
│not_started  │            │ learning │                   │mastered  │
└─────────────┘            └──────────┘                   └──────────┘
```

---

### 5. KnowledgePointDependency (知识点依赖关系)

**Description**: 知识点之间的多对多关联表，记录前置知识点依赖关系。

**Table Name**: `knowledge_point_dependencies`

**Fields**:

| Field Name | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| knowledge_point_id | Integer | FOREIGN KEY → knowledge_points.id, PRIMARY KEY | 知识点 ID |
| prerequisite_id | Integer | FOREIGN KEY → knowledge_points.id, PRIMARY KEY | 前置知识点 ID |
| created_at | DateTime | NOT NULL, DEFAULT=NOW | 创建时间 |

**Relationships**:
- **Many-to-Many** (self-reference of `KnowledgePoint`): 通过中间表实现知识点之间的依赖关系

**Indexes**:
- **PRIMARY KEY**: 复合主键（knowledge_point_id, prerequisite_id），确保同一对依赖关系不重复
- `idx_prerequisite_id`: 加速反向查询（哪些知识点依赖当前知识点）

**Validation Rules**:
- `knowledge_point_id != prerequisite_id`: 知识点不能依赖自己
- **DAG Constraint**: 不能存在循环依赖（A → B → C → A）

---

## Database Migration Strategy

### Migration Steps

1. **Phase 1: 创建基础表**
   - 创建 `learning_records` 表（扩展已存在的表）
   - 创建 `knowledge_points` 表
   - 创建 `knowledge_mastery` 表

2. **Phase 2: 创建关联表**
   - 创建 `knowledge_point_dependencies` 表
   - 创建 `wrong_answer_records` 表

3. **Phase 3: 创建索引**
   - 创建所有单列索引
   - 创建复合索引

4. **Phase 4: 数据迁移**
   - 从旧的 `learning_records` 表迁移数据
   - 初始化一年级数学知识点数据（20 个知识点）

### Rollback Strategy

每个 migration 都有对应的 rollback 脚本：
- Phase 4 rollback: 清空初始化数据
- Phase 3 rollback: 删除索引
- Phase 2 rollback: 删除关联表
- Phase 1 rollback: 删除基础表

---

## Performance Considerations

1. **索引策略**:
   - 所有外键字段都建立索引
   - 高频查询字段（is_correct, mastery_status）建立索引
   - 复合索引优化多条件查询

2. **查询优化**:
   - 使用 `EXPLAIN QUERY PLAN` 分析慢查询
   - 避免 N+1 查询问题，使用 `eager loading`
   - 对大数据集使用分页

3. **缓存策略**:
   - 知识点列表（不常变化）可以缓存
   - 学生学习进度使用 Redis 缓存（TTL: 5 分钟）
   - 错题本使用短期缓存（TTL: 1 分钟）

---

## Security Considerations

1. **数据加密**:
   - `student_answer` 字段使用 AES-256 加密存储
   - 加密密钥通过环境变量配置

2. **访问控制**:
   - 家长只能查看自己孩子的学习记录
   - 通过 `get_current_parent_id()` 获取当前登录家长 ID
   - 所有查询都加上 `student.parent_id = current_parent_id` 过滤条件

3. **数据保留**:
   - 学习记录保留 6 个月
   - 定期清理过期数据（使用 cron job）

---

## Summary

| Entity | Table Name | Fields | Relationships | Indexes |
|--------|-----------|--------|---------------|---------|
| LearningRecord | learning_records | 11 | Many-to-One: Student, One-to-One: WrongAnswerRecord | 4 |
| WrongAnswerRecord | wrong_answer_records | 8 | One-to-One: LearningRecord | 3 |
| KnowledgePoint | knowledge_points | 7 | Many-to-Many: self, Many-to-Many: KnowledgeMastery | 3 |
| KnowledgeMastery | knowledge_mastery | 11 | Many-to-One: Student, Many-to-One: KnowledgePoint | 3 |
| KnowledgePointDependency | knowledge_point_dependencies | 3 | Many-to-Many: KnowledgePoint (self) | 2 |

**Total Tables**: 5
**Total Relationships**: 6
**Total Indexes**: 15
