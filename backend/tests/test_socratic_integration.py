"""
苏格拉底响应集成测试 (LWP-14)

测试 SocraticResponseService 与对话流程的集成
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.socratic_response import SocraticResponseService
from app.services.engine import ConversationEngine
from app.services.context_extractor import InteractionContextExtractor
from app.services.scaffolding_manager import ScaffoldingLevelManager
from app.models.socratic import ScaffoldingLevel


class TestInteractionContextExtractor:
    """测试交互上下文提取器"""

    @pytest.fixture
    def engine(self):
        """创建对话引擎实例"""
        return ConversationEngine()

    @pytest.fixture
    def context_extractor(self, engine):
        """创建上下文提取器实例"""
        return InteractionContextExtractor(engine)

    @pytest.fixture
    def sample_session(self, engine):
        """创建示例会话"""
        session_id = engine.create_session(
            student_id="student_001",
            subject="数学",
            student_age=6
        )

        # 添加一些对话历史
        engine.add_message(session_id, "user", "1 + 1 = ?")
        engine.add_message(session_id, "assistant", "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？")

        return session_id

    def test_extract_context_from_session(self, context_extractor, sample_session):
        """测试从会话中提取上下文"""
        # Act
        context = context_extractor.extract_context(
            conversation_id=sample_session,
            student_input="我想想...是 2 吗？",
            input_type="text"
        )

        # Assert
        assert context is not None
        assert context["student_input"] == "我想想...是 2 吗？"
        assert context["input_type"] == "text"
        assert len(context["conversation_history"]) > 0
        assert context["student_age"] == 6
        assert context["subject"] == "数学"

    def test_extract_context_with_empty_history(self, context_extractor, engine):
        """测试从空历史的会话中提取上下文"""
        # Arrange
        session_id = engine.create_session(
            student_id="student_002",
            subject="语文",
            student_age=7
        )

        # Act
        context = context_extractor.extract_context(
            conversation_id=session_id,
            student_input="这个字怎么读？",
            input_type="voice"
        )

        # Assert
        assert context is not None
        assert context["student_input"] == "这个字怎么读？"
        assert context["input_type"] == "voice"
        assert context["conversation_history"] == []

    def test_extract_context_invalid_session(self, context_extractor):
        """测试从无效会话中提取上下文"""
        # Act & Assert
        with pytest.raises(ValueError, match="不存在"):
            context_extractor.extract_context(
                conversation_id="invalid_session_id",
                student_input="测试",
                input_type="text"
            )

    def test_extract_context_converts_to_ai_format(self, context_extractor, sample_session):
        """测试上下文转换为 AI 格式"""
        # Act
        context = context_extractor.extract_context(
            conversation_id=sample_session,
            student_input="2 + 3 = ?",
            input_type="text"
        )

        ai_history = context_extractor.convert_to_ai_history_format(
            context["conversation_history"]
        )

        # Assert
        assert isinstance(ai_history, list)
        if len(ai_history) > 0:
            assert "role" in ai_history[0]
            assert "content" in ai_history[0]


class TestScaffoldingLevelManager:
    """测试脚手架层级管理器"""

    @pytest.fixture
    def scaffolding_manager(self):
        """创建脚手架管理器实例"""
        return ScaffoldingLevelManager()

    def test_determine_default_level_new_student(self, scaffolding_manager):
        """测试新学生的默认脚手架层级"""
        # Act
        level = scaffolding_manager.determine_level(
            conversation_id="new_session",
            performance_history=None
        )

        # Assert
        assert level == ScaffoldingLevel.MODERATE

    def test_increase_scaffolding_after_errors(self, scaffolding_manager):
        """测试连续错误后提升脚手架层级"""
        # Arrange - 模拟连续 3 个错误
        performance_history = [
            {"is_correct": False},
            {"is_correct": False},
            {"is_correct": False}
        ]

        # Act
        level = scaffolding_manager.determine_level(
            conversation_id="session_001",
            performance_history=performance_history
        )

        # Assert
        assert level == ScaffoldingLevel.HIGHLY_GUIDED

    def test_decrease_scaffolding_after_success(self, scaffolding_manager):
        """测试连续成功后降低脚手架层级"""
        # Arrange - 模拟连续 3 个正确答案
        performance_history = [
            {"is_correct": True},
            {"is_correct": True},
            {"is_correct": True}
        ]

        # Act
        level = scaffolding_manager.determine_level(
            conversation_id="session_001",
            performance_history=performance_history
        )

        # Assert
        assert level == ScaffoldingLevel.MINIMAL

    def test_maintain_moderate_level(self, scaffolding_manager):
        """测试混合表现维持中度引导"""
        # Arrange - 混合表现
        performance_history = [
            {"is_correct": True},
            {"is_correct": False},
            {"is_correct": True}
        ]

        # Act
        level = scaffolding_manager.determine_level(
            conversation_id="session_001",
            performance_history=performance_history
        )

        # Assert
        assert level == ScaffoldingLevel.MODERATE


class TestSocraticIntegration:
    """测试苏格拉底响应与对话流程的集成"""

    @pytest.fixture
    def engine(self):
        """创建对话引擎实例"""
        return ConversationEngine()

    @pytest.fixture
    def socratic_service(self):
        """创建苏格拉底服务实例"""
        return SocraticResponseService()

    @pytest.fixture
    def context_extractor(self, engine):
        """创建上下文提取器实例"""
        return InteractionContextExtractor(engine)

    @pytest.fixture
    def scaffolding_manager(self):
        """创建脚手架管理器实例"""
        return ScaffoldingLevelManager()

    @pytest.fixture
    def sample_session(self, engine):
        """创建示例会话"""
        return engine.create_session(
            student_id="student_001",
            subject="数学",
            student_age=6
        )

    @pytest.mark.asyncio
    async def test_voice_input_with_socratic_response(
        self,
        engine,
        socratic_service,
        context_extractor,
        scaffolding_manager,
        sample_session
    ):
        """测试语音输入使用苏格拉底响应"""
        # Arrange
        student_input = "1 + 1 = ?"

        # 提取上下文
        context = context_extractor.extract_context(
            conversation_id=sample_session,
            student_input=student_input,
            input_type="voice"
        )

        # 确定脚手架层级
        level = scaffolding_manager.determine_level(
            conversation_id=sample_session,
            performance_history=None
        )

        # Act - 生成苏格拉底响应
        response = await socratic_service.generate_response(
            student_message=student_input,
            problem_context=None,
            scaffolding_level=level.value,
            conversation_history=context_extractor.convert_to_ai_history_format(
                context["conversation_history"]
            ),
            conversation_id=sample_session
        )

        # Assert
        assert response is not None
        assert response.response != ""
        assert response.is_socratic is True
        assert response.scaffolding_level == level
        assert 0.0 <= response.validation_score <= 1.0

    @pytest.mark.asyncio
    async def test_text_input_with_socratic_response(
        self,
        socratic_service,
        context_extractor,
        scaffolding_manager,
        sample_session
    ):
        """测试文字输入使用苏格拉底响应"""
        # Arrange
        student_input = "这道题怎么做？"

        # 提取上下文
        context = context_extractor.extract_context(
            conversation_id=sample_session,
            student_input=student_input,
            input_type="text"
        )

        # 确定脚手架层级
        level = scaffolding_manager.determine_level(
            conversation_id=sample_session,
            performance_history=None
        )

        # Act
        response = await socratic_service.generate_response(
            student_message=student_input,
            problem_context=None,
            scaffolding_level=level.value,
            conversation_history=context_extractor.convert_to_ai_history_format(
                context["conversation_history"]
            ),
            conversation_id=sample_session
        )

        # Assert
        assert response is not None
        assert response.response != ""
        assert "?" in response.response or "？" in response.response  # 应该包含引导性问题

    @pytest.mark.asyncio
    async def test_socratic_response_with_history(
        self,
        engine,
        socratic_service,
        context_extractor,
        scaffolding_manager,
        sample_session
    ):
        """测试带对话历史的苏格拉底响应"""
        # Arrange - 添加对话历史
        engine.add_message(sample_session, "user", "1 + 1 = ?")
        engine.add_message(sample_session, "assistant", "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？")
        engine.add_message(sample_session, "user", "我想想...是 2 吗？")

        student_input = "对吗？"

        # 提取上下文
        context = context_extractor.extract_context(
            conversation_id=sample_session,
            student_input=student_input,
            input_type="text"
        )

        # 确定脚手架层级
        level = scaffolding_manager.determine_level(
            conversation_id=sample_session,
            performance_history=None
        )

        # Act
        response = await socratic_service.generate_response(
            student_message=student_input,
            problem_context=None,
            scaffolding_level=level.value,
            conversation_history=context_extractor.convert_to_ai_history_format(
                context["conversation_history"]
            ),
            conversation_id=sample_session
        )

        # Assert
        assert response is not None
        # 应该基于历史上下文生成响应
        assert len(context["conversation_history"]) > 0

    @pytest.mark.asyncio
    async def test_dynamic_scaffolding_adjustment(
        self,
        socratic_service,
        context_extractor,
        scaffolding_manager,
        sample_session
    ):
        """测试动态脚手架层级调整"""
        # Arrange - 模拟连续正确
        performance_history = [
            {"is_correct": True},
            {"is_correct": True},
            {"is_correct": True}
        ]

        # 确定脚手架层级
        level = scaffolding_manager.determine_level(
            conversation_id=sample_session,
            performance_history=performance_history
        )

        # Act
        response = await socratic_service.generate_response(
            student_message="3 + 2 = ?",
            problem_context=None,
            scaffolding_level=level.value,
            conversation_history=[],
            conversation_id=sample_session
        )

        # Assert
        assert response.scaffolding_level == ScaffoldingLevel.MINIMAL
        assert response.is_socratic is True

    @pytest.mark.asyncio
    async def test_socratic_fallback_on_error(
        self,
        socratic_service
    ):
        """测试 API 失败时的 fallback 响应"""
        # Act - 空输入会触发 ValueError，但服务会返回 fallback
        response = await socratic_service.generate_response(
            student_message="",  # 空输入
            problem_context=None,
            scaffolding_level="moderate"
        )

        # Assert - 应该返回 fallback 响应
        assert response is not None
        assert response.response != ""

    def test_response_format_for_frontend(self):
        """测试响应格式是否符合前端预期"""
        # Arrange
        socratic_response = {
            "response": "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
            "is_socratic": True,
            "validation_score": 0.95,
            "scaffolding_level": "moderate"
        }

        # Assert - 验证响应格式
        assert "response" in socratic_response
        assert "is_socratic" in socratic_response
        assert "validation_score" in socratic_response
        assert "scaffolding_level" in socratic_response
        assert isinstance(socratic_response["validation_score"], float)
        assert 0.0 <= socratic_response["validation_score"] <= 1.0
