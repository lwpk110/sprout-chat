"""
苏格拉底教学服务（Phase 2.2 - US2）

实现苏格拉底式引导教学，通过提问引导学生思考，而不是直接给出答案。

注意：AI 服务集成已在 socratic_response.py 中的 SocraticResponseService 实现
"""

from typing import Dict, Any, List
from app.services.wrong_analyzer import WrongAnswerClassifier
from app.services.response_validator import ResponseValidator
# AI 服务集成已在其他模块实现
# from app.core.ai_service import get_ai_service


class SocraticTeacherService:
    """
    苏格拉底教学服务

    根据学生的错误答案，生成引导式反馈，帮助学生自己思考找到正确答案。

    支持的引导类型（7 种）：
    - clarify: 澄清型（澄清学生的理解）
    - hint: 提示型（给出提示但不直接给答案）
    - break_down: 分解型（将问题分解为小步骤）
    - visualize: 可视化型（建议用画图等可视化方式）
    - check_work: 检查型（引导学生检查自己的答案）
    - alternative_method: 替代方法型（建议用其他方法）
    - encourage: 鼓励型（给予鼓励和信心）
    """

    # 错误类型到引导类型的映射（首次尝试）
    ERROR_TYPE_TO_GUIDANCE = {
        "calculation": ["hint", "check_work"],
        "concept": ["clarify", "break_down"],
        "understanding": ["clarify"],
        "careless": ["check_work", "encourage"],
    }

    # 多次尝试后的引导类型映射
    RETRY_GUIDANCE = {
        "calculation": ["break_down", "visualize"],
        "concept": ["visualize", "alternative_method"],
        "understanding": ["break_down", "hint"],
        "careless": ["encourage", "check_work"],
    }

    # 系统提示词模板（简化版）
    SYSTEM_PROMPTS = {
        "clarify": """你是苏格拉底式教师。通过提问澄清学生的理解，不要直接给出答案。

问题：{question}
学生答案：{student_answer}

请通过提问帮助学生理解题意，引导他们自己思考。""",
        "hint": """你是苏格拉底式教师。通过提示引导学生思考，不要直接给出答案。

问题：{question}
学生答案：{student_answer}

请给出有针对性的提示，帮助学生找到正确答案。""",
        "break_down": """你是苏格拉底式教师。将复杂问题分解为简单步骤，引导学生逐步解决。

问题：{question}
学生答案：{student_answer}

请将问题分解为小步骤，引导学生一步步思考。""",
        "visualize": """你是苏格拉底式教师。建议学生用可视化方式（画图、用实物等）帮助理解。

问题：{question}
学生答案：{student_answer}

请建议学生用画图或实物模拟的方式理解问题。""",
        "check_work": """你是苏格拉底式教师。引导学生检查自己的答案和解题过程。

问题：{question}
学生答案：{student_answer}

请引导学生检查自己的答案，找出可能的问题。""",
        "alternative_method": """你是苏格拉底式教师。建议学生尝试不同的解题方法。

问题：{question}
学生答案：{student_answer}

请建议学生用其他方法思考这个问题，帮助找到正确答案。""",
        "encourage": """你是苏格拉底式教师。给予学生鼓励，建立信心，同时引导思考。

问题：{question}
学生答案：{student_answer}

请鼓励学生继续思考，并给予一些方向性的提示。""",
    }

    def __init__(self):
        """初始化苏格拉底教学服务"""
        self.classifier = WrongAnswerClassifier()
        self.validator = ResponseValidator()

    def generate_guidance(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        error_type: str,
        attempts: int = 1
    ) -> Dict[str, Any]:
        """
        生成引导式反馈

        Args:
            question: 问题内容
            student_answer: 学生答案
            correct_answer: 正确答案
            error_type: 错误类型
            attempts: 尝试次数

        Returns:
            引导式反馈：{"guidance_type": str, "content": str, "metadata": dict}
        """
        # 选择引导类型
        guidance_type = self._select_guidance_type(error_type, attempts)

        # 构建系统提示词
        system_prompt = self._build_system_prompt(
            guidance_type=guidance_type,
            question=question,
            student_answer=student_answer,
            error_type=error_type
        )

        # 调用 AI 服务生成引导内容
        # 注意：Claude API 调用已在 socratic_response.py 的 SocraticResponseService 中实现
        # 这里使用模拟数据作为快速测试实现
        guidance_content = self._generate_mock_guidance(
            guidance_type=guidance_type,
            question=question,
            student_answer=student_answer
        )

        # 验证响应不包含直接答案
        validation_result = self.validator.validate_response(
            response=guidance_content,
            correct_answer=correct_answer,
            question=question
        )

        if not validation_result["valid"]:
            # 如果验证失败，使用更安全的默认引导
            guidance_content = self._get_fallback_guidance(question)

        return {
            "guidance_type": guidance_type,
            "content": guidance_content,
            "metadata": {
                "error_type": error_type,
                "attempts": attempts,
                "validation_result": validation_result
            }
        }

    def _select_guidance_type(self, error_type: str, attempts: int) -> str:
        """
        选择引导类型

        Args:
            error_type: 错误类型
            attempts: 尝试次数

        Returns:
            引导类型
        """
        if attempts <= 2:
            # 首次或早期尝试：使用标准映射
            candidates = self.ERROR_TYPE_TO_GUIDANCE.get(error_type, ["hint"])
        else:
            # 多次尝试后：使用更强的引导
            candidates = self.RETRY_GUIDANCE.get(error_type, ["break_down"])

        # 返回第一个候选（可以优化为随机选择）
        return candidates[0]

    def _build_system_prompt(
        self,
        guidance_type: str,
        question: str,
        student_answer: str,
        error_type: str
    ) -> str:
        """
        构建系统提示词

        Args:
            guidance_type: 引导类型
            question: 问题内容
            student_answer: 学生答案
            error_type: 错误类型

        Returns:
            系统提示词
        """
        template = self.SYSTEM_PROMPTS.get(guidance_type, self.SYSTEM_PROMPTS["hint"])
        return template.format(
            question=question,
            student_answer=student_answer
        )

    def _generate_mock_guidance(
        self,
        guidance_type: str,
        question: str,
        student_answer: str
    ) -> str:
        """
        生成模拟引导内容（用于测试）

        注意：实际 AI 调用已在 socratic_response.py 的 SocraticResponseService 中实现

        Args:
            guidance_type: 引导类型
            question: 问题内容
            student_answer: 学生答案

        Returns:
            引导内容
        """
        # 简化的引导内容生成
        mock_guidance = {
            "clarify": f"让我确认一下你的理解。题目说的是什么呢？",
            "hint": f"让我来帮你想一想。要不要试试用手指或画图的方式数一数？",
            "break_down": f"我们把这个问题分解一下。先看第一步应该做什么？",
            "visualize": f"我们可以画个图来理解这个问题。要不要试试？",
            "check_work": f"让我帮你检查一下。你能不能再数一遍，看看是不是正确？",
            "alternative_method": f"让我们试试另一种方法。也许换个角度思考这个问题？",
            "encourage": f"你已经很接近了！继续加油，再试一次？",
        }

        return mock_guidance.get(guidance_type, "让我来帮你想一想。")

    def _get_fallback_guidance(self, question: str) -> str:
        """
        获取后备引导内容（当验证失败时使用）

        Args:
            question: 问题内容

        Returns:
            安全的引导内容
        """
        return "让我来帮你想一想。能不能用自己的话说说，这个问题在问什么？"
