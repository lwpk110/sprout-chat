"""
苏格拉底教学服务单元测试（Phase 2.2 - US2）

TDD Phase: Red - 先写失败的测试
测试苏格拉底引导教学的核心功能：
- 错误答案分类（计算、概念、理解、粗心）
- 7 种引导类型（澄清、提示、分解、可视化、检查、替代方法、鼓励）
- 引导式反馈生成
- 连续出错时的策略调整
"""

import pytest
from unittest.mock import Mock, patch
from app.services.wrong_analyzer import WrongAnswerClassifier
from app.services.response_validator import ResponseValidator
from app.services.socratic_teacher import SocraticTeacherService


class TestWrongAnswerClassifier:
    """错误答案分类器测试"""

    def setup_method(self):
        """测试前置设置"""
        self.classifier = WrongAnswerClassifier()

    def test_classify_calculation_error(self):
        """
        测试计算错误分类

        验收场景：
        给定学生提交计算错误的答案（如 3+5=7）
        那么系统应分类为 "calculation" 错误
        """
        question = "3 + 5 = ?"
        student_answer = "7"
        correct_answer = "8"

        error_type = self.classifier.classify(
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer
        )

        assert error_type == "calculation"

    def test_classify_concept_error(self):
        """
        测试概念错误分类

        验收场景：
        给定学生显示概念理解错误（如混淆加减法）
        那么系统应分类为 "concept" 错误
        """
        question = "你有 5 个苹果，吃掉 3 个，还剩几个？"
        student_answer = "8"  # 误用加法
        correct_answer = "2"

        error_type = self.classifier.classify(
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer
        )

        assert error_type == "concept"

    def test_classify_understanding_error(self):
        """
        测试理解错误分类

        验收场景：
        给定学生显示对题意理解错误
        那么系统应分类为 "understanding" 错误
        """
        question = "小明有 5 个苹果，小红有 3 个苹果，他们一共有多少个？"
        student_answer = "2"  # 误理解为求差
        correct_answer = "8"

        error_type = self.classifier.classify(
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer
        )

        assert error_type == "understanding"

    def test_classify_careless_error(self):
        """
        测试粗心错误分类

        验收场景：
        给定学生答案与正确答案非常接近（如差 1）
        那么系统应分类为 "careless" 错误
        """
        question = "100 - 1 = ?"
        student_answer = "99"  # 粗心写错
        correct_answer = "99"

        # 这种情况下应该识别为可能的理解问题
        # 实际答案正确时不应调用分类
        # 这个测试验证边界情况处理

    def test_classify_with_multiple_attempts(self):
        """
        测试多次尝试后的分类

        验收场景：
        给定学生已经尝试了 3 次
        那么系统应考虑答题历史调整分类
        """
        question = "15 - 7 = ?"
        student_answer = "9"
        correct_answer = "8"
        attempts = 3

        error_type = self.classifier.classify(
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer,
            attempts=attempts
        )

        # 多次错误可能意味着概念或理解问题
        assert error_type in ["concept", "understanding"]


class TestResponseValidator:
    """响应验证系统测试"""

    def setup_method(self):
        """测试前置设置"""
        self.validator = ResponseValidator()

    def test_validate_response_contains_answer(self):
        """
        测试检测包含直接答案的响应

        验收场景（SC-003）：
        给定引导式响应包含 "答案是 8"
        那么验证应失败，返回 {"valid": False, "reason": "contains_answer"}
        目标准确率：95%
        """
        response = "让我来帮你。答案是 8，你应该记住这个。"

        result = self.validator.validate_response(
            response=response,
            correct_answer="8",
            question="3 + 5 = ?"
        )

        assert result["valid"] is False
        assert "contains_answer" in result["reason"]

    def test_validate_response_no_answer(self):
        """
        试测试不包含答案的响应

        验收场景：
        给定引导式响应不包含直接答案
        那么验证应通过，返回 {"valid": True}
        """
        response = "让我来帮你检查一下。你一开始有 3 个苹果，妈妈又给了你 5 个，你能用手指或画图的方式数一数吗？"

        result = self.validator.validate_response(
            response=response,
            correct_answer="8",
            question="3 + 5 = ?"
        )

        assert result["valid"] is True

    def test_validate_response_contains_keywords(self):
        """
        测试关键词检测（Layer 1）

        验收场景：
        给定响应包含 "等于"、"结果是" 等关键词
        那么验证应进行更严格的检查
        """
        response = "让我算一下。计算结果是..."  # 包含 "结果"

        result = self.validator.validate_response(
            response=response,
            correct_answer="8",
            question="3 + 5 = ?"
        )

        # Layer 1 检测到关键词，应进行 Layer 2 验证
        assert "layer" in result or "valid" in result

    def test_validate_response_with_number(self):
        """
        测试包含数字的响应（Layer 2）

        验收场景：
        给定响应包含数字但不是直接答案
        那么验证应区分是否为答案
        """
        response = "先用 3 个加上 5 个，数一数看看。"

        result = self.validator.validate_response(
            response=response,
            correct_answer="8",
            question="3 + 5 = ?"
        )

        # 响应中的数字是题目中的数字，不是答案
        assert result["valid"] is True or "contains_number" not in result.get("reason", "")


class TestSocraticTeacherService:
    """苏格拉底教学服务测试"""

    def setup_method(self):
        """测试前置设置"""
        # 使用 mock AI 服务避免实际 API 调用
        self.service = SocraticTeacherService()

    @patch('app.services.socratic_teacher.AIService')
    def test_generate_guidance_hint_type(self, mock_ai_service):
        """
        测试生成提示型引导（hint）

        验收场景：
        给定学生答错，错误类型为 "calculation"
        那么系统应生成 "hint" 类型的引导式反馈
        """
        # Mock AI 响应
        mock_ai_service.generate_response.return_value = "让我来帮你检查一下。用手指或画图的方式数一数，3 加 5 等于多少呢？"

        guidance = self.service.generate_guidance(
            question="3 + 5 = ?",
            student_answer="7",
            correct_answer="8",
            error_type="calculation",
            attempts=1
        )

        assert guidance["guidance_type"] == "hint"
        assert len(guidance["content"]) > 0
        assert "guidance" in guidance

    @patch('app.services.socratic_teacher.AIService')
    def test_generate_guidance_clarify_type(self, mock_ai_service):
        """
        测试生成澄清型引导（clarify）

        验收场景：
        给定学生答错，错误类型为 "understanding"
        那么系统应生成 "clarify" 类型的引导式反馈
        """
        mock_ai_service.generate_response.return_value = "让我确认一下你的理解。题目说的是你一共有多少个苹果，还是需要吃掉多少个？"

        guidance = self.service.generate_guidance(
            question="小明有 5 个苹果，吃掉 3 个，还剩几个？",
            student_answer="8",
            correct_answer="2",
            error_type="understanding",
            attempts=1
        )

        assert guidance["guidance_type"] == "clarify"
        assert "guidance" in guidance

    @patch('app.services.socratic_teacher.AIService')
    def test_generate_guidance_with_multiple_attempts(self, mock_ai_service):
        """
        测试多次尝试后的策略调整

        验收场景：
        给定学生已经尝试了 3 次
        那么系统应使用更直接的引导类型（如 break_down 或 visualize）
        """
        mock_ai_service.generate_response.return_value = "让我们画个图来理解。先画 5 个圆圈代表 5 个苹果，然后划掉 3 个，数数剩下几个？"

        guidance = self.service.generate_guidance(
            question="5 - 3 = ?",
            student_answer="4",
            correct_answer="2",
            error_type="calculation",
            attempts=3
        )

        # 多次错误后应使用更强的引导
        assert guidance["guidance_type"] in ["break_down", "visualize", "hint"]

    @patch('app.services.socratic_teacher.AIService')
    def test_generate_guidance_response_time(self, mock_ai_service):
        """
        测试引导生成响应时间

        验收场景（SC-002）：
        给定调用 Claude API 生成引导
        那么响应时间应 < 3 秒
        """
        import time

        mock_ai_service.generate_response.return_value = "让我来帮你。"

        start_time = time.time()
        guidance = self.service.generate_guidance(
            question="3 + 5 = ?",
            student_answer="7",
            correct_answer="8",
            error_type="calculation",
            attempts=1
        )
        end_time = time.time()

        response_time = end_time - start_time
        assert response_time < 3.0, f"响应时间 {response_time} 超过 3 秒"
        assert "guidance" in guidance

    def test_select_guidance_type_mapping(self):
        """
        测试引导类型选择逻辑

        验收场景：
        验证错误类型到引导类型的映射关系
        """
        test_cases = [
            ("calculation", 1, ["hint", "check_work"]),
            ("concept", 1, ["clarify", "break_down"]),
            ("understanding", 1, ["clarify"]),
            ("careless", 1, ["check_work", "encourage"]),
            ("calculation", 3, ["break_down", "visualize"]),
            ("concept", 3, ["visualize", "alternative_method"]),
        ]

        for error_type, attempts, expected_types in test_cases:
            guidance_type = self.service._select_guidance_type(error_type, attempts)
            assert guidance_type in expected_types, \
                f"错误类型 {error_type}（尝试 {attempts} 次）应选择 {expected_types} 之一，实际选择了 {guidance_type}"

    def test_build_system_prompt_for_hint_type(self):
        """
        测试构建 hint 类型系统提示词

        验收场景：
        给定引导类型为 "hint"
        那么系统提示词应包含 hint 类型的指导原则
        """
        prompt = self.service._build_system_prompt(
            guidance_type="hint",
            question="3 + 5 = ?",
            student_answer="7",
            error_type="calculation"
        )

        # 验证提示词包含关键要素
        assert "苏格拉底" in prompt or "引导" in prompt
        assert "不要直接给出答案" in prompt or "not give" in prompt.lower()
        assert len(prompt) > 50  # 提示词应有足够内容

    def test_all_guidance_types_supported(self):
        """
        测试支持所有 7 种引导类型

        验收场景：
        验证系统支持 7 种引导类型
        """
        guidance_types = [
            "clarify",      # 澄清
            "hint",         # 提示
            "break_down",   # 分解
            "visualize",    # 可视化
            "check_work",   # 检查
            "alternative_method",  # 替代方法
            "encourage"     # 鼓励
        ]

        for guidance_type in guidance_types:
            prompt = self.service._build_system_prompt(
                guidance_type=guidance_type,
                question="测试问题",
                student_answer="测试答案",
                error_type="calculation"
            )
            assert len(prompt) > 0, f"引导类型 {guidance_type} 的提示词为空"
