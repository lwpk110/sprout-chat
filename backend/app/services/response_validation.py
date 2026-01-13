"""
响应验证服务 (LWP-16)

多维度验证系统，确保 AI 生成的响应真正符合苏格拉底教学法
"""
import re
import asyncio
from typing import Optional, List
from app.core.ai_service import get_ai_service
from app.core.config import settings
from app.models.validation import (
    ValidationResult,
    StudentContext,
    ValidationRequest
)
from app.models.socratic import ScaffoldingLevel


class ResponseValidationService:
    """
    响应验证服务

    五维验证系统：
    1. 引导性问题检测 (pattern-based)
    2. 直接答案检测 (pattern-based + AI-based)
    3. 脚手架层级对齐检测 (pattern-based)
    4. 问题质量评估 (AI-based)
    5. 上下文相关性验证 (AI-based)
    """

    # 引导问题引导词
    GUIDING_WORDS = [
        "你觉得", "你为什么", "你怎么", "有没有", "会不会",
        "让我们", "一起", "想想", "试试", "看看"
    ]

    # 直接答案检测模式
    DIRECT_ANSWER_PATTERNS = [
        r"答案是\s*\d+",
        r"等于\s*\d+",
        r"应该是\s*\d+",
        r"就是\s*\d+",
        r"正确答案是",
        r"不对，.*?是\s*\d+",  # "不对，应该是 5"
        r"你应该",  # "你应该这样做..."
        r"你需要",  # "你需要..."
        r"这道题.*?答案是",  # "这道题的答案是..."
    ]

    # 脚手架层级特征词
    HIGHLY_GUIDED_KEYWORDS = [
        "先看看", "找一找", "数一数", "让我们", "第一步", "第二步",
        "你找到了", "有几个"
    ]

    MODERATE_GUIDED_KEYWORDS = [
        "你觉得", "为什么", "怎么", "哪一步", "为什么"
    ]

    MINIMAL_GUIDED_KEYWORDS = [
        "还有", "其他", "方法", "思路", "很好", "不错"
    ]

    def __init__(self):
        """初始化服务"""
        self.ai_client = None

    def _get_ai_client(self):
        """获取 AI 客户端（延迟加载）"""
        if self.ai_client is None:
            self.ai_client = get_ai_service()
        return self.ai_client

    # ========== 维度 1: 引导性问题检测 ==========

    def _contains_guiding_questions(self, response: str) -> bool:
        """
        检测响应是否包含引导性问题

        规则：
        - 包含问号
        - 包含引导词："你觉得"、"为什么"、"怎么"、"有没有"
        - 问题开放性（不是是/否问题）
        """
        # 检查是否包含问号
        has_question_mark = "？" in response or "?" in response

        # 检查是否包含引导词
        has_guiding_words = any(word in response for word in self.GUIDING_WORDS)

        return has_question_mark or has_guiding_words

    def _calculate_guiding_question_score(self, response: str) -> float:
        """
        计算引导问题得分

        评分标准：
        - 包含问号: +0.5
        - 包含引导词: +0.3
        - 引导词数量多: +0.2
        """
        score = 0.0

        # 包含问号
        if "？" in response or "?" in response:
            score += 0.5

        # 包含引导词
        guiding_words_count = sum(1 for word in self.GUIDING_WORDS if word in response)
        if guiding_words_count > 0:
            score += 0.3
            if guiding_words_count >= 2:
                score += 0.2  # 多个引导词加分

        return min(1.0, score)

    # ========== 维度 2: 直接答案检测 ==========

    def _contains_direct_answers(self, response: str) -> bool:
        """
        检测响应是否包含直接答案

        模式检测：
        - "答案是"、"等于"、"结果是"
        - "你应该"、"你需要"
        - "正确答案是"、"不对，应该是"
        """
        for pattern in self.DIRECT_ANSWER_PATTERNS:
            if re.search(pattern, response):
                return True
        return False

    # ========== 维度 3: 脚手架层级对齐 ==========

    def _validate_scaffolding_alignment(
        self,
        response: str,
        expected_level: ScaffoldingLevel
    ) -> float:
        """
        验证响应的引导级别是否符合预期的脚手架层级

        highly_guided: 应包含具体提示、分解步骤
        moderate: 开放式问题 + 必要时的小提示
        minimal: 开放式问题，无具体提示
        """
        score = 0.0

        if expected_level == ScaffoldingLevel.HIGHLY_GUIDED:
            # 高度引导：应该包含具体步骤或提示
            has_guided_keywords = any(word in response for word in self.HIGHLY_GUIDED_KEYWORDS)
            has_question = "？" in response or "?" in response

            if has_guided_keywords and has_question:
                score = 1.0
            elif has_guided_keywords or has_question:
                score = 0.5  # 降低分数，只有其中一个不够
            else:
                score = 0.2

        elif expected_level == ScaffoldingLevel.MODERATE:
            # 中度引导：开放式问题
            has_moderate_keywords = any(word in response for word in self.MODERATE_GUIDED_KEYWORDS)
            has_question = "？" in response or "?" in response

            if has_moderate_keywords and has_question:
                score = 1.0
            elif has_question:
                score = 0.7
            else:
                score = 0.4

        elif expected_level == ScaffoldingLevel.MINIMAL:
            # 最小引导：简洁开放
            has_minimal_keywords = any(word in response for word in self.MINIMAL_GUIDED_KEYWORDS)
            has_question = "？" in response or "?" in response
            response_length = len(response)

            # 简洁且开放
            if response_length <= 50 and has_question:
                score = 1.0
            elif response_length <= 100 and has_question:
                score = 0.7
            else:
                score = 0.5

        return score

    # ========== 维度 4: 问题质量评估 (AI-based) ==========

    async def _assess_question_quality(
        self,
        response: str,
        student_context: StudentContext
    ) -> float:
        """
        评估引导问题的质量

        评估标准：
        - 问题是否适合学生年级（一年级）
        - 问题是否基于学生之前的工作
        - 问题是否鼓励元认知（思考关于思考）
        - 问题是否指向学习目标而不泄露答案
        """
        try:
            # 构建评估提示
            prompt = f"""
请评估以下家教响应的质量（0.0 - 1.0 分）。

**学生信息**：
- 年级：{student_context.grade}
- 问题类型：{student_context.problem_type}
- 之前尝试：{", ".join(student_context.previous_attempts) if student_context.previous_attempts else "无"}

**家教响应**：
{response}

**评估标准**：
1. 是否适合一年级学生（语言简单、具体）
2. 是否鼓励学生思考（不直接给答案）
3. 是否基于学生的具体问题（不是通用模板）
4. 是否温柔鼓励（不严厉、不轻视）

**输出格式**（只输出分数）：
0.XX
"""

            client = self._get_ai_client()

            # 调用 AI 评估
            if settings.ai_provider == "anthropic":
                ai_response = await client.messages.create(
                    model=settings.ai_model,
                    max_tokens=50,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                score_text = ai_response.content[0].text.strip()
            else:
                ai_response = await client.chat.completions.create(
                    model=settings.ai_model,
                    max_tokens=50,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                score_text = ai_response.choices[0].message.content.strip()

            # 解析分数
            score = float(re.search(r"0\.\d+|1\.0", score_text).group())
            return max(0.0, min(1.0, score))

        except Exception as e:
            # AI 调用失败，返回默认分数
            print(f"Warning: AI quality assessment failed: {e}")
            # 检查响应长度，如果很长可能是过于复杂
            if len(response) > 100:
                return 0.4  # 长响应可能是复杂的
            return 0.6  # 默认给予及格分数

    # ========== 维度 5: 上下文相关性 (AI-based) ==========

    async def _verify_context_relevance(
        self,
        response: str,
        student_context: StudentContext
    ) -> bool:
        """
        验证响应是否与学生的具体问题和上下文相关

        检查：
        - 响应是否引用了学生的具体工作
        - 响应是否针对学生的问题
        - 响应是否过于通用（可以应用到任何问题）
        """
        try:
            # 构建相关性检查提示
            prompt = f"""
判断以下家教响应是否与学生的具体问题和上下文相关。

**学生信息**：
- 年级：{student_context.grade}
- 问题类型：{student_context.problem_type}
- 之前尝试：{", ".join(student_context.previous_attempts) if student_context.previous_attempts else "无"}

**家教响应**：
{response}

**判断标准**：
1. 响应是否引用了学生的具体尝试或错误？
2. 响应是否针对这个具体问题（而不是通用模板）？
3. 响应是否考虑到学生的年级水平？

**输出格式**（只输出 "relevant" 或 "generic"）：
"""

            client = self._get_ai_client()

            # 调用 AI 检查
            if settings.ai_provider == "anthropic":
                ai_response = await client.messages.create(
                    model=settings.ai_model,
                    max_tokens=10,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = ai_response.content[0].text.strip().lower()
            else:
                ai_response = await client.chat.completions.create(
                    model=settings.ai_model,
                    max_tokens=10,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = ai_response.choices[0].message.content.strip().lower()

            # 解析结果
            return "relevant" in result

        except Exception as e:
            # AI 调用失败，默认返回 True（不过度严格）
            print(f"Warning: AI relevance check failed: {e}")
            return True

    # ========== 整体验证 ==========

    async def validate_socratic_response(
        self,
        response: str,
        scaffolding_level: ScaffoldingLevel,
        student_context: Optional[StudentContext] = None
    ) -> ValidationResult:
        """
        多维度验证响应是否符合苏格拉底教学法

        Args:
            response: 待验证的响应
            scaffolding_level: 预期的脚手架层级
            student_context: 学生上下文信息

        Returns:
            ValidationResult
        """
        if student_context is None:
            student_context = StudentContext()

        # 维度 1: 引导性问题检测
        guiding_question_score = self._calculate_guiding_question_score(response)

        # 维度 2: 直接答案检测
        direct_answer_violation = self._contains_direct_answers(response)

        # 维度 3: 脚手架层级对齐
        scaffolding_alignment_score = self._validate_scaffolding_alignment(
            response,
            scaffolding_level
        )

        # 维度 4 & 5: AI 验证（并行执行）
        question_quality_score, context_relevance_score = await asyncio.gather(
            self._assess_question_quality(response, student_context),
            self._verify_context_relevance(response, student_context),
            return_exceptions=True
        )

        # 处理 AI 调用可能的异常
        if isinstance(question_quality_score, Exception):
            print(f"Warning: Quality assessment failed: {question_quality_score}")
            question_quality_score = 0.7

        if isinstance(context_relevance_score, Exception):
            print(f"Warning: Relevance check failed: {context_relevance_score}")
            context_relevance_score = 1.0  # 转换为分数

        # 如果 context_relevance_score 是 bool，转换为 float
        if isinstance(context_relevance_score, bool):
            context_relevance_score = 1.0 if context_relevance_score else 0.5

        # 计算综合分数（加权平均）
        weights = {
            "guiding": 0.25,
            "direct": 0.30,  # 直接答案最重要
            "scaffolding": 0.20,
            "quality": 0.15,
            "relevance": 0.10
        }

        overall_score = (
            guiding_question_score * weights["guiding"] +
            (0.0 if direct_answer_violation else 1.0) * weights["direct"] +
            scaffolding_alignment_score * weights["scaffolding"] +
            question_quality_score * weights["quality"] +
            context_relevance_score * weights["relevance"]
        )

        # 判断是否有效
        is_valid = (
            not direct_answer_violation and
            guiding_question_score >= 0.5 and
            overall_score >= 0.6
        )

        # 收集失败原因
        failure_reasons = []
        if direct_answer_violation:
            failure_reasons.append("包含直接答案")
        if guiding_question_score < 0.5:
            failure_reasons.append("缺少引导性问题")
        if scaffolding_alignment_score < 0.6:
            failure_reasons.append("脚手架层级不对齐")
        if question_quality_score < 0.6:
            failure_reasons.append("问题质量不高")
        if context_relevance_score < 0.6:
            failure_reasons.append("上下文相关性不足")

        # 生成改进建议
        suggestions = []
        if direct_answer_violation:
            suggestions.append("移除直接答案，改用引导性问题")
        if guiding_question_score < 0.5:
            suggestions.append("添加引导性问题，如'你觉得...'、'为什么...'")
        if scaffolding_alignment_score < 0.6:
            suggestions.append("调整引导层级以匹配预期脚手架")
        if question_quality_score < 0.6:
            suggestions.append("简化语言，确保适合一年级学生")
        if context_relevance_score < 0.6:
            suggestions.append("引用学生的具体尝试或问题")

        return ValidationResult(
            is_valid=is_valid,
            overall_score=overall_score,
            guiding_question_score=guiding_question_score,
            direct_answer_violation=direct_answer_violation,
            scaffolding_alignment_score=scaffolding_alignment_score,
            question_quality_score=question_quality_score,
            context_relevance_score=context_relevance_score,
            failure_reasons=failure_reasons,
            suggestions=suggestions
        )


# 便捷函数
def create_validation_service() -> ResponseValidationService:
    """创建响应验证服务实例"""
    return ResponseValidationService()
