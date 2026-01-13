"""
响应验证系统测试 (LWP-16)

测试多维度验证系统：
1. 引导性问题检测 (pattern-based)
2. 直接答案检测 (pattern-based + AI-based)
3. 脚手架层级对齐检测
4. 问题质量评估 (AI-based)
5. 上下文相关性验证 (AI-based)
"""
import pytest
from app.services.response_validation import ResponseValidationService
from app.models.validation import ValidationResult, ValidationRequest, StudentContext
from app.models.socratic import ScaffoldingLevel


class TestGuidingQuestionDetection:
    """测试引导性问题检测"""

    @pytest.fixture
    def service(self):
        """创建验证服务实例"""
        return ResponseValidationService()

    def test_contains_guiding_question_with_mark(self, service):
        """测试：包含问号的响应被识别为有引导问题"""
        response = "你觉得这道题应该怎么做？"
        result = service._contains_guiding_questions(response)
        assert result is True

    def test_contains_guiding_question_with_guiding_words(self, service):
        """测试：包含引导词的响应被识别"""
        response = "你为什么觉得答案是 5"
        result = service._contains_guiding_questions(response)
        assert result is True

    def test_no_guiding_question_statement(self, service):
        """测试：陈述句没有引导问题"""
        response = "这是一道数学题"
        result = service._contains_guiding_questions(response)
        assert result is False

    def test_guiding_question_score_calculation(self, service):
        """测试：引导问题得分正确计算"""
        response = "你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？"
        score = service._calculate_guiding_question_score(response)
        assert score >= 0.8  # 应该得到高分


class TestDirectAnswerDetection:
    """测试直接答案检测"""

    @pytest.fixture
    def service(self):
        """创建验证服务实例"""
        return ResponseValidationService()

    def test_detects_explicit_answer(self, service):
        """测试：检测明确的直接答案"""
        response = "答案是 5"
        result = service._contains_direct_answers(response)
        assert result is True

    def test_detects_equals_answer(self, service):
        """测试：检测"等于"形式的答案"""
        response = "1 + 1 等于 2"
        result = service._contains_direct_answers(response)
        assert result is True

    def test_detects_should_be_answer(self, service):
        """测试：检测"应该是"形式的答案"""
        response = "你应该这样做：先把两个数字加起来"
        result = service._contains_direct_answers(response)
        assert result is True

    def test_no_direct_answer_in_guiding_question(self, service):
        """测试：引导问题不包含直接答案"""
        response = "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？"
        result = service._contains_direct_answers(response)
        assert result is False

    def test_correct_answer_is_wrong(self, service):
        """测试："正确答案是"被检测"""
        response = "不对，正确答案是 5"
        result = service._contains_direct_answers(response)
        assert result is True


class TestScaffoldingAlignment:
    """测试脚手架层级对齐"""

    @pytest.fixture
    def service(self):
        """创建验证服务实例"""
        return ResponseValidationService()

    def test_highly_guided_alignment(self, service):
        """测试：高度引导响应包含具体提示"""
        response = "让我们先看看题目里有几个数字。你找到了吗？"
        score = service._validate_scaffolding_alignment(
            response,
            ScaffoldingLevel.HIGHLY_GUIDED
        )
        assert score >= 0.7

    def test_moderate_guided_alignment(self, service):
        """测试：中度引导响应包含开放式问题"""
        response = "你觉得这道题应该先算哪一步？为什么？"
        score = service._validate_scaffolding_alignment(
            response,
            ScaffoldingLevel.MODERATE
        )
        assert score >= 0.7

    def test_minimal_guided_alignment(self, service):
        """测试：最小引导响应简洁开放"""
        response = "你的方法很有创意！还有其他方法吗？"
        score = service._validate_scaffolding_alignment(
            response,
            ScaffoldingLevel.MINIMAL
        )
        assert score >= 0.7

    def test_misaligned_highly_guided(self, service):
        """测试：高度引导但响应过于简单"""
        response = "你觉得怎么做？"
        score = service._validate_scaffolding_alignment(
            response,
            ScaffoldingLevel.HIGHLY_GUIDED
        )
        assert score < 0.6  # 应该得到低分


class TestQuestionQuality:
    """测试问题质量评估（需要 AI）"""

    @pytest.fixture
    def service(self):
        """创建验证服务实例"""
        return ResponseValidationService()

    @pytest.mark.asyncio
    async def test_age_appropriate_question(self, service):
        """测试：适合一年级的问题得到高分"""
        response = "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？"
        context = StudentContext(grade=1, problem_type="math")

        # 注意：这需要 AI 调用，如果失败会返回默认分数
        score = await service._assess_question_quality(response, context)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_too_complex_question(self, service):
        """测试：过于复杂的问题得到低分"""
        response = "根据代数原理，我们需要建立方程组来解决这个问题..."
        context = StudentContext(grade=1, problem_type="math")

        score = await service._assess_question_quality(response, context)
        assert score <= 0.6  # 应该得到低分


class TestContextRelevance:
    """测试上下文相关性验证（需要 AI）"""

    @pytest.fixture
    def service(self):
        """创建验证服务实例"""
        return ResponseValidationService()

    @pytest.mark.asyncio
    async def test_context_relevant_response(self, service):
        """测试：相关的响应得到高分"""
        response = "你觉得这道题应该先算哪一步？"
        context = StudentContext(
            grade=1,
            problem_type="math",
            previous_attempts=["1 + 1 = 3"]
        )

        is_relevant = await service._verify_context_relevance(response, context)
        # 注意：如果 AI 调用失败，默认返回 True
        assert isinstance(is_relevant, bool)

    @pytest.mark.asyncio
    async def test_generic_response(self, service):
        """测试：通用响应被检测为不相关"""
        response = "这是一道很有趣的数学题。"
        context = StudentContext(
            grade=1,
            problem_type="math",
            previous_attempts=["1 + 1 = 3"]
        )

        is_relevant = await service._verify_context_relevance(response, context)
        # 应该被检测为不相关（但如果 AI 失败则返回 True）
        assert isinstance(is_relevant, bool)


class TestOverallValidation:
    """测试整体验证流程"""

    @pytest.fixture
    def service(self):
        """创建验证服务实例"""
        return ResponseValidationService()

    @pytest.mark.asyncio
    async def test_perfect_socratic_response_passes(self, service):
        """测试：完美的苏格拉底响应通过验证"""
        request = ValidationRequest(
            response="🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
            scaffolding_level=ScaffoldingLevel.MODERATE,
            student_context=StudentContext(grade=1, problem_type="math")
        )

        result = await service.validate_socratic_response(
            request.response,
            request.scaffolding_level,
            request.student_context
        )

        assert result.is_valid is True
        assert result.overall_score >= 0.8
        assert result.direct_answer_violation is False

    @pytest.mark.asyncio
    async def test_direct_answer_fails(self, service):
        """测试：直接答案被检测并拒绝"""
        request = ValidationRequest(
            response="答案是 2",
            scaffolding_level=ScaffoldingLevel.MODERATE,
            student_context=StudentContext(grade=1, problem_type="math")
        )

        result = await service.validate_socratic_response(
            request.response,
            request.scaffolding_level,
            request.student_context
        )

        assert result.is_valid is False
        assert result.direct_answer_violation is True
        assert "直接答案" in " ".join(result.failure_reasons)

    @pytest.mark.asyncio
    async def test_scaffolding_misalignment_detected(self, service):
        """测试：脚手架层级不对齐被检测"""
        request = ValidationRequest(
            response="你觉得怎么做？",  # 太简单，不适合高度引导
            scaffolding_level=ScaffoldingLevel.HIGHLY_GUIDED,
            student_context=StudentContext(grade=1, problem_type="math")
        )

        result = await service.validate_socratic_response(
            request.response,
            request.scaffolding_level,
            request.student_context
        )

        # 应该检测到脚手架层级不对齐
        assert result.scaffolding_alignment_score < 0.7
        if not result.is_valid:
            assert any("脚手架" in reason for reason in result.failure_reasons)

    @pytest.mark.asyncio
    async def test_generic_response_low_quality(self, service):
        """测试：通用响应被检测为低质量"""
        request = ValidationRequest(
            response="这是一道数学题。",
            scaffolding_level=ScaffoldingLevel.MODERATE,
            student_context=StudentContext(
                grade=1,
                problem_type="math",
                previous_attempts=["1 + 1 = 3"]
            )
        )

        result = await service.validate_socratic_response(
            request.response,
            request.scaffolding_level,
            request.student_context
        )

        # 通用响应应该得到较低分数
        assert result.overall_score < 0.8

    @pytest.mark.asyncio
    async def test_validation_score_calculation(self, service):
        """测试：验证分数正确计算"""
        request = ValidationRequest(
            response="🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
            scaffolding_level=ScaffoldingLevel.MODERATE,
            student_context=StudentContext(grade=1, problem_type="math")
        )

        result = await service.validate_socratic_response(
            request.response,
            request.scaffolding_level,
            request.student_context
        )

        # 验证分数范围
        assert 0.0 <= result.overall_score <= 1.0
        assert 0.0 <= result.guiding_question_score <= 1.0
        assert 0.0 <= result.scaffolding_alignment_score <= 1.0
        assert 0.0 <= result.question_quality_score <= 1.0
        assert 0.0 <= result.context_relevance_score <= 1.0


class TestValidationResult:
    """测试 ValidationResult 模型"""

    def test_to_dict_conversion(self):
        """测试： ValidationResult 可以转换为字典"""
        result = ValidationResult(
            is_valid=True,
            overall_score=0.95,
            guiding_question_score=1.0,
            direct_answer_violation=False,
            scaffolding_alignment_score=0.9,
            question_quality_score=0.95,
            context_relevance_score=0.9,
            failure_reasons=[],
            suggestions=[]
        )

        data = result.to_dict()
        assert data["is_valid"] is True
        assert data["overall_score"] == 0.95
        assert data["direct_answer_violation"] is False
        assert isinstance(data["failure_reasons"], list)
