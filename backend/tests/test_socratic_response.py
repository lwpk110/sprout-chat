"""
苏格拉底响应生成服务测试 (LWP-13)

测试范围：
1. 生成正确的引导式响应
2. 检测并拒绝直接答案
3. 不同脚手架层级的响应差异
4. 上下文管理（对话历史）
5. 错误处理（API 失败）
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.socratic_response import (
    SocraticResponseService,
    SocraticRequest,
    SocraticResponse,
    ValidationResult,
    SOCRATIC_SYSTEM_PROMPT
)
from app.core.config import settings


class TestSocraticResponseModels:
    """测试数据模型"""

    def test_socratic_request_model(self):
        """测试请求模型"""
        request = SocraticRequest(
            student_message="1 + 1 = ?",
            problem_context="数学加法题",
            scaffolding_level="moderate",
            conversation_id="test-conv-123"
        )
        assert request.student_message == "1 + 1 = ?"
        assert request.scaffolding_level == "moderate"

    def test_socratic_response_model(self):
        """测试响应模型"""
        response = SocraticResponse(
            response="🌱 你觉得如果有 1 个苹果...",
            is_socratic=True,
            validation_score=0.95,
            scaffolding_level="moderate"
        )
        assert response.is_socratic is True
        assert response.validation_score == 0.95

    def test_validation_result_model(self):
        """测试验证结果模型"""
        result = ValidationResult(
            is_valid=True,
            contains_question=True,
            contains_direct_answer=False,
            tone_appropriate=True,
            length_appropriate=True,
            score=0.95,
            reasons=["包含引导性问题", "语气温柔", "长度适中"]
        )
        assert result.is_valid is True
        assert result.contains_question is True
        assert result.contains_direct_answer is False


class TestSocraticResponseService:
    """测试苏格拉底响应生成服务"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return SocraticResponseService()

    @pytest.fixture
    def mock_claude_response(self):
        """模拟 Claude API 响应 - 正确的引导式响应"""
        return Mock(
            content="🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？"
        )

    @pytest.fixture
    def mock_claude_direct_answer(self):
        """模拟 Claude API 响应 - 直接答案（应该被拒绝）"""
        return Mock(
            content="答案是 2"
        )

    @pytest.mark.asyncio
    async def test_generate_socratic_response_success(self, service, mock_claude_response):
        """测试：成功生成引导式响应"""
        with patch('app.services.socratic_response.get_ai_client') as mock_client:
            # 设置模拟响应
            mock_ai = AsyncMock()
            mock_ai.messages.create = AsyncMock(return_value=mock_claude_response)
            mock_client.return_value = mock_ai

            # 调用服务
            request = SocraticRequest(
                student_message="1 + 1 = ?",
                problem_context="数学加法题",
                scaffolding_level="moderate"
            )

            response = await service.generate_response(
                student_message=request.student_message,
                problem_context=request.problem_context,
                scaffolding_level=request.scaffolding_level
            )

            # 验证响应
            assert response.is_socratic is True
            assert response.validation_score >= 0.8
            assert "你觉得" in response.response or "？" in response.response
            assert "答案" not in response.response

    @pytest.mark.asyncio
    async def test_reject_direct_answer(self, service, mock_claude_direct_answer):
        """测试：拒绝直接答案"""
        with patch('app.services.socratic_response.get_ai_client') as mock_client:
            # 设置模拟响应（直接答案）
            mock_ai = AsyncMock()
            mock_ai.messages.create = AsyncMock(return_value=mock_claude_direct_answer)
            mock_client.return_value = mock_ai

            # 调用服务
            request = SocraticRequest(
                student_message="1 + 1 = ?",
                problem_context="数学加法题",
                scaffolding_level="moderate"
            )

            response = await service.generate_response(
                student_message=request.student_message,
                problem_context=request.problem_context,
                scaffolding_level=request.scaffolding_level
            )

            # 验证：应该被拒绝或重新生成
            # 如果验证逻辑工作正常，is_socratic 应该为 False
            # 或者服务应该使用 fallback 响应
            assert response.is_socratic is False or "答案是" not in response.response

    @pytest.mark.asyncio
    async def test_scaffolding_levels(self, service):
        """测试：不同脚手架层级的响应差异"""
        with patch('app.services.socratic_response.get_ai_client') as mock_client:
            mock_ai = AsyncMock()

            # 测试高度引导
            mock_ai.messages.create = AsyncMock(
                return_value=Mock(content="让我们先看看题目里有几个数字。你找到了吗？")
            )
            mock_client.return_value = mock_ai

            response_highly_guided = await service.generate_response(
                student_message="我不知道怎么做",
                problem_context="2 + 3 = ?",
                scaffolding_level="highly_guided"
            )

            # 测试中度引导
            mock_ai.messages.create = AsyncMock(
                return_value=Mock(content="你觉得这道题应该先算哪一步？为什么？")
            )

            response_moderate = await service.generate_response(
                student_message="2 + 3 = ?",
                problem_context="数学加法题",
                scaffolding_level="moderate"
            )

            # 测试最小引导
            mock_ai.messages.create = AsyncMock(
                return_value=Mock(content="你的方法很有创意！还有其他方法吗？")
            )

            response_minimal = await service.generate_response(
                student_message="我做出来了！",
                problem_context="2 + 3 = 5",
                scaffolding_level="minimal"
            )

            # 验证：不同层级应该有不同的 scaffolding_level
            assert response_highly_guided.scaffolding_level == "highly_guided"
            assert response_moderate.scaffolding_level == "moderate"
            assert response_minimal.scaffolding_level == "minimal"

    @pytest.mark.asyncio
    async def test_conversation_history_context(self, service):
        """测试：对话历史上下文管理"""
        with patch('app.services.socratic_response.get_ai_client') as mock_client:
            mock_ai = AsyncMock()
            mock_ai.messages.create = AsyncMock(
                return_value=Mock(content="🌱 让我们再想想。你刚才说应该减法，为什么？")
            )
            mock_client.return_value = mock_ai

            conversation_history = [
                {"role": "user", "content": "3 - 1 = ?"},
                {"role": "assistant", "content": "你觉得如果有 3 个苹果..."},
                {"role": "user", "content": "应该用减法"}
            ]

            response = await service.generate_response(
                student_message="应该用减法",
                problem_context="数学减法题",
                conversation_history=conversation_history
            )

            # 验证：服务应该使用对话历史
            assert response.is_socratic is True
            # 验证 AI 调用包含了历史记录
            call_args = mock_ai.messages.create.call_args
            messages = call_args[1]['messages']
            assert len(messages) > 2  # 应该包含历史记录

    @pytest.mark.asyncio
    async def test_api_error_handling(self, service):
        """测试：API 错误处理"""
        with patch('app.services.socratic_response.get_ai_client') as mock_client:
            mock_ai = AsyncMock()
            # 模拟 API 失败
            mock_ai.messages.create = AsyncMock(side_effect=Exception("API Error"))
            mock_client.return_value = mock_ai

            # 调用服务
            with pytest.raises(Exception) as exc_info:
                await service.generate_response(
                    student_message="1 + 1 = ?",
                    problem_context="数学加法题"
                )

            assert "API Error" in str(exc_info.value)


class TestValidationLogic:
    """测试响应验证逻辑"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return SocraticResponseService()

    def test_validate_good_socratic_response(self, service):
        """测试：验证好的引导式响应"""
        good_response = "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？"

        result = service.validate_response(good_response, correct_answer="2")

        assert result.is_valid is True
        assert result.contains_question is True
        assert result.contains_direct_answer is False
        assert result.tone_appropriate is True
        assert result.score >= 0.8

    def test_validate_direct_answer(self, service):
        """测试：检测直接答案"""
        direct_answer = "答案是 2"

        result = service.validate_response(direct_answer, correct_answer="2")

        assert result.is_valid is False
        assert result.contains_direct_answer is True
        assert result.score < 0.5

    def test_validate_response_without_question(self, service):
        """测试：检测没有问题的响应"""
        no_question = "很好，继续加油！"

        result = service.validate_response(no_question, correct_answer="2")

        assert result.is_valid is False
        assert result.contains_question is False
        assert any("引导性问题" in reason for reason in result.reasons)

    def test_validate_too_long_response(self, service):
        """测试：检测过长的响应"""
        long_response = "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？" * 10

        result = service.validate_response(long_response, correct_answer="2")

        assert result.length_appropriate is False
        assert any("长度" in reason for reason in result.reasons)

    def test_validate_inappropriate_tone(self, service):
        """测试：检测不当语气"""
        inappropriate_tone = "你怎么这么笨！这都不会！"

        result = service.validate_response(inappropriate_tone, correct_answer="2")

        assert result.tone_appropriate is False
        assert result.score < 0.5


class TestSystemPrompt:
    """测试系统提示词"""

    def test_system_prompt_contains_core_principles(self):
        """测试：系统提示包含核心原则"""
        assert "引导思考，不直接给答案" in SOCRATIC_SYSTEM_PROMPT
        assert "温柔耐心" in SOCRATIC_SYSTEM_PROMPT
        assert "循序渐进" in SOCRATIC_SYSTEM_PROMPT

    def test_system_prompt_contains_scaffolding_levels(self):
        """测试：系统提示包含脚手架层级说明"""
        assert "highly_guided" in SOCRATIC_SYSTEM_PROMPT
        assert "moderate" in SOCRATIC_SYSTEM_PROMPT
        assert "minimal" in SOCRATIC_SYSTEM_PROMPT

    def test_system_prompt_contains_examples(self):
        """测试：系统提示包含示例对话"""
        assert "学生:" in SOCRATIC_SYSTEM_PROMPT or "示例" in SOCRATIC_SYSTEM_PROMPT
        assert "❌ 错误" in SOCRATIC_SYSTEM_PROMPT
        assert "✅ 正确" in SOCRATIC_SYSTEM_PROMPT


class TestEdgeCases:
    """测试边缘情况"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return SocraticResponseService()

    @pytest.mark.asyncio
    async def test_empty_student_message(self, service):
        """测试：空学生消息"""
        with pytest.raises(ValueError) as exc_info:
            await service.generate_response(
                student_message="",
                problem_context="数学题"
            )
        assert "学生消息不能为空" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_scaffolding_level(self, service):
        """测试：无效的脚手架层级"""
        with patch('app.services.socratic_response.get_ai_client') as mock_client:
            mock_ai = AsyncMock()
            mock_ai.messages.create = AsyncMock(
                return_value=Mock(content="🌱 你觉得...")
            )
            mock_client.return_value = mock_ai

            # 应该回退到默认值 "moderate"
            response = await service.generate_response(
                student_message="1 + 1 = ?",
                problem_context="数学题",
                scaffolding_level="invalid_level"
            )

            assert response.scaffolding_level == "moderate"

    @pytest.mark.asyncio
    async def test_unicode_and_emoji(self, service):
        """测试：Unicode 字符和 Emoji 支持"""
        with patch('app.services.socratic_response.get_ai_client') as mock_client:
            mock_ai = AsyncMock()
            mock_ai.messages.create = AsyncMock(
                return_value=Mock(content="🌱✨🎨 你觉得这道题有趣吗？🤔💭")
            )
            mock_client.return_value = mock_ai

            response = await service.generate_response(
                student_message="这道题好难",
                problem_context="数学题"
            )

            assert response.is_socratic is True
            assert "🌱" in response.response or "✨" in response.response
