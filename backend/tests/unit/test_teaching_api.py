"""
引导教学 API 单元测试（Phase 2.2 - US2 - T025）

TDD Phase: Green - 测试引导教学 API 端点功能
"""

import pytest
from fastapi.testclient import TestClient


class TestGenerateGuidanceEndpoint:
    """测试生成引导式反馈端点"""

    def test_generate_guidance_with_calculation_error(self, client: TestClient):
        """
        测试生成计算错误的引导反馈

        验收场景：
        给定学生答错计算题（3+5=7）
        那么系统应生成 hint 类型的引导式反馈
        """
        request_data = {
            "question": "3 + 5 = ?",
            "student_answer": "7",
            "correct_answer": "8",
            "attempts": 1
        }

        response = client.post("/api/v1/teaching/guidance", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["guidance_type"] in ["hint", "check_work"]
        assert len(data["content"]) > 0
        assert "metadata" in data
        assert data["metadata"]["error_type"] == "calculation"

    def test_generate_guidance_with_concept_error(self, client: TestClient):
        """
        测试生成概念错误的引导反馈

        验收场景：
        给定学生混淆减法为加法（5-3=8）
        那么系统应生成 clarify 或 break_down 类型的引导式反馈
        """
        request_data = {
            "question": "你有 5 个苹果，吃掉 3 个，还剩几个？",
            "student_answer": "8",
            "correct_answer": "2",
            "attempts": 1
        }

        response = client.post("/api/v1/teaching/guidance", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["guidance_type"] in ["clarify", "break_down"]
        assert data["metadata"]["error_type"] == "concept"

    def test_generate_guidance_auto_classify_error_type(self, client: TestClient):
        """
        测试自动分类错误类型

        验收场景：
        给定未提供 error_type 参数
        那么系统应自动判断错误类型
        """
        request_data = {
            "question": "小明有 5 个苹果，小红有 3 个苹果，他们一共有多少个？",
            "student_answer": "2",
            "correct_answer": "8",
            "attempts": 1
        }

        response = client.post("/api/v1/teaching/guidance", json=request_data)

        assert response.status_code == 200
        data = response.json()
        # "一共"问题用减法应分类为 understanding 错误
        assert data["metadata"]["error_type"] == "understanding"
        assert data["guidance_type"] == "clarify"

    def test_generate_guidance_with_multiple_attempts(self, client: TestClient):
        """
        测试多次尝试后的策略调整

        验收场景：
        给定学生已经尝试了 3 次
        那么系统应使用更直接的引导类型
        """
        request_data = {
            "question": "15 - 7 = ?",
            "student_answer": "9",
            "correct_answer": "8",
            "error_type": "calculation",
            "attempts": 3
        }

        response = client.post("/api/v1/teaching/guidance", json=request_data)

        assert response.status_code == 200
        data = response.json()
        # 多次尝试后应使用 break_down 或 visualize
        assert data["guidance_type"] in ["break_down", "visualize"]
        assert data["metadata"]["attempts"] == 3

    def test_generate_guidance_invalid_input(self, client: TestClient):
        """
        测试无效输入验证

        验收场景：
        给定缺少必填字段
        那么系统应返回 422 错误
        """
        request_data = {
            "question": "3 + 5 = ?",
            # 缺少 student_answer, correct_answer
        }

        response = client.post("/api/v1/teaching/guidance", json=request_data)

        assert response.status_code == 422


class TestValidateGuidanceEndpoint:
    """测试验证引导式反馈端点"""

    def test_validate_guidance_contains_answer(self, client: TestClient):
        """
        测试检测包含直接答案的响应

        验收场景（SC-003）：
        给定引导式响应包含 "答案是 8"
        那么验证应失败，返回 valid=False
        """
        request_data = {
            "response": "让我来帮你。答案是 8，你应该记住这个。",
            "question": "3 + 5 = ?",
            "correct_answer": "8"
        }

        response = client.post("/api/v1/teaching/guidance/validate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "contains_answer" in data["reason"] or "keyword" in data["reason"]
        assert data["layer"] >= 1

    def test_validate_guidance_no_answer(self, client: TestClient):
        """
        测试不包含答案的响应

        验收场景：
        给定引导式响应不包含直接答案
        那么验证应通过，返回 valid=True
        """
        request_data = {
            "response": "让我来帮你检查一下。你一开始有 3 个苹果，妈妈又给了你 5 个，你能用手指或画图的方式数一数吗？",
            "question": "3 + 5 = ?",
            "correct_answer": "8"
        }

        response = client.post("/api/v1/teaching/guidance/validate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["layer"] == 3

    def test_validate_guidance_invalid_input(self, client: TestClient):
        """
        测试无效输入验证

        验收场景：
        给定缺少必填字段
        那么系统应返回 422 错误
        """
        request_data = {
            "response": "测试响应",
            # 缺少 question, correct_answer
        }

        response = client.post("/api/v1/teaching/guidance/validate", json=request_data)

        assert response.status_code == 422


class TestGetGuidanceTypesEndpoint:
    """测试获取引导类型列表端点"""

    def test_get_guidance_types(self, client: TestClient):
        """
        测试获取所有引导类型

        验收场景：
        当请求获取引导类型列表
        那么系统应返回所有 7 种引导类型及其说明
        """
        response = client.get("/api/v1/teaching/guidance/types")

        assert response.status_code == 200
        data = response.json()
        assert "guidance_types" in data

        guidance_types = data["guidance_types"]
        assert len(guidance_types) == 7

        # 验证包含所有 7 种类型
        type_codes = [gt["type"] for gt in guidance_types]
        expected_types = [
            "clarify",
            "hint",
            "break_down",
            "visualize",
            "check_work",
            "alternative_method",
            "encourage"
        ]
        for expected in expected_types:
            assert expected in type_codes

        # 验证每种类型有完整的字段
        for guidance_type in guidance_types:
            assert "type" in guidance_type
            assert "name" in guidance_type
            assert "description" in guidance_type
            # API 返回中文别名
            assert "适用场景" in guidance_type
            assert isinstance(guidance_type["适用场景"], list)


class TestHealthCheckEndpoint:
    """测试健康检查端点"""

    def test_health_check(self, client: TestClient):
        """
        测试健康检查

        验收场景：
        当请求健康检查
        那么系统应返回服务状态
        """
        response = client.get("/api/v1/teaching/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "features" in data
        assert "guidance_generation" in data["features"]
        assert "response_validation" in data["features"]
        assert "error_classification" in data["features"]
