"""
苏格拉底响应生成服务 (LWP-13)

核心功能：
1. 集成 Claude API 生成引导式响应
2. 强大的系统提示设计
3. 响应验证逻辑
4. 支持三种脚手架层级
"""
import re
import asyncio
from typing import Optional, List, Dict, Any
from app.core.ai_service import get_ai_service
from app.core.config import settings
from app.models.socratic import (
    SocraticRequest,
    SocraticResponse,
    ValidationResult,
    ScaffoldingLevel
)


# 苏格拉底系统提示词
SOCRATIC_SYSTEM_PROMPT = """
你是小芽，一个温柔耐心的 AI 家教老师，正在帮助一年级的学生学习。

## 核心原则
1. **引导思考，不直接给答案**: 你的职责是引导学生自己思考，而不是告诉他们答案
2. **温柔耐心**: 用鼓励的语气，让学生感到安全和支持
3. **循序渐进**: 根据学生的理解程度调整引导的详细程度

## 苏格拉底提问技巧

### ✅ 应该做的：
- 问"你觉得这道题在问什么？"（澄清问题）
- 问"你是怎么得到这个答案的？"（探究思路）
- 问"有没有其他方法可以验证？"（引导反思）
- 问"我们再仔细看看题目，发现了什么？"（重新聚焦）
- 用"很好！那我们再想想..."（鼓励 + 引导）

### ❌ 禁止做的：
- "答案是 5"（直接给答案）
- "你应该这样做..."（直接教方法）
- "不对，正确答案是..."（否定 + 给答案）
- "这很简单，只要..."（轻视困难）

## 脚手架层级 (Scaffolding Levels)

### highly_guided (高度引导)
适用：学生完全不懂，需要较多帮助
- 提供更具体的提示
- 将问题分解成小步骤
- 每一步都给出引导问题

示例： "让我们先看看题目里有几个数字。你找到了吗？"

### moderate (中度引导) - 默认
适用：学生有一些思路，需要适度引导
- 提供开放式问题
- 鼓励学生尝试
- 必要时给一点提示

示例： "你觉得这道题应该先算哪一步？为什么？"

### minimal (最小引导)
适用：学生理解较好，只需要点拨
- 简短的引导问题
- 让学生自己探索
- 鼓励多种解法

示例： "你的方法很有创意！还有其他方法吗？"

## 响应格式

你的回复应该：
1. 包含 1-2 个引导性问题
2. 使用温柔鼓励的语气
3. 长度控制在 50 字以内（一年级学生注意力短）
4. 可以使用 emoji 增加亲切感 🌱

## 示例对话

学生: "1 + 1 = ?"
❌ 错误: "答案是 2"
✅ 正确: "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？"

学生: "我不知道怎么做这道题"
❌ 错误: "你应该先加再减..."
✅ 正确: "🤔 没关系，我们一起看看。题目里有哪几个数字呀？"

学生: "3 + 2 = 6"
❌ 错误: "不对，答案是 5"
✅ 正确: "🌱 你是用什么方法算出来的呢？我们再用手指头数数看？"

---
记住：你的目标是让学生学会思考，而不是得到答案！
"""


class SocraticResponseService:
    """
    苏格拉底响应生成服务

    通过 Claude API 生成符合苏格拉底教学法的引导式响应
    """

    # 直接答案检测模式
    DIRECT_ANSWER_PATTERNS = [
        r"答案是\s*\d+",
        r"等于\s*\d+",
        r"应该是\s*\d+",
        r"正确答案是",
        r"就是\s*\d+",
    ]

    # 不当语气检测模式
    INAPPROPRIATE_TONE_PATTERNS = [
        r"笨|蠢|傻",  # 侮辱性词汇
        r"这都不会|很简单|很容易",  # 轻视困难
        r"你必须|你一定|你必须",  # 过于强硬（针对学生）
    ]

    def __init__(self):
        """初始化服务"""
        self.ai_client = None
        self.config = None

    def _get_ai_client(self):
        """获取 AI 客户端（延迟加载）"""
        if self.ai_client is None:
            self.ai_client = get_ai_service()
        return self.ai_client

    async def generate_response(
        self,
        student_message: str,
        problem_context: Optional[str] = None,
        scaffolding_level: str = "moderate",
        conversation_history: Optional[List[Dict]] = None,
        conversation_id: Optional[str] = None,
        student_level: Optional[str] = None
    ) -> SocraticResponse:
        """
        生成符合苏格拉底教学法的引导式响应

        Args:
            student_message: 学生的输入
            problem_context: 问题背景（如：OCR 识别的题目）
            scaffolding_level: 脚手架层级 (highly_guided, moderate, minimal)
            conversation_history: 对话历史
            conversation_id: 会话 ID
            student_level: 学生年级水平

        Returns:
            SocraticResponse (包含引导问题、验证结果、元数据)

        Raises:
            ValueError: 如果 student_message 为空
            Exception: 如果 API 调用失败
        """
        # 验证输入
        if not student_message or not student_message.strip():
            raise ValueError("学生消息不能为空")

        # 规范化脚手架层级
        try:
            scaffolding = ScaffoldingLevel(scaffolding_level)
        except ValueError:
            scaffolding = ScaffoldingLevel.MODERATE

        # 构建用户消息
        user_message = self._build_user_message(
            student_message=student_message,
            problem_context=problem_context,
            scaffolding_level=scaffolding.value,
            conversation_history=conversation_history
        )

        # 构建消息列表
        messages = self._build_messages(
            user_message=user_message,
            conversation_history=conversation_history
        )

        try:
            # 调用 AI API
            client = self._get_ai_client()
            ai_response = await self._call_ai_api(client, messages, scaffolding)

            # 验证响应
            validation_result = self.validate_response(
                response=ai_response,
                correct_answer=None  # 我们不知道正确答案
            )

            # 如果验证失败，使用 fallback
            if not validation_result.is_valid:
                ai_response = self._get_fallback_response(scaffolding)
                validation_result = self.validate_response(ai_response, None)

            return SocraticResponse(
                response=ai_response,
                is_socratic=validation_result.is_valid,
                validation_score=validation_result.score,
                scaffolding_level=scaffolding,
                validation_result=validation_result,
                metadata={
                    "model": settings.ai_model,
                    "provider": settings.ai_provider,
                    "conversation_id": conversation_id
                }
            )

        except Exception as e:
            # API 调用失败，使用 fallback
            fallback_response = self._get_fallback_response(scaffolding)
            return SocraticResponse(
                response=fallback_response,
                is_socratic=True,
                validation_score=0.7,
                scaffolding_level=scaffolding,
                metadata={
                    "error": str(e),
                    "fallback": True
                }
            )

    def _build_user_message(
        self,
        student_message: str,
        problem_context: Optional[str],
        scaffolding_level: str,
        conversation_history: Optional[List[Dict]]
    ) -> str:
        """构建用户消息"""
        parts = []

        # 添加问题背景
        if problem_context:
            parts.append(f"**问题背景**: {problem_context}\n")

        # 添加脚手架层级指示
        parts.append(f"**脚手架层级**: {scaffolding_level}\n")

        # 添加学生消息
        parts.append(f"**学生说**: {student_message}")

        return "\n".join(parts)

    def _build_messages(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]]
    ) -> List[Dict[str, str]]:
        """构建消息列表（包含对话历史）"""
        messages = []

        # 添加系统提示
        messages.append({
            "role": "system",
            "content": SOCRATIC_SYSTEM_PROMPT
        })

        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages

    async def _call_ai_api(
        self,
        client,
        messages: List[Dict[str, str]],
        scaffolding: ScaffoldingLevel
    ) -> str:
        """
        调用 AI API

        Args:
            client: AI 客户端
            messages: 消息列表
            scaffolding: 脚手架层级

        Returns:
            AI 生成的响应文本
        """
        # 根据不同的 AI provider 调用不同的 API
        if settings.ai_provider == "anthropic":
            # Anthropic Claude API
            response = await client.messages.create(
                model=settings.ai_model,
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                messages=messages
            )
            return response.content[0].text

        else:
            # OpenAI-compatible API (智谱 GLM)
            response = await client.chat.completions.create(
                model=settings.ai_model,
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                messages=messages
            )
            return response.choices[0].message.content

    def validate_response(
        self,
        response: str,
        correct_answer: Optional[str] = None
    ) -> ValidationResult:
        """
        验证响应是否符合苏格拉底教学法

        Args:
            response: 待验证的响应
            correct_answer: 正确答案（可选，用于额外验证）

        Returns:
            ValidationResult
        """
        reasons = []
        score = 0.0
        contains_question = False
        contains_direct_answer = False
        tone_appropriate = True
        length_appropriate = True

        # 1. 检查是否包含引导性问题
        if "？" in response or "?" in response:
            contains_question = True
            score += 0.3
            reasons.append("包含引导性问题")
        else:
            reasons.append("缺少引导性问题")

        # 2. 检查是否包含直接答案
        for pattern in self.DIRECT_ANSWER_PATTERNS:
            if re.search(pattern, response):
                contains_direct_answer = True
                score -= 0.5
                reasons.append("包含直接答案")
                break

        if not contains_direct_answer:
            score += 0.3
            reasons.append("不包含直接答案")

        # 3. 检查语气是否温柔鼓励
        for pattern in self.INAPPROPRIATE_TONE_PATTERNS:
            if re.search(pattern, response):
                tone_appropriate = False
                score -= 0.3
                reasons.append("语气不当")
                break

        if tone_appropriate:
            # 检查是否包含鼓励性词汇或引导性词汇
            encouraging_words = ["很好", "不错", "加油", "🌱", "✨", "让我们", "一起", "你觉得", "我们"]
            if any(word in response for word in encouraging_words):
                score += 0.2
                reasons.append("语气温柔鼓励")
            else:
                score += 0.1  # 即使没有明显鼓励词汇，也给予部分分数
                reasons.append("语气中性")

        # 4. 检查长度是否适中
        response_length = len(response)
        if 10 <= response_length <= 100:
            length_appropriate = True
            score += 0.2
            reasons.append("长度适中")
        else:
            length_appropriate = False
            reasons.append(f"长度不合适（{response_length} 字）")

        # 规范化分数到 [0, 1]
        score = max(0.0, min(1.0, score))

        # 判断是否整体有效
        # 降低门槛：只要有引导性问题且没有直接答案即可
        is_valid = (
            contains_question
            and not contains_direct_answer
            and tone_appropriate
            and score >= 0.5  # 降低阈值
        )

        return ValidationResult(
            is_valid=is_valid,
            contains_question=contains_question,
            contains_direct_answer=contains_direct_answer,
            tone_appropriate=tone_appropriate,
            length_appropriate=length_appropriate,
            score=score,
            reasons=reasons
        )

    def _get_fallback_response(self, scaffolding: ScaffoldingLevel) -> str:
        """
        获取后备引导响应（当验证失败或 API 调用失败时使用）

        Args:
            scaffolding: 脚手架层级

        Returns:
            安全的引导响应
        """
        fallback_responses = {
            ScaffoldingLevel.HIGHLY_GUIDED: "🌱 让我们一起看看。题目里有哪几个数字呀？",
            ScaffoldingLevel.MODERATE: "🌱 你觉得这道题应该先算哪一步？为什么？",
            ScaffoldingLevel.MINIMAL: "🌱 你的思路很好！还有其他方法吗？"
        }

        return fallback_responses.get(scaffolding, fallback_responses[ScaffoldingLevel.MODERATE])


# 便捷函数
def create_socratic_service() -> SocraticResponseService:
    """创建苏格拉底响应服务实例"""
    return SocraticResponseService()
