"""
响应验证 API 测试 (LWP-16)

测试验证 API 端点
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.validation import ValidationRequest, StudentContext
from app.models.socratic import ScaffoldingLevel


client = TestClient(app)


class TestValidationAPI:
    """测试验证 API 端点"""

    def test_validate_perfect_socratic_response(self):
        """测试：验证完美的苏格拉底响应"""
        request_data = {
            "response": "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
            "scaffolding_level": "moderate",
            "student_context": {
                "grade": 1,
                "problem_type": "math",
                "previous_attempts": ["1 + 1 = 2"]
            }
        }

        response = client.post("/api/v1/validation/validate-response", json=request_data)

        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is True
        assert result["overall_score"] >= 0.8
        assert result["direct_answer_violation"] is False
        assert result["guiding_question_score"] >= 0.8

    def test_validate_direct_answer_fails(self):
        """测试：直接答案验证失败"""
        request_data = {
            "response": "答案是 2",
            "scaffolding_level": "moderate",
            "student_context": {
                "grade": 1,
                "problem_type": "math"
            }
        }

        response = client.post("/api/v1/validation/validate-response", json=request_data)

        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is False
        assert result["direct_answer_violation"] is True
        assert any("直接答案" in reason for reason in result["failure_reasons"])

    def test_validate_generic_response_low_quality(self):
        """测试：通用响应被检测为低质量"""
        request_data = {
            "response": "这是一道数学题。",
            "scaffolding_level": "moderate",
            "student_context": {
                "grade": 1,
                "problem_type": "math",
                "previous_attempts": ["1 + 1 = 3"]
            }
        }

        response = client.post("/api/v1/validation/validate-response", json=request_data)

        assert response.status_code == 200
        result = response.json()
        # 通用响应应该得到较低分数
        assert result["guiding_question_score"] < 0.5

    def test_validate_missing_response_field(self):
        """测试：缺少必填字段返回 422"""
        request_data = {
            "scaffolding_level": "moderate"
            # 缺少 response 字段
        }

        response = client.post("/api/v1/validation/validate-response", json=request_data)

        assert response.status_code == 422  # Validation Error

    def test_validate_invalid_scaffolding_level(self):
        """测试：无效的脚手架层级"""
        request_data = {
            "response": "你觉得怎么做？",
            "scaffolding_level": "invalid_level"
        }

        response = client.post("/api/v1/validation/validate-response", json=request_data)

        # 应该返回 422 或使用默认值
        assert response.status_code in [200, 422]

    def test_health_check(self):
        """测试：健康检查端点"""
        response = client.get("/api/v1/validation/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "validation"

    def test_validate_with_minimal_student_context(self):
        """测试：最小学生上下文"""
        request_data = {
            "response": "你觉得这道题应该怎么做？",
            "scaffolding_level": "moderate"
            # student_context 使用默认值
        }

        response = client.post("/api/v1/validation/validate-response", json=request_data)

        assert response.status_code == 200
        result = response.json()
        assert "overall_score" in result
