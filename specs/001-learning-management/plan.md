# Implementation Plan: 小芽家教 Phase 2.2 学习管理系统

**Branch**: `001-learning-management` | **Date**: 2025-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-learning-management/spec.md`

## Summary

实现小芽家教的学习管理系统，包括四个核心功能：学习记录追踪、苏格拉底式引导教学、错题本管理和知识点图谱追踪。

**主要需求**：
- 为一年级学生（6-7岁）提供学习活动记录和进度分析
- 通过苏格拉底式提问引导学生思考，避免直接给出答案
- 智能分类错题并提供针对性练习推荐
- 建立知识点依赖关系图，追踪学生掌握程度

**技术方法**：
- 基于现有 FastAPI 后端架构扩展
- 集成 Claude API 生成引导式教学响应
- 使用 SQLAlchemy ORM 扩展数据模型
- 实现响应验证系统确保教育质量

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic v2, Claude API (Anthropic SDK)
**Storage**: SQLite (开发) / PostgreSQL (生产)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux 服务器
**Project Type**: Web 应用（后端 API）
**Performance Goals**:
- API 响应时间（p95）< 200ms
- 支持 1000 并发学生同时记录学习活动
- 引导式反馈生成时间 < 3秒（包含 Claude API 调用）

**Constraints**:
- 必须与 Phase 2.1 用户认证系统集成
- 儿童数据必须加密存储
- 响应内容不得包含直接答案（苏格拉底教学原则）
- 知识点依赖关系必须形成有向无环图（DAG）

**Scale/Scope**:
- 一年级数学核心知识点：至少 20 个
- 支持 4 种错误类型分类
- 7 种引导类型（澄清、提示、分解、可视化、检查、替代方法、鼓励）
- 学习数据保留期限：6 个月

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**参考项目宪章**：[.specify/memory/constitution.md](../../.specify/memory/constitution.md)

### 核心价值观检查

- [x] **规范先于代码**：✅ 规范文档已完成 (`specs/001-learning-management/spec.md`)
- [x] **质量不可妥协**：✅ 测试覆盖率目标 ≥ 80%（所有单元测试必须通过）
- [x] **用户价值至上**：✅ 优先考虑一年级学生的认知能力（苏格拉底式引导教学）
- [x] **透明可追溯**：✅ 可追溯到规范文档和后续 Task ID

### 不可违反的原则检查

- [x] **P1: 规范完整性**：✅ 规范包含所有必需章节（用户场景、需求、成功标准、假设）
- [x] **P2: TDD 强制执行**：✅ 遵循 Red-Green-Refactor 循环（红灯→绿灯→重构）
- [x] **P3: 安全优先**：✅ 考虑安全要求（儿童数据加密存储、权限控制）
- [x] **P4: 性能合约**：✅ API 响应时间 < 200ms (SC-004)
- [x] **P5: 向后兼容**：✅ 无破坏性变更（基于 Phase 2.1 用户系统扩展）
- [x] **P6: 代码一致性**：✅ 实施计划与规范一致（4 个核心功能）

## Project Structure

### Documentation (this feature)

```text
specs/001-learning-management/
├── spec.md              # 功能规范文档
├── plan.md              # 本文件 (/speckit.plan 命令输出)
├── research.md          # Phase 0 输出 (/speckit.plan 命令)
├── data-model.md        # Phase 1 输出 (/speckit.plan 命令)
├── quickstart.md        # Phase 1 输出 (/speckit.plan 命令)
├── contracts/           # Phase 1 输出 (/speckit.plan 命令)
│   ├── learning-api.yaml      # 学习记录 API 契约
│   ├── teaching-api.yaml      # 引导教学 API 契约
│   ├── wrong-answers-api.yaml # 错题本 API 契约
│   └── knowledge-api.yaml     # 知识点 API 契约
└── checklists/
    └── requirements.md        # 规范质量检查清单
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── learning.py              # 学习记录 API 端点 (已存在，需扩展)
│   │   ├── teaching.py              # 引导教学 API 端点 (新建)
│   │   ├── wrong_answers.py         # 错题本 API 端点 (新建)
│   │   └── knowledge.py             # 知识点 API 端点 (新建)
│   ├── models/
│   │   ├── learning.py              # 学习记录模型 (已存在，需扩展)
│   │   ├── wrong_answer.py          # 错题记录模型 (新建)
│   │   ├── knowledge_point.py       # 知识点模型 (新建)
│   │   └── knowledge_mastery.py     # 知识点掌握模型 (新建)
│   ├── services/
│   │   ├── learning_tracker.py      # 学习追踪服务 (已存在，需扩展)
│   │   ├── socratic_teacher.py      # 苏格拉底教学服务 (新建)
│   │   ├── wrong_analyzer.py        # 错误分析服务 (新建)
│   │   ├── practice_recommender.py  # 练习推荐服务 (新建)
│   │   └── knowledge_tracker.py     # 知识点追踪服务 (新建)
│   └── core/
│       └── security.py              # 安全模块（儿童数据加密）
└── tests/
    ├── unit/
    │   ├── test_learning_tracker.py     # 学习追踪单元测试 (已存在)
    │   ├── test_socratic_teacher.py     # 苏格拉底教学测试 (新建)
    │   ├── test_wrong_analyzer.py       # 错误分析测试 (新建)
    │   └── test_knowledge_tracker.py    # 知识点追踪测试 (新建)
    ├── integration/
    │   ├── test_teaching_flow.py        # 教学流程集成测试 (新建)
    │   └── test_knowledge_graph.py      # 知识图谱集成测试 (新建)
    └── contract/
        └── test_api_contracts.py        # API 契约测试 (新建)
```

**Structure Decision**: 选择 Web 应用架构（Option 2），因为：
1. 项目已有 frontend/ 和 backend/ 目录结构
2. Phase 2.1 已完成用户系统和数据库集成
3. 后端采用 FastAPI，前端采用 React
4. 本功能专注于后端 API 扩展，前端由其他分支负责

---

## Phase 0: Research & Technology Decisions

本阶段研究技术实现方案，解决关键技术问题。

### Research Tasks

基于 Technical Context 和功能规范，需要研究以下技术问题：

1. **Claude API 集成方案**
   - 如何使用 Anthropic SDK 生成苏格拉底式引导响应
   - 提示词工程最佳实践（确保不直接给答案）
   - API 调用性能优化（目标 < 3 秒响应）

2. **响应验证系统**
   - 如何检测响应中包含直接答案
   - 正则表达式和关键词匹配策略
   - 验证失败的重试机制

3. **错误答案分类算法**
   - 计算错误 vs 概念错误的识别规则
   - 基于答案特征的分类策略
   - 初期规则引擎 + 后期 AI 模型的混合方案

4. **知识点 DAG 结构**
   - 一年级数学知识点依赖关系设计
   - 如何在数据库中存储和查询 DAG
   - 掌握度计算算法

5. **儿童数据安全**
   - 加密存储方案（字段级加密）
   - 与 Phase 2.1 认证系统的权限集成

### Research Findings

#### R1: Claude API 集成方案

**Decision**: 使用 Anthropic Python SDK + 结构化提示词

**Rationale**:
- Anthropic SDK 提供官方 Python 绑定，支持异步调用
- 结构化提示词可以确保 Claude 理解苏格拉底教学原则
- 通过系统提示词约束，Claude 可以生成符合要求的引导式反馈

**Implementation Strategy**:
```python
# 系统提示词模板
SYSTEM_PROMPT = """
你是一位小学一年级数学老师，使用苏格拉底式教学方法。
当学生答错时，**绝对不要直接给出正确答案**。
而是通过提问引导学生自己思考。

引导类型：
1. 澄清（clarify）：帮助学生理解题目意思
2. 提示（hint）：给出关键提示但不给答案
3. 分解（break down）：将复杂问题分解为简单步骤
4. 可视化（visualize）：建议用画图或实物演示
5. 检查（check work）：引导学生检查自己的答案
6. 替代方法（alternative method）：建议其他解题思路
7. 鼓励（encourage）：给予正向激励

响应格式要求：
- 用简单易懂的语言（6-7岁儿童能理解）
- 每次只问1-2个问题
- 不要说"答案是X"或"正确答案是X"
"""
```

**Alternatives Considered**:
- OpenAI GPT-4: 功能类似，但本项目已决定使用 Claude
- 自建规则引擎: 无法提供足够灵活的引导，教育效果较差

---

#### R2: 响应验证系统

**Decision**: 多层验证机制（关键词检测 + 正则表达式 + AI 二次验证）

**Rationale**:
- 单层验证不够可靠，容易误判
- 多层验证可以提高准确率（目标 95% 符合 SC-003）

**Implementation Strategy**:
```python
class ResponseValidator:
    def validate_response(self, response: str, correct_answer: str) -> bool:
        """
        验证响应是否包含直接答案
        返回 True 表示验证通过（不包含直接答案）
        """
        # Layer 1: 关键词检测
        forbidden_patterns = [
            r"答案是\s*[0-9]+",
            r"正确答案是\s*[0-9]+",
            r"答案应该是\s*[0-9]+",
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, response):
                return False

        # Layer 2: 直接答案检测
        if correct_answer in response and "答案是" in response:
            return False

        # Layer 3: AI 二次验证（可选，提高准确率）
        # 使用 Claude 判断响应是否包含直接答案

        return True
```

**Alternatives Considered**:
- 仅关键词检测: 准确率不够高，可能遗漏变体
- 仅 AI 验证: 成本高，速度慢

---

#### R3: 错误答案分类算法

**Decision**: 规则引擎 + 答案差异分析

**Rationale**:
- 初期使用规则引擎快速实现
- 基于答案与正确答案的差异进行分类
- 后期可引入机器学习模型提升准确率

**Implementation Strategy**:
```python
class WrongAnswerClassifier:
    def classify(self, question: str, student_answer: str,
                 correct_answer: str) -> str:
        """
        分类错误答案类型
        返回: 'calculation' | 'concept' | 'understanding' | 'careless'
        """
        # 计算错误：答案接近但不正确
        if self._is_calculation_error(student_answer, correct_answer):
            return 'calculation'

        # 概念错误：答案显示对概念理解错误
        if self._is_concept_error(question, student_answer):
            return 'concept'

        # 理解错误：答案与题目要求不符
        if self._is_understanding_error(question, student_answer):
            return 'understanding'

        # 默认：粗心错误
        return 'careless'

    def _is_calculation_error(self, student: str, correct: str) -> bool:
        """判断是否为计算错误"""
        try:
            s_num = int(re.search(r'\d+', student).group())
            c_num = int(re.search(r'\d+', correct).group())
            return abs(s_num - c_num) <= 2  # 差距较小
        except:
            return False
```

**Alternatives Considered**:
- 纯 AI 分类: 准确率高但成本高，依赖外部服务
- 机器学习模型: 需要大量标注数据，初期不适用

---

#### R4: 知识点 DAG 结构

**Decision**: 邻接表存储 + 递归查询前置知识点

**Rationale**:
- 邻接表适合存储稀疏图（知识点依赖关系）
- 递归查询可以获取完整的前置知识点链
- SQLAlchemy 支持自引用关系

**Implementation Strategy**:
```python
class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(50), nullable=False)  # 'math', 'chinese', 'english'
    difficulty_level = Column(Integer, default=1)

    # 自引用关系（DAG）
    prerequisites = relationship(
        "KnowledgePoint",
        secondary="knowledge_point_dependencies",
        primaryjoin="KnowledgePoint.id == KnowledgePointDependency.knowledge_point_id",
        secondaryjoin="KnowledgePoint.id == KnowledgePointDependency.prerequisite_id",
        backref="dependents"
    )

class KnowledgePointDependency(Base):
    __tablename__ = "knowledge_point_dependencies"

    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey("knowledge_points.id"), primary_key=True)
```

**Alternatives Considered**:
- 路径枚举（Path Enumeration）: 查询前置方便，但更新困难
- 嵌套集（Nested Set）: 查询高效，但实现复杂

---

#### R5: 儿童数据安全

**Decision**: 字段级加密（AES-256）+ 访问控制列表

**Rationale**:
- 符合数据保护法规要求
- 与 Phase 2.1 用户系统集成，确保家长只能查看自己孩子的数据
- 加密敏感字段（学生答案、学习记录）

**Implementation Strategy**:
```python
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# 使用示例
class LearningRecord(Base):
    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True)
    student_answer = Column(String(500))  # 加密存储

    def set_answer(self, answer: str, encryption_service: EncryptionService):
        self.student_answer = encryption_service.encrypt(answer)
```

**Alternatives Considered**:
- 数据库级加密: 实现复杂，性能开销大
- 无加密: 不符合安全要求，违反 P3 原则

---

### Research Summary

所有关键技术问题已通过研究得出解决方案：

| 技术问题 | 决策方案 | 实现复杂度 | 风险等级 |
|---------|---------|-----------|---------|
| Claude API 集成 | Anthropic SDK + 结构化提示词 | 中 | 低 |
| 响应验证系统 | 多层验证机制 | 中 | 中 |
| 错误答案分类 | 规则引擎 + 差异分析 | 低 | 低 |
| 知识点 DAG | 邻接表 + 递归查询 | 中 | 低 |
| 儿童数据安全 | 字段级加密 + ACL | 中 | 低 |

**Conclusion**: 技术方案可行，可以进入 Phase 1 设计阶段。

---

## Phase 1: Design & Contracts

本阶段完成数据模型设计、API 契约定义和开发者文档。

### 1.1 Data Model Design

**Output**: [`data-model.md`](./data-model.md)

**核心实体**:
- **LearningRecord** (学习记录): 记录学生的答题活动
- **WrongAnswerRecord** (错题记录): 记录错误答案和引导式反馈
- **KnowledgePoint** (知识点): 定义一年级数学知识点结构
- **KnowledgeMastery** (知识点掌握): 追踪学生对知识点的掌握程度
- **KnowledgePointDependency** (知识点依赖关系): 记录知识点之间的依赖关系

**关键设计决策**:
- 使用 SQLAlchemy ORM 实现 5 个核心实体
- 邻接表存储知识点 DAG 结构
- 字段级加密保护儿童数据（AES-256）
- 15 个索引优化查询性能
- 复合索引加速多条件查询

---

### 1.2 API Contracts

**Output**: [`contracts/`](./contracts/) 目录

**已定义的 API 契约**:

#### 1. 学习记录 API (`learning-api.yaml`)
- `POST /learning/records` - 创建学习记录
- `GET /learning/records` - 查询学习记录列表
- `GET /learning/records/{record_id}` - 获取学习记录详情
- `GET /learning/progress` - 获取学习进度统计
- `GET /learning/report` - 生成学习进度报告

#### 2. 苏格拉底式引导教学 API (`teaching-api.yaml`)
- `POST /teaching/guidance` - 生成引导式反馈
- `POST /teaching/guidance/validate` - 验证引导式反馈
- `GET /teaching/guidance/types` - 获取引导类型列表

#### 3. 错题本 API (`wrong-answers-api.yaml`)
- `GET /wrong-answers` - 查询错题列表
- `GET /wrong-answers/{wrong_answer_id}` - 获取错题详情
- `PATCH /wrong-answers/{wrong_answer_id}` - 更新错题状态
- `GET /wrong-answers/statistics` - 获取错题统计
- `GET /wrong-answers/recommendations` - 获取练习推荐

#### 4. 知识点图谱 API (`knowledge-api.yaml`)
- `GET /knowledge-points` - 查询知识点列表
- `GET /knowledge-points/{knowledge_point_id}` - 获取知识点详情
- `GET /knowledge-points/graph` - 获取知识点图谱
- `GET /knowledge-mastery` - 查询学生知识点掌握情况
- `GET /knowledge-mastery/{mastery_id}` - 获取知识点掌握详情
- `PATCH /knowledge-mastery/{mastery_id}` - 更新知识点掌握度
- `GET /knowledge-mastery/recommendations` - 获取学习路径推荐

**API 设计原则**:
- RESTful 风格
- 统一的响应格式
- JWT 认证
- 权限控制（家长只能访问自己孩子的数据）
- OpenAPI 3.0 规范

---

### 1.3 Developer Documentation

**Output**: [`quickstart.md`](./quickstart.md)

**内容包括**:
- 前置条件和环境配置
- 安装步骤
- 核心 API 使用示例
- 开发指南
- 常见问题解答
- 调试技巧

---

### 1.4 Agent Context Update

**Status**: ✅ 完成

已更新 Claude Code agent 上下文文件 (`CLAUDE.md`)，添加了：
- 语言：Python 3.11+
- 框架：FastAPI, SQLAlchemy, Pydantic v2, Claude API
- 数据库：SQLite (开发) / PostgreSQL (生产)

---

## Phase 1 Completion Report

### Deliverables Summary

| 交付物 | 状态 | 路径 |
|--------|------|------|
| 研究文档 | ✅ 完成 | [`research.md`](./research.md) |
| 数据模型设计 | ✅ 完成 | [`data-model.md`](./data-model.md) |
| API 契约（学习记录） | ✅ 完成 | [`contracts/learning-api.yaml`](./contracts/learning-api.yaml) |
| API 契约（引导教学） | ✅ 完成 | [`contracts/teaching-api.yaml`](./contracts/teaching-api.yaml) |
| API 契约（错题本） | ✅ 完成 | [`contracts/wrong-answers-api.yaml`](./contracts/wrong-answers-api.yaml) |
| API 契约（知识点图谱） | ✅ 完成 | [`contracts/knowledge-api.yaml`](./contracts/knowledge-api.yaml) |
| 快速开始指南 | ✅ 完成 | [`quickstart.md`](./quickstart.md) |
| Agent 上下文更新 | ✅ 完成 | `CLAUDE.md` |

### Constitution Re-Check (Phase 1 后)

所有宪章检查项继续通过：

- ✅ **规范先于代码**: 完整的设计文档已生成
- ✅ **质量不可妥协**: 测试覆盖率目标 ≥ 80%
- ✅ **用户价值至上**: 苏格拉底式引导教学符合一年级学生认知能力
- ✅ **透明可追溯**: 所有设计决策有据可查

- ✅ **P1: 规范完整性**: 数据模型、API 契约完整
- ✅ **P2: TDD 强制执行**: 下一步实施阶段将遵循 Red-Green-Refactor
- ✅ **P3: 安全优先**: 儿童数据加密存储、权限控制已设计
- ✅ **P4: 性能合约**: API 响应时间 < 200ms，索引已优化
- ✅ **P5: 向后兼容**: 基于 Phase 2.1 用户系统扩展
- ✅ **P6: 代码一致性**: 设计与规范一致

---

## Next Steps

### Phase 2: Task Generation

使用 `/speckit.tasks` 命令生成实施任务清单：

```bash
/speckit.tasks
```

这将生成：
1. 按依赖顺序排列的任务列表
2. 每个任务包含明确的验收标准
3. 任务优先级（P1 > P2）

### Phase 3: Implementation

使用 Ralph Loop 进行迭代实施：

```bash
/ralph-loop "实现 Phase 2.2 学习管理系统，按 specs/001-learning-management/plan.md 规范"
```

实施顺序：
1. **Phase 3.1**: 扩展学习记录 API（基于现有代码）
2. **Phase 3.2**: 实现苏格拉底式引导教学 API（核心功能）
3. **Phase 3.3**: 实现错题本 CRUD API
4. **Phase 3.4**: 实现知识点图谱数据模型和 API
5. **Phase 3.5**: 编写单元测试（覆盖率 ≥ 80%）
6. **Phase 3.6**: 集成测试和性能优化

---

## Appendix

### A. Related Documents

- [功能规范](./spec.md)
- [规范质量检查清单](./checklists/requirements.md)
- [项目宪章](../../.specify/memory/constitution.md)

### B. External References

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [Anthropic Claude API 文档](https://docs.anthropic.com/)
- [OpenAPI 3.0 规范](https://swagger.io/specification/)

### C. Version History

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | 2025-01-12 | 初始版本，完成 Phase 0 和 Phase 1 设计 |

---

**Plan Status**: ✅ Phase 0 & Phase 1 完成，等待进入 Phase 2 (Task Generation)
