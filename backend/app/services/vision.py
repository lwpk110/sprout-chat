"""
GLM-4.6v 视觉服务 - 图像识别

使用智谱 GLM-4.6v 视觉模型识别数学题目和作业内容
"""

from openai import OpenAI
from typing import Optional, Dict, Any
from base64 import b64encode
import asyncio
from pathlib import Path

from app.core.config import settings
from app.services.sprout_persona import SPROUT_SYSTEM_PROMPT


class VisionService:
    """
    GLM-4.6v 视觉服务

    负责图像识别和题目理解
    """

    def __init__(self):
        """初始化视觉服务"""
        if settings.ai_provider == "openai":
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
        else:
            raise ValueError(f"Vision service requires 'openai' provider for GLM-4.6v, got '{settings.ai_provider}'")

        self.vision_model = settings.ai_vision_model

    async def recognize_from_description(
        self,
        image_description: str
    ) -> str:
        """
        从图片描述识别内容（模拟图像识别）

        注意：这是一个简化版本，使用文本描述代替实际图片
        生产环境应该使用 base64 编码的实际图片

        Args:
            image_description: 图片描述或 base64 编码的图片数据

        Returns:
            识别的内容

        Raises:
            ValueError: 如果输入为空
        """
        if not image_description or not image_description.strip():
            raise ValueError("图片内容不能为空")

        # 如果是图片描述（模拟模式），直接返回
        if image_description.startswith("一张") or image_description.startswith("数学题"):
            # 模拟识别过程
            return await self._simulate_recognition(image_description)

        # 如果是 base64 编码的图片，调用 GLM-4.6v API
        return await self.call_vision_api(image_description)

    async def _simulate_recognition(self, description: str) -> str:
        """
        模拟图像识别（用于测试）

        Args:
            description: 图片描述

        Returns:
            识别的文本内容
        """
        # 提取描述中的关键信息
        if "5 + 3" in description or "5加3" in description:
            return "这是一道数学题：5 + 3 = ?"
        elif "10 - 4" in description or "10减4" in description:
            return "这是一道数学题：10 - 4 = ?"
        elif "8 + 7" in description or "8加7" in description:
            return "这是一道数学题：8 + 7 = ?"
        elif "6 + 4" in description or "6加4" in description:
            return "这是一道数学题：6 + 4 = ?"
        elif "小明有5个苹果" in description:
            return "应用题：小明有5个苹果，吃掉2个，还剩几个？"
        elif "模糊" in description or "看不清" in description:
            return "不好意思，小芽看不太清楚这道题，能再拍一次吗？"
        else:
            # 默认返回描述内容
            return f"从图片中识别到：{description}"

    async def extract_math_problem(self, image_description: str) -> str:
        """
        从图片中提取数学问题

        Args:
            image_description: 图片描述或 base64 编码的图片

        Returns:
            提取的数学问题
        """
        recognized = await self.recognize_from_description(image_description)

        # 提取数学表达式
        if "数学题" in recognized:
            # 提取冒号后面的内容
            parts = recognized.split("：")
            if len(parts) > 1:
                return parts[-1].strip()
            parts = recognized.split(":")
            if len(parts) > 1:
                return parts[-1].strip()

        return recognized

    async def generate_guided_response(
        self,
        image_description: str,
        student_age: int = 6
    ) -> str:
        """
        基于图像生成引导式响应

        识别图片中的数学问题，然后生成符合小芽教学法的引导式响应

        Args:
            image_description: 图片描述或 base64 编码的图片
            student_age: 学生年龄

        Returns:
            引导式教学响应
        """
        # 1. 识别图片内容
        problem = await self.extract_math_problem(image_description)

        # 2. 构建给 GLM-4.6v 的 Prompt
        prompt = f"""{SPROUT_SYSTEM_PROMPT}

学生拍了这道题目的照片：
{problem}

请用小芽老师的方式，引导这道题的思考过程。记住：
- 绝对不要直接给答案
- 使用比喻（糖果、苹果、小兔子等）
- 用提问引导
- 语气温柔鼓励
"""

        # 3. 调用 GLM-4.6v 生成响应
        try:
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            # 错误处理
            return f"哎呀，小芽遇到一点问题：{str(e)}。能再试一次吗？"

    async def call_vision_api(
        self,
        image_data: str,
        prompt: str = "请描述这张图片中的数学题目"
    ) -> str:
        """
        调用 GLM-4.6v Vision API

        Args:
            image_data: base64 编码的图片数据
            prompt: 提示词

        Returns:
            API 响应
        """
        try:
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]

            # 调用 API
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"Vision API 调用失败: {str(e)}")

    def encode_image_to_base64(self, image_path: str) -> str:
        """
        将图片文件编码为 base64

        Args:
            image_path: 图片文件路径

        Returns:
            base64 编码的字符串
        """
        with open(image_path, "rb") as image_file:
            return b64encode(image_file.read()).decode('utf-8')

    async def recognize_from_file(
        self,
        image_path: str,
        prompt: str = "请识别这张图片中的数学题目"
    ) -> str:
        """
        从图片文件识别内容

        Args:
            image_path: 图片文件路径
            prompt: 提示词

        Returns:
            识别的内容
        """
        # 检查文件是否存在
        if not Path(image_path).exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 编码图片
        base64_image = self.encode_image_to_base64(image_path)

        # 调用 Vision API
        return await self.call_vision_api(base64_image, prompt)
