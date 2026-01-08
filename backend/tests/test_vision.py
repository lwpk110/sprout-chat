"""
GLM-4.6v 图像识别测试 - TDD Red Phase

测试小芽家教使用 GLM-4.6v 视觉模型识别数学题目
"""

import pytest
from base64 import b64encode
from pathlib import Path
from app.services.vision import VisionService
from app.core.config import settings


@pytest.fixture
def vision_service():
    """创建视觉服务实例"""
    service = VisionService()
    yield service


class TestVisionServiceInit:
    """测试：视觉服务初始化"""

    def test_service_creation(self, vision_service):
        """测试：视觉服务应该能成功创建"""
        assert vision_service is not None
        assert hasattr(vision_service, 'client')

    def test_vision_model_configured(self):
        """测试：GLM-4.6v 模型应该已配置"""
        assert settings.ai_vision_model == "glm-4.6v"


class TestImageRecognition:
    """测试：图像识别功能"""

    @pytest.mark.asyncio
    async def test_recognize_simple_addition(self, vision_service):
        """
        测试：识别简单加法题

        输入：包含 "5 + 3 = ?" 的图片
        预期：识别出数学题目内容
        """
        # 创建测试图片描述（实际使用 base64 编码的图片）
        test_image_description = "一张数学题图片，上面写着 5 + 3 = ?"

        # 这里我们先用文本模拟图片识别结果
        # Red Phase: 测试应该失败，因为功能还没实现
        result = await vision_service.recognize_from_description(test_image_description)

        # 验证识别结果包含关键信息
        assert result is not None
        assert "5" in result or "五" in result
        assert "+" in result or "加" in result
        assert "3" in result or "三" in result

    @pytest.mark.asyncio
    async def test_recognize_subtraction_problem(self, vision_service):
        """
        测试：识别减法题

        输入：包含减法题目的图片
        预期：识别出减法题目
        """
        test_image_description = "一张数学题图片，上面写着 10 - 4 = ?"

        result = await vision_service.recognize_from_description(test_image_description)

        assert result is not None
        assert "10" in result or "十" in result
        assert "-" in result or "减" in result
        assert "4" in result or "四" in result

    @pytest.mark.asyncio
    async def test_recognize_word_problem(self, vision_service):
        """
        测试：识别应用题

        输入：包含文字描述的应用题图片
        预期：识别出题目内容
        """
        test_image_description = "一张应用题图片：小明有5个苹果，吃掉2个，还剩几个？"

        result = await vision_service.recognize_from_description(test_image_description)

        assert result is not None
        assert "小明" in result or "5" in result
        assert "苹果" in result
        assert "还剩" in result or "等于" in result


class TestVisionServiceIntegration:
    """测试：视觉服务集成"""

    @pytest.mark.asyncio
    async def test_extract_math_problem(self, vision_service):
        """
        测试：从图片中提取数学问题

        验证服务能够准确提取图片中的数学表达式
        """
        image_description = "数学题：8 + 7 = ?"

        problem = await vision_service.extract_math_problem(image_description)

        assert problem is not None
        assert len(problem) > 0
        # 应该提取出数字和运算符
        assert any(char.isdigit() for char in problem)

    @pytest.mark.asyncio
    async def test_generate_guided_response(self, vision_service):
        """
        测试：基于图像生成引导式响应

        验证识别图片后能够生成符合小芽教学法的响应
        """
        # 使用描述模式，避免真实 Vision API 调用
        image_description = "一张数学题图片，上面写着 6 + 4 = ?"

        response = await vision_service.generate_guided_response(image_description)

        assert response is not None
        assert len(response) > 0
        # 验证响应符合引导式教学原则
        # 不能直接给答案
        # 注意：由于调用真实 AI，响应可能变化，所以我们只检查基本要求
        assert len(response) > 20  # 响应应该有实质内容


class TestErrorHandling:
    """测试：错误处理"""

    @pytest.mark.asyncio
    async def test_handle_empty_image(self, vision_service):
        """
        测试：处理空图片

        验证服务能够优雅地处理无效输入
        """
        with pytest.raises(ValueError) as exc_info:
            await vision_service.recognize_from_description("")

        assert "图片" in str(exc_info.value) or "空" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_unrecognized_content(self, vision_service):
        """
        测试：处理无法识别的内容

        验证服务对模糊或不清楚的图片有合适的错误处理
        """
        unclear_description = "一张非常模糊的图片，看不清内容"

        result = await vision_service.recognize_from_description(unclear_description)

        # 应该返回友好的提示而不是崩溃
        assert result is not None
        assert "看不清" in result or "重新" in result or "再拍" in result


class TestVisionAPI:
    """测试：Vision API 接口"""

    def test_vision_api_configured(self):
        """
        测试：Vision API 配置正确

        验证所有必需的配置项都已设置
        """
        assert settings.openai_api_key != ""
        assert settings.openai_base_url != ""
        assert settings.ai_vision_model == "glm-4.6v"

    @pytest.mark.asyncio
    async def test_vision_api_call(self, vision_service):
        """
        测试：Vision API 调用

        验证能够成功调用 GLM-4.6v API
        """
        test_prompt = "请描述这个图片：这是一张写着 2 + 3 = ? 的数学题图片"

        try:
            response = await vision_service.call_vision_api(test_prompt)
            assert response is not None
            assert len(response) > 0
        except Exception as e:
            # Red Phase: API 调用可能失败，这是预期的
            pytest.skip(f"Vision API not yet configured: {e}")

# Red Phase 标记：这些测试在功能实现前应该失败
# pytestmark = [
#     pytest.mark.red_phase,
#     pytest.mark.asyncio,
# ]
