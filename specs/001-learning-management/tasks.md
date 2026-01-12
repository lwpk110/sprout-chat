# Implementation Tasks: Phase 2.2 学习管理系统

**Feature**: 小芽家教 Phase 2.2 学习管理系统
**Branch**: `001-learning-management`
**Date**: 2025-01-12
**Status**: Ready for Implementation

## Overview

本文档定义 Phase 2.2 学习管理系统的实施任务清单，任务按用户故事组织，支持独立实施和测试。

**技术栈**：
- 语言：Python 3.11+
- 框架：FastAPI, SQLAlchemy, Pydantic v2
- 数据库：SQLite (开发) / PostgreSQL (生产)
- 测试：pytest, pytest-asyncio
- 外部服务：Claude API (Anthropic SDK)

**开发原则**：
- 遵循 TDD 流程：红灯 → 绿灯 → 重构
- 测试覆盖率目标：≥ 80%
- 每个阶段独立提交到 Git

---

## Phase 1: Setup & Foundation

### 目标
建立项目基础设施，配置开发环境，集成必要的外部服务。

### 验收标准
- [ ] 开发环境可以正常启动 FastAPI 服务器
- [ ] Claude API 连接测试通过
- [ ] 数据库表结构创建成功
- [ ] 所有依赖包安装完成

### 任务清单

- [ ] T001 配置 Claude API 集成环境
  - 在 `backend/.env` 添加 AI_PROVIDER、AI_MODEL、OPENAI_API_KEY、OPENAI_BASE_URL
  - 测试 Claude API 连接：创建简单的测试脚本验证 API 调用
  - 提交：`git commit -m "[LWP-2.2-T001] chore: 配置 Claude API 集成环境"`

- [ ] T002 安装 Python 依赖包
  - 添加 anthropic (Claude SDK) 到 requirements.txt
  - 添加 cryptography (AES-256 加密) 到 requirements.txt
  - 运行 `pip install -r requirements.txt`
  - 提交：`git commit -m "[LWP-2.2-T002] chore: 安装 Phase 2.2 必要依赖包"`

- [ ] T003 创建数据加密服务（儿童数据安全）
  - 在 `backend/app/core/security.py` 实现 EncryptionService 类
  - 使用 Fernet (AES-256) 实现字段级加密
  - 提供 encrypt() 和 decrypt() 方法
  - 提交：`git commit -m "[LWP-2.2-T003] feat: 实现数据加密服务"`

- [ ] T004 [P] 创建学习记录扩展模型（LearningRecord）
  - 扩展 `backend/app/models/learning.py`，添加新字段（如果需要）
  - 添加索引：idx_student_id, idx_is_correct, idx_created_at, idx_student_created
  - 实现 SQLAlchemy 模型定义
  - 提交：`git commit -m "[LWP-2.2-T004] feat: 扩展学习记录模型"`

- [ ] T005 [P] 创建错题记录模型（WrongAnswerRecord）
  - 在 `backend/app/models/wrong_answer.py` 实现 WrongAnswerRecord 模型
  - 字段：id, learning_record_id, error_type, guidance_type, guidance_content, is_resolved, resolved_at, created_at
  - 添加索引：idx_learning_record_id (UNIQUE), idx_error_type, idx_is_resolved
  - 实现与 LearningRecord 的一对一关系
  - 提交：`git commit -m "[LWP-2.2-T005] feat: 创建错题记录模型"`

- [ ] T006 [P] 创建知识点模型（KnowledgePoint）
  - 在 `backend/app/models/knowledge_point.py` 实现 KnowledgePoint 模型
  - 字段：id, name, subject, difficulty_level, description, created_at, updated_at
  - 添加索引：idx_name (UNIQUE), idx_subject, idx_subject_difficulty
  - 提交：`git commit -m "[LWP-2.2-T006] feat: 创建知识点模型"`

- [ ] T007 [P] 创建知识点掌握模型（KnowledgeMastery）
  - 在 `backend/app/models/knowledge_mastery.py` 实现 KnowledgeMastery 模型
  - 字段：id, student_id, knowledge_point_id, mastery_percentage, questions_practiced, questions_correct, recent_performance, mastery_status, last_practiced_at, created_at, updated_at
  - 添加索引：idx_student_knowledge (UNIQUE), idx_mastery_status, idx_last_practiced_at
  - 实现掌握度计算逻辑
  - 提交：`git commit -m "[LWP-2.2-T007] feat: 创建知识点掌握模型"`

- [ ] T008 [P] 创建知识点依赖关系模型（KnowledgePointDependency）
  - 在 `backend/app/models/knowledge_point.py` 添加 KnowledgePointDependency 模型
  - 字段：knowledge_point_id, prerequisite_id, created_at
  - 添加复合主键约束
  - 实现 DAG 约束（防止循环依赖）
  - 提交：`git commit -m "[LWP-2.2-T008] feat: 创建知识点依赖关系模型"`

- [ ] T009 创建数据库迁移脚本
  - 使用 Alembic 创建迁移脚本
  - 包含所有新模型的表结构定义
  - 添加索引和外键约束
  - 提交：`git commit -m "[LWP-2.2-T009] feat: 创建数据库迁移脚本"`

- [ ] T010 初始化知识点数据
  - 在 `backend/scripts/init_knowledge_points.py` 创建初始化脚本
  - 生成 20 个一年级数学知识点
  - 建立知识点之间的依赖关系
  - 提交：`git commit -m "[LWP-2.2-T010] feat: 初始化一年级数学知识点数据"`

---

## Phase 2: User Story 1 - 学习记录追踪 (P1)

### 目标
实现学生学习活动的记录、查询和统计功能，支持生成学习进度报告。

### 用户故事
家长和老师需要记录学生的学习活动，以便追踪学习进度和识别学习困难点。当学生完成一道题目时，系统应该自动记录问题内容、学生的答案、是否正确、以及答题耗时。

### 依赖关系
- 无前置依赖（基础功能）

### 独立测试标准
- [ ] 可以创建学习记录（正确答案）
- [ ] 可以创建学习记录（错误答案）并自动生成错题记录
- [ ] 可以查询学生的学习记录列表（按时间、题型筛选）
- [ ] 可以生成学习进度报告（总题数、正确率、连续答对次数等）

### 任务清单

#### 测试任务（TDD - Red Phase）

- [ ] T011 [US1] 编写学习记录 API 测试（红灯）
  - 在 `backend/tests/unit/test_learning_api.py` 编写测试用例
  - 测试创建学习记录（正确答案）
  - 测试创建学习记录（错误答案，自动创建错题记录）
  - 测试查询学习记录列表
  - 测试获取学习进度统计
  - 测试生成学习进度报告
  - 运行 `pytest` 确认失败 ❌
  - 提交：`git commit -m "[LWP-2.2-T011] test: 添加学习记录 API 测试用例 (Red)"`

#### 实现任务（TDD - Green Phase）

- [ ] T012 [US1] 扩展学习记录 API 端点
  - 在 `backend/app/api/learning.py` 扩展现有 API
  - 实现 POST /learning/records（创建记录，自动处理错题）
  - 实现 GET /learning/records（查询列表，支持筛选）
  - 实现 GET /learning/records/{record_id}（获取详情）
  - 实现 GET /learning/progress（获取进度统计）
  - 实现 GET /learning/report（生成报告）
  - 集成加密服务保护学生答案
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T012] feat: 实现学习记录 API 端点 (Green)"`

- [ ] T013 [US1] 实现学习追踪服务
  - 在 `backend/app/services/learning_tracker.py` 扩展服务
  - 实现 create_record() 方法（创建记录，判断对错）
  - 实现 get_progress() 方法（计算进度统计）
  - 实现 generate_report() 方法（生成报告）
  - 实现自动创建错题记录逻辑（当 is_correct = False）
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T013] feat: 实现学习追踪业务逻辑 (Green)"`

#### 集成测试

- [ ] T014 [US1] 编写学习记录集成测试
  - 在 `backend/tests/integration/test_learning_flow.py` 编写测试
  - 测试完整的学习记录流程（创建 → 查询 → 报告）
  - 测试错题记录自动创建逻辑
  - 测试数据加密解密正确性
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T014] test: 添加学习记录集成测试 (Green)"`

---

## Phase 3: User Story 2 - 苏格拉底式引导教学 (P1)

### 目标
实现苏格拉底式引导教学系统，当学生答错时通过提问引导学生思考，而不是直接给出答案。

### 用户故事
当学生回答错误时，系统不应该直接给出正确答案，而是通过苏格拉底式提问引导学生自己思考，找到正确答案。这能培养学生的思维能力。

### 依赖关系
- 无前置依赖（独立功能，可与 US1 并行开发）

### 独立测试标准
- [ ] 可以生成引导式反馈（包含引导性问题）
- [ ] 引导式响应不包含直接答案（通过验证）
- [ ] 支持 7 种引导类型（澄清、提示、分解、可视化、检查、替代方法、鼓励）
- [ ] 根据错误类型和答题历史调整引导策略

### 任务清单

#### 测试任务（TDD - Red Phase）

- [ ] T021 [US2] 编写苏格拉底教学服务测试（红灯）
  - 在 `backend/tests/unit/test_socratic_teacher.py` 编写测试
  - 测试生成引导式反馈
  - 测试 7 种引导类型
  - 测试错误答案分类
  - 测试连续出错时的策略调整
  - 运行 `pytest` 确认失败 ❌
  - 提交：`git commit -m "[LWP-2.2-T021] test: 添加苏格拉底教学服务测试用例 (Red)"`

#### 实现任务（TDD - Green Phase）

- [ ] T022 [US2] 实现错误答案分类器
  - 在 `backend/app/services/wrong_analyzer.py` 实现 WrongAnswerClassifier 类
  - 实现 classify() 方法（判断错误类型：calculation/concept/understanding/careless）
  - 实现 _is_calculation_error()（计算错误检测）
  - 实现 _is_concept_error()（概念错误检测）
  - 实现 _is_understanding_error()（理解错误检测）
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T022] feat: 实现错误答案分类器 (Green)"`

- [ ] T023 [US2] 实现响应验证系统
  - 在 `backend/app/services/response_validator.py` 实现 ResponseValidator 类
  - 实现 validate_response() 方法（检测直接答案）
  - 实现关键词检测（Layer 1）
  - 实现答案检测（Layer 2）
  - 实现 AI 二次验证（Layer 3，可选）
  - 目标准确率：95%（SC-003）
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T023] feat: 实现响应验证系统 (Green)"`

- [ ] T024 [US2] 集成 Claude API 生成引导式响应
  - 在 `backend/app/services/socratic_teacher.py` 实现 SocraticTeacherService 类
  - 实现 generate_guidance() 方法（调用 Claude API）
  - 实现系统提示词模板（7 种引导类型）
  - 实现引导策略选择逻辑（基于错误类型和答题历史）
  - 实现 _build_system_prompt() 方法（构建提示词）
  - 实现 _select_guidance_type() 方法（选择引导类型）
  - 调用 ResponseValidator 验证响应
  - 目标响应时间：< 3 秒
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T024] feat: 集成 Claude API 生成引导式响应 (Green)"`

- [ ] T025 [US2] 实现引导教学 API 端点
  - 在 `backend/app/api/teaching.py` 创建新的 API 路由
  - 实现 POST /teaching/guidance（生成引导式反馈）
  - 实现 POST /teaching/guidance/validate（验证引导式反馈）
  - 实现 GET /teaching/guidance/types（获取引导类型列表）
  - 集成 SocraticTeacherService
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T025] feat: 实现引导教学 API 端点 (Green)"`

#### 集成测试

- [ ] T026 [US2] 编写引导教学集成测试
  - 在 `backend/tests/integration/test_teaching_flow.py` 编写测试
  - 测试完整的引导流程（错误 → 引导 → 验证）
  - 测试连续出错时的策略调整
  - 测试 Claude API 调用失败时的降级处理
  - 测试响应验证逻辑
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T026] test: 添加引导教学集成测试 (Green)"`

---

## Phase 4: User Story 3 - 错题本管理 (P2)

### 目标
实现错题本的记录、查询、统计和练习推荐功能，帮助家长和学生针对性地复习薄弱知识点。

### 用户故事
家长和学生需要查看和练习错题，以便针对性地复习薄弱知识点。系统应该自动将学生的错误答案分类整理，提供针对性的练习推荐。

### 依赖关系
- **依赖 US1**（学习记录追踪）
- US3 中的错题记录在 US1 中已创建（T012, T013）

### 独立测试标准
- [ ] 可以查询错题列表（按科目、题型、错误类型筛选）
- [ ] 可以查看错题详情（包含原始问题和引导式反馈）
- [ ] 可以更新错题状态（标记为已解决/未解决）
- [ ] 可以获取错题统计（按错误类型、题型分布）
- [ ] 可以生成练习推荐（基于错题类型）

### 任务清单

#### 测试任务（TDD - Red Phase）

- [ ] T031 [US3] 编写错题本 API 测试（红灯）
  - 在 `backend/tests/unit/test_wrong_answers_api.py` 编写测试
  - 测试查询错题列表
  - 测试获取错题详情
  - 测试更新错题状态
  - 测试获取错题统计
  - 测试生成练习推荐
  - 运行 `pytest` 确认失败 ❌
  - 提交：`git commit -m "[LWP-2.2-T031] test: 添加错题本 API 测试用例 (Red)"`

#### 实现任务（TDD - Green Phase）

- [ ] T032 [US3] 实现练习推荐服务
  - 在 `backend/app/services/practice_recommender.py` 实现 PracticeRecommenderService 类
  - 实现 generate_recommendations() 方法（基于错题类型推荐练习）
  - 实现 _get_wrong_answers_by_type() 方法（按类型分组错题）
  - 实现 _generate_similar_question() 方法（生成相似但不相同的题目）
  - 实现优先级排序（high/medium/low）
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T032] feat: 实现练习推荐服务 (Green)"`

- [ ] T033 [US3] 实现错题本 API 端点
  - 在 `backend/app/api/wrong_answers.py` 创建新的 API 路由
  - 实现 GET /wrong-answers（查询错题列表，支持筛选）
  - 实现 GET /wrong-answers/{wrong_answer_id}（获取详情）
  - 实现 PATCH /wrong-answers/{wrong_answer_id}（更新状态）
  - 实现 GET /wrong-answers/statistics（获取统计）
  - 实现 GET /wrong-answers/recommendations（获取练习推荐）
  - 集成 PracticeRecommenderService
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T033] feat: 实现错题本 API 端点 (Green)"`

#### 集成测试

- [ ] T034 [US3] 编写错题本集成测试
  - 在 `backend/tests/integration/test_wrong_answers_flow.py` 编写测试
  - 测试错题记录自动创建流程（基于 US1）
  - 测试错题查询和筛选
  - 测试错题状态更新（解决/未解决）
  - 测试练习推荐生成逻辑
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T034] test: 添加错题本集成测试 (Green)"`

---

## Phase 5: User Story 4 - 知识点图谱追踪 (P2)

### 目标
实现知识点图谱的建立、掌握度追踪和学习路径推荐功能，帮助家长和老师了解学生的学习进度。

### 用户故事
家长和老师需要了解学生对各个知识点的掌握情况，以便调整学习计划。系统应该建立一年级数学的知识点结构，并追踪学生的掌握程度。

### 依赖关系
- **依赖 US1**（学习记录追踪）
- US4 中的知识点掌握度基于学习记录数据计算

### 独立测试标准
- [ ] 可以查询知识点列表（按科目、难度筛选）
- [ ] 可以获取知识点图谱（DAG 结构）
- [ ] 可以查询学生的知识点掌握情况
- [ ] 可以更新知识点掌握度
- [ ] 可以获取学习路径推荐（基于前置知识点）

### 任务清单

#### 测试任务（TDD - Red Phase）

- [ ] T041 [US4] 编写知识点图谱 API 测试（红灯）
  - 在 `backend/tests/unit/test_knowledge_api.py` 编写测试
  - 测试查询知识点列表
  - 测试获取知识点详情
  - 测试获取知识点图谱
  - 测试查询知识点掌握情况
  - 测试更新知识点掌握度
  - 测试获取学习路径推荐
  - 运行 `pytest` 确认失败 ❌
  - 提交：`git commit -m "[LWP-2.2-T041] test: 添加知识点图谱 API 测试用例 (Red)"`

#### 实现任务（TDD - Green Phase）

- [ ] T042 [US4] 实现知识点追踪服务
  - 在 `backend/app/services/knowledge_tracker.py` 实现 KnowledgeTrackerService 类
  - 实现 update_mastery() 方法（更新知识点掌握度）
  - 实现 calculate_mastery_percentage() 方法（计算掌握度）
  - 实现 check_prerequisites_met() 方法（检查前置知识点是否已掌握）
  - 实现 generate_learning_path() 方法（生成学习路径推荐）
  - 实现掌握度计算公式（最近表现 40% + 历史表现 40% + 连续答对 20%）
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T042] feat: 实现知识点追踪服务 (Green)"`

- [ ] T043 [US4] 实现知识点图谱 API 端点
  - 在 `backend/app/api/knowledge.py` 创建新的 API 路由
  - 实现 GET /knowledge-points（查询知识点列表）
  - 实现 GET /knowledge-points/{knowledge_point_id}（获取详情）
  - 实现 GET /knowledge-points/graph（获取知识点图谱 DAG）
  - 实现 GET /knowledge-mastery（查询掌握情况）
  - 实现 GET /knowledge-mastery/{mastery_id}（获取掌握详情）
  - 实现 PATCH /knowledge-mastery/{mastery_id}（更新掌握度）
  - 实现 GET /knowledge-mastery/recommendations（获取学习路径推荐）
  - 集成 KnowledgeTrackerService
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T043] feat: 实现知识点图谱 API 端点 (Green)"`

#### 集成测试

- [ ] T044 [US4] 编写知识点图谱集成测试
  - 在 `backend/tests/integration/test_knowledge_graph.py` 编写测试
  - 测试知识点 DAG 结构正确性
  - 测试掌握度计算逻辑
  - 测试前置知识点依赖检查
  - 测试学习路径推荐算法
  - 测试与学习记录的集成（基于 US1）
  - 运行 `pytest` 确认通过 ✅
  - 提交：`git commit -m "[LWP-2.2-T044] test: 添加知识点图谱集成测试 (Green)"`

---

## Phase 6: Polish & Cross-Cutting Concerns

### 目标
性能优化、文档完善、最终测试和部署准备。

### 验收标准
- [ ] 所有测试通过（单元测试 + 集成测试）
- [ ] 测试覆盖率 ≥ 80%
- [ ] API 响应时间（p95）< 200ms
- [ ] 文档完善（API 文档、快速开始指南）

### 任务清单

- [ ] T051 [P] 编写 API 契约测试
  - 在 `backend/tests/contract/test_api_contracts.py` 编写契约测试
  - 验证所有 API 端点符合 OpenAPI 规范
  - 测试请求/响应格式正确性
  - 提交：`git commit -m "[LWP-2.2-T051] test: 添加 API 契约测试"`

- [ ] T052 [P] 性能优化（索引和查询）
  - 分析慢查询（使用 EXPLAIN QUERY PLAN）
  - 优化数据库索引
  - 优化 N+1 查询问题（使用 eager loading）
  - 实现 Redis 缓存（学习进度、知识点列表）
  - 目标：API 响应时间（p95）< 200ms
  - 提交：`git commit -m "[LWP-2.2-T052] perf: 优化 API 响应时间"`

- [ ] T053 [P] 验证与现有认证系统的集成
  - 测试 JWT 认证集成（基于 Phase 2.1）
  - 测试权限控制（家长只能访问自己孩子的数据）
  - 测试加密数据访问控制
  - 提交：`git commit -m "[LWP-2.2-T053] feat: 验证认证系统集成"`

- [ ] T054 [P] 生成测试覆盖率报告
  - 运行 `pytest --cov=app --cov-report=html --cov-report=term`
  - 验证测试覆盖率 ≥ 80%
  - 查看未覆盖的代码并补充测试
  - 提交：`git commit -m "[LWP-2.2-T054] test: 生成测试覆盖率报告"`

- [ ] T055 完善 API 文档
  - 更新 FastAPI 自动文档（/docs, /redoc）
  - 添加详细的请求/响应示例
  - 添加错误码说明
  - 提交：`git commit -m "[LWP-2.2-T055] docs: 完善 API 文档"`

- [ ] T056 最终端到端测试
  - 测试完整的用户流程（学习记录 → 引导教学 → 错题本 → 知识点图谱）
  - 测试并发场景（1000 并发学生）
  - 测试边界情况（空答案、异常数据、API 失败）
  - 提交：`git commit -m "[LWP-2.2-T056] test: 最终端到端测试"`

---

## Dependencies & Execution Order

### User Story 依赖图

```text
Phase 1: Setup & Foundation
  ├─ T001-T010 (基础设施)
  └─ → Phase 2, Phase 3 (并行开始)

Phase 2: US1 - 学习记录追踪 (P1)
  ├─ T011-T014
  └─ → Phase 4: US3 (依赖 US1)

Phase 3: US2 - 引导式教学 (P1)
  ├─ T021-T026
  └─ → 无依赖（独立功能）

Phase 4: US3 - 错题本管理 (P2)
  ├─ T031-T034
  └─ 依赖 US1 (T012, T013 创建错题记录)

Phase 5: US4 - 知识点图谱追踪 (P2)
  ├─ T041-T044
  └─ 依赖 US1 (掌握度基于学习记录)

Phase 6: Polish & Cross-Cutting Concerns
  └─ T051-T056 (所有功能完成后)
```

### 推荐执行顺序

**Week 1-2: Foundation + P1 Stories**
1. Phase 1: Setup (T001-T010) - 2 天
2. Phase 2: US1 学习记录 (T011-T014) - 3 天
3. Phase 3: US2 引导教学 (T021-T026) - 4 天

**Week 3: P2 Stories**
4. Phase 4: US3 错题本 (T031-T034) - 2 天
5. Phase 5: US4 知识点图谱 (T041-T044) - 3 天

**Week 4: Polish & Deployment**
6. Phase 6: Polish (T051-T056) - 2 天

---

## Parallel Execution Opportunities

### Phase 1 (Setup & Foundation)
**并行任务组 1**（可同时开发）：
- T004: LearningRecord 模型
- T005: WrongAnswerRecord 模型
- T006: KnowledgePoint 模型
- T007: KnowledgeMastery 模型
- T008: KnowledgePointDependency 模型

**原因**：不同文件，无相互依赖

### Phase 2 & 3 (P1 Stories - 可并行)
- Phase 2 (US1): T011-T014 - 学习记录追踪
- Phase 3 (US2): T021-T026 - 引导式教学

**原因**：US1 和 US2 都是 P1，无依赖关系，可由不同开发者并行实施

### Phase 6 (Polish)
**并行任务组 2**（可同时开发）：
- T051: API 契约测试
- T052: 性能优化
- T053: 认证集成验证
- T055: API 文档完善

**原因**：不同关注点，可并行处理

---

## Implementation Strategy

### MVP Scope（最小可行产品）

**第一版发布（MVP）**：仅包含 **Phase 1 + Phase 2 + Phase 3**
- Setup & Foundation
- US1: 学习记录追踪 (P1)
- US2: 引导式教学 (P1)

**MVP 验收标准**：
- [ ] 学生可以提交答题记录
- [ ] 系统可以生成苏格拉底式引导反馈
- [ ] 家长可以查看学习进度报告
- [ ] 所有 MVP 功能的测试覆盖率 ≥ 80%

**后续迭代**：增量交付
- Iteration 2: Phase 4 (US3 错题本)
- Iteration 3: Phase 5 (US4 知识点图谱)

### Incremental Delivery（增量交付）

每个 User Story 完成后都应：
1. 运行完整的测试套件
2. 验证独立测试标准
3. 提交到 Git（使用功能分支）
4. 合并到主分支（可选，取决于发布策略）

---

## Testing Strategy

### TDD 流程（强制执行）

每个功能都必须遵循 **Red → Green → Refactor** 循环：

1. **Red（红灯）**：先写失败的测试
   - 编写测试用例
   - 运行 `pytest` 确认失败 ❌
   - 提交：`git commit -m "... test: ... (Red)"`

2. **Green（绿灯）**：编写最少代码让测试通过
   - 实现功能代码
   - 运行 `pytest` 确认通过 ✅
   - 提交：`git commit -m "... feat: ... (Green)"`

3. **Refactor（重构）**：优化代码质量
   - 重构代码，保持测试通过
   - 运行 `pytest` 确认仍然通过 ✅
   - 提交：`git commit -m "... refactor: ... (Refactor)"`

### 测试覆盖率目标

- **单元测试**：每个 service 和 api 都有对应的单元测试
- **集成测试**：每个 user story 都有集成测试
- **契约测试**：所有 API 端点符合 OpenAPI 规范
- **覆盖率目标**：≥ 80%（项目宪章要求）

---

## Task Checklist Format Validation

✅ **所有任务都遵循严格的检查清单格式**：
- ✅ 复选框：`- [ ]`
- ✅ 任务 ID：`T001`, `T002`, ...
- ✅ [P] 标记：标记可并行任务
- ✅ [USn] 标签：标记用户故事（Phase 2-5）
- ✅ 描述：包含具体的文件路径

**总计任务数**：56 个任务
- Phase 1: 10 个任务（Setup）
- Phase 2 (US1): 4 个任务
- Phase 3 (US2): 6 个任务
- Phase 4 (US3): 4 个任务
- Phase 5 (US4): 4 个任务
- Phase 6: 6 个任务（Polish）

**并行机会**：3 个并行任务组（Phase 1 模型创建、Phase 2+3、Phase 6）

---

## Next Steps

1. **开始实施**：
   ```bash
   /ralph-loop "实现 Phase 2.2 学习管理系统，按 specs/001-learning-management/tasks.md 任务清单"
   ```

2. **或使用 Task-Master 集成**：
   ```bash
   tm import tasks.md
   tm autopilot start T001
   ```

3. **或手动执行任务**：
   - 从 Phase 1 开始
   - 完成每个任务后更新 tasks.md 中的复选框
   - 遵循 TDD 流程（Red → Green → Refactor）

---

**Document Status**: ✅ Ready for Implementation
**Last Updated**: 2025-01-12
