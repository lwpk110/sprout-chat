# Research & Technology Decisions: Phase 2.2 学习管理系统

**Feature**: 小芽家教 Phase 2.2 学习管理系统
**Date**: 2025-01-12
**Status**: ✅ 完成

## Overview

本文档记录 Phase 2.2 学习管理系统的技术研究和决策，涵盖 Claude API 集成、响应验证、错误分类、知识点图谱和数据安全等关键技术问题。

---

## Research Topics

### 1. Claude API 集成方案

**问题**: 如何使用 Anthropic SDK 生成苏格拉底式引导响应？

**决策**: 使用 Anthropic Python SDK + 结构化提示词

**理由**:
- Anthropic SDK 提供官方 Python 绑定，支持异步调用
- 结构化提示词可以确保 Claude 理解苏格拉底教学原则
- 通过系统提示词约束，Claude 可以生成符合要求的引导式反馈

**实现策略**:
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

**替代方案**:
- OpenAI GPT-4: 功能类似，但本项目已决定使用 Claude
- 自建规则引擎: 无法提供足够灵活的引导，教育效果较差

---

### 2. 响应验证系统

**问题**: 如何检测响应中包含直接答案？

**决策**: 多层验证机制（关键词检测 + 正则表达式 + AI 二次验证）

**理由**:
- 单层验证不够可靠，容易误判
- 多层验证可以提高准确率（目标 95% 符合 SC-003）

**实现策略**:
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

**替代方案**:
- 仅关键词检测: 准确率不够高，可能遗漏变体
- 仅 AI 验证: 成本高，速度慢

---

### 3. 错误答案分类算法

**问题**: 如何分类计算错误 vs 概念错误？

**决策**: 规则引擎 + 答案差异分析

**理由**:
- 初期使用规则引擎快速实现
- 基于答案与正确答案的差异进行分类
- 后期可引入机器学习模型提升准确率

**实现策略**:
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

**替代方案**:
- 纯 AI 分类: 准确率高但成本高，依赖外部服务
- 机器学习模型: 需要大量标注数据，初期不适用

---

### 4. 知识点 DAG 结构

**问题**: 如何在数据库中存储和查询知识点依赖关系？

**决策**: 邻接表存储 + 递归查询前置知识点

**理由**:
- 邻接表适合存储稀疏图（知识点依赖关系）
- 递归查询可以获取完整的前置知识点链
- SQLAlchemy 支持自引用关系

**实现策略**:
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

**替代方案**:
- 路径枚举（Path Enumeration）: 查询前置方便，但更新困难
- 嵌套集（Nested Set）: 查询高效，但实现复杂

---

### 5. 儿童数据安全

**问题**: 如何确保儿童数据的安全存储？

**决策**: 字段级加密（AES-256）+ 访问控制列表

**理由**:
- 符合数据保护法规要求
- 与 Phase 2.1 用户系统集成，确保家长只能查看自己孩子的数据
- 加密敏感字段（学生答案、学习记录）

**实现策略**:
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

**替代方案**:
- 数据库级加密: 实现复杂，性能开销大
- 无加密: 不符合安全要求，违反 P3 原则

---

## Summary

| 技术问题 | 决策方案 | 实现复杂度 | 风险等级 |
|---------|---------|-----------|---------|
| Claude API 集成 | Anthropic SDK + 结构化提示词 | 中 | 低 |
| 响应验证系统 | 多层验证机制 | 中 | 中 |
| 错误答案分类 | 规则引擎 + 差异分析 | 低 | 低 |
| 知识点 DAG | 邻接表 + 递归查询 | 中 | 低 |
| 儿童数据安全 | 字段级加密 + ACL | 中 | 低 |

**Conclusion**: 所有技术方案已确定，可以进入 Phase 1 设计阶段。
