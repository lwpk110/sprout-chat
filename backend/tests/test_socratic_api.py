"""
苏格拉底响应 API 集成测试 (LWP-13)

测试 API 端点的功能
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app
from app.models.socratic import ScaffoldingLevel, SocraticResponse, ValidationResult


client = TestClient(app)


class TestSocraticAPI:
    """测试苏格拉底响应 API"""

    @pytest.fixture
    def mock_claude_response(self):
        """模拟 Claude API 响应"""
        mock_response = Mock()
        mock_response.content = [Mock(text="🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？")]
        return mock_response

    def test_generate_socratic_response_success(self, mock_claude_response):
        """测试：成功生成引导式响应"""
        with patch('app.services.socratic_response.settings') as mock_settings:
            mock_settings.ai_provider = "anthropic"
            mock_settings.ai_model = "claude-3-5-sonnet"
            mock_settings.ai_max_tokens = 1000
            mock_settings.ai_temperature = 0.7

            with patch('app.api.socratic.socratic_service') as mock_service:
                # 设置模拟响应 - 使用真实的 SocraticResponse 对象
                mock_response = SocraticResponse(
                    response="🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
                    is_socratic=True,
                    validation_score=0.95,
                    scaffolding_level=ScaffoldingLevel.MODERATE,
                    validation_result=ValidationResult(
                        is_valid=True,
                        contains_question=True,
                        contains_direct_answer=False,
                        tone_appropriate=True,
                        length_appropriate=True,
                        score=0.95,
                        reasons=["包含引导性问题", "语气温柔鼓励"]
                    ),
                    metadata={"model": "claude-3-5-sonnet"}
                )
                mock_service.generate_response = AsyncMock(return_value=mock_response)

                # 发送请求
                response = client.post(
                    "/api/v1/socratic/generate",
                    json={
                        "student_message": "1 + 1 = ?",
                        "problem_context": "数学加法题",
                        "scaffolding_level": "moderate"
                    }
                )

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert data["is_socratic"] is True
                assert data["validation_score"] >= 0.8
                assert "response" in data

    def test_generate_socratic_response_empty_message(self):
        """测试：空学生消息返回 400 错误"""
        with patch('app.api.socratic.socratic_service') as mock_service:
            # 模拟服务抛出 ValueError
            mock_service.generate_response = AsyncMock(
                side_effect=ValueError("学生消息不能为空")
            )

            # 发送请求
            response = client.post(
                "/api/v1/socratic/generate",
                json={
                    "student_message": "",
                    "problem_context": "数学题"
                }
            )

            # 验证响应
            assert response.status_code == 400
            data = response.json()
            assert data["detail"]["error"] == "ValidationError"
            assert "学生消息不能为空" in data["detail"]["message"]

    def test_generate_socratic_response_server_error(self):
        """测试：服务器错误返回 500"""
        with patch('app.api.socratic.socratic_service') as mock_service:
            # 模拟服务抛出异常
            mock_service.generate_response = AsyncMock(
                side_effect=Exception("Internal server error")
            )

            # 发送请求
            response = client.post(
                "/api/v1/socratic/generate",
                json={
                    "student_message": "1 + 1 = ?"
                }
            )

            # 验证响应
            assert response.status_code == 500
            data = response.json()
            assert data["detail"]["error"] == "InternalError"

    def test_health_check(self):
        """测试：健康检查端点"""
        response = client.get("/api/v1/socratic/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "socratic-response"

    def test_get_scaffolding_levels(self):
        """测试：获取脚手架层级列表"""
        response = client.get("/api/v1/socratic/scaffolding-levels")
        assert response.status_code == 200
        data = response.json()
        assert "scaffolding_levels" in data
        assert len(data["scaffolding_levels"]) == 3

        # 验证每个层级都有必需的字段
        for level in data["scaffolding_levels"]:
            assert "value" in level
            assert "label" in level
            assert "description" in level
            assert "example" in level

        # 验证层级值
        level_values = [level["value"] for level in data["scaffolding_levels"]]
        assert "highly_guided" in level_values
        assert "moderate" in level_values
        assert "minimal" in level_values

    def test_request_with_conversation_history(self):
        """测试：带对话历史的请求"""
        with patch('app.api.socratic.socratic_service') as mock_service:
            # 使用真实的 SocraticResponse 对象
            mock_response = SocraticResponse(
                response="🌱 让我们再想想。你刚才说应该减法，为什么？",
                is_socratic=True,
                validation_score=0.9,
                scaffolding_level=ScaffoldingLevel.MODERATE,
                metadata={}
            )
            mock_service.generate_response = AsyncMock(return_value=mock_response)

            conversation_history = [
                {"role": "user", "content": "3 - 1 = ?"},
                {"role": "assistant", "content": "你觉得如果有 3 个苹果..."},
                {"role": "user", "content": "应该用减法"}
            ]

            # 发送请求
            response = client.post(
                "/api/v1/socratic/generate",
                json={
                    "student_message": "应该用减法",
                    "problem_context": "数学减法题",
                    "conversation_history": conversation_history,
                    "conversation_id": "conv-123"
                }
            )

            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["is_socratic"] is True

            # 验证服务被正确调用
            mock_service.generate_response.assert_called_once()
            call_args = mock_service.generate_response.call_args
            assert call_args[1]["conversation_history"] == conversation_history
            assert call_args[1]["conversation_id"] == "conv-123"
