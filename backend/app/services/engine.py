"""
小芽对话引擎 - 核心引擎

实现小芽老师的对话管理、AI 集成、引导式教学逻辑
"""

import anthropic
from openai import OpenAI
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json

from app.core.config import settings
from app.services.sprout_persona import (
    get_sprout_prompt,
    format_conversation_history
)
from app.services.teaching_strategy import TeachingStrategySelector


class ConversationEngine:
    """
    小芽对话引擎

    负责管理对话状态、调用 AI、生成引导式响应
    """

    def __init__(self):
        """初始化对话引擎"""
        self.ai_provider = settings.ai_provider

        # 根据配置选择 AI 提供商
        if self.ai_provider == "openai":
            self.openai_client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
            self.anthropic_client = None
        else:  # anthropic
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key
            )
            self.openai_client = None

        self.conversations: Dict[str, Dict] = {}  # 会话存储
        self.strategy_selector = TeachingStrategySelector()  # 教学策略选择器

    def create_session(
        self,
        student_id: str,
        subject: str = "数学",
        student_age: int = 6
    ) -> str:
        """
        创建新的对话会话

        Args:
            student_id: 学生 ID
            subject: 科目
            student_age: 学生年龄

        Returns:
            会话 ID
        """
        session_id = f"{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 初始化会话
        self.conversations[session_id] = {
            "student_id": student_id,
            "subject": subject,
            "student_age": student_age,
            "messages": [],
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "topic": "基础对话"
        }

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        获取会话信息

        Args:
            session_id: 会话 ID

        Returns:
            会话信息或 None
        """
        return self.conversations.get(session_id)

    def is_session_valid(self, session_id: str) -> bool:
        """
        检查会话是否有效（未超时）

        Args:
            session_id: 会话 ID

        Returns:
            会话是否有效
        """
        session = self.get_session(session_id)
        if not session:
            return False

        timeout = timedelta(minutes=settings.session_timeout_minutes)
        return datetime.now() - session["last_activity"] < timeout

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """
        添加消息到会话

        Args:
            session_id: 会话 ID
            role: 角色 (user/assistant)
            content: 消息内容
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"会话 {session_id} 不存在")

        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # 限制历史记录长度
        if len(session["messages"]) > settings.max_conversation_history:
            session["messages"] = session["messages"][-settings.max_conversation_history:]

        # 更新活动时间
        session["last_activity"] = datetime.now()

    def generate_response(
        self,
        session_id: str,
        user_input: str,
        use_guided: bool = True
    ) -> str:
        """
        生成 AI 响应

        Args:
            session_id: 会话 ID
            user_input: 用户输入
            use_guided: 是否使用引导式教学

        Returns:
            AI 响应文本
        """
        # 验证会话
        if not self.is_session_valid(session_id):
            raise ValueError("会话已过期或不存在")

        session = self.get_session(session_id)

        # 添加用户消息
        self.add_message(session_id, "user", user_input)

        # 构建系统提示
        if use_guided:
            # 使用教学策略选择器生成引导式 Prompt
            system_prompt = self.strategy_selector.generate_guided_prompt(
                problem=user_input,
                student_age=session["student_age"],
                problem_context={
                    "subject": session["subject"],
                    "topic": session["topic"]
                }
            )
        else:
            # 使用标准 Prompt
            system_prompt = get_sprout_prompt(
                subject=session["subject"],
                topic=session["topic"],
                student_age=session["student_age"]
            )

        # 构建消息列表（给 Claude 的）
        messages_for_api = []
        for msg in session["messages"][:-1]:  # 除了刚添加的最后一条
            messages_for_api.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 添加当前用户输入
        messages_for_api.append({
            "role": "user",
            "content": user_input
        })

        try:
            if self.ai_provider == "openai":
                # 使用 OpenAI 兼容 API（智谱 GLM）
                response = self.openai_client.chat.completions.create(
                    model=settings.ai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *messages_for_api
                    ],
                    max_tokens=settings.ai_max_tokens,
                    temperature=settings.ai_temperature
                )
                assistant_message = response.choices[0].message.content
            else:
                # 使用 Anthropic Claude API
                response = self.anthropic_client.messages.create(
                    model=settings.ai_model,
                    max_tokens=settings.ai_max_tokens,
                    temperature=settings.ai_temperature,
                    system=system_prompt,
                    messages=messages_for_api
                )
                assistant_message = response.content[0].text

            # 添加助手响应到会话
            self.add_message(session_id, "assistant", assistant_message)

            return assistant_message

        except Exception as e:
            # 错误处理
            error_msg = f"小芽有点累了，能再说一次吗？（错误: {str(e)}）"
            self.add_message(session_id, "assistant", error_msg)
            return error_msg

    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        获取对话历史

        Args:
            session_id: 会话 ID
            limit: 返回的消息数量限制

        Returns:
            消息列表
        """
        session = self.get_session(session_id)
        if not session:
            return []

        messages = session["messages"][-limit:]
        return [
            {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            }
            for msg in messages
        ]

    def clear_session(self, session_id: str) -> bool:
        """
        清除会话

        Args:
            session_id: 会话 ID

        Returns:
            是否成功
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话

        Returns:
            清理的会话数量
        """
        timeout = timedelta(minutes=settings.session_timeout_minutes)
        now = datetime.now()

        expired_sessions = [
            session_id
            for session_id, session in self.conversations.items()
            if now - session["last_activity"] > timeout
        ]

        for session_id in expired_sessions:
            del self.conversations[session_id]

        return len(expired_sessions)

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话统计信息

        Args:
            session_id: 会话 ID

        Returns:
            统计信息字典
        """
        session = self.get_session(session_id)
        if not session:
            return {}

        duration = datetime.now() - session["created_at"]
        message_count = len(session["messages"])

        return {
            "session_id": session_id,
            "student_id": session["student_id"],
            "subject": session["subject"],
            "message_count": message_count,
            "duration_seconds": int(duration.total_seconds()),
            "created_at": session["created_at"].isoformat(),
            "last_activity": session["last_activity"].isoformat(),
            "is_valid": self.is_session_valid(session_id)
        }

    async def generate_response_async(
        self,
        session_id: str,
        user_input: str,
        use_guided: bool = True
    ) -> str:
        """
        异步生成 AI 响应

        Args:
            session_id: 会话 ID
            user_input: 用户输入
            use_guided: 是否使用引导式教学

        Returns:
            AI 响应文本
        """
        # 对于同步的 generate_response 方法，我们这里简单封装
        # 在实际应用中，可以使用真正的异步 AI SDK
        import asyncio
        return await asyncio.to_thread(
            self.generate_response,
            session_id,
            user_input,
            use_guided
        )

    async def get_conversation_history_async(
        self,
        session_id: str
    ) -> List[Dict]:
        """
        异步获取对话历史

        Args:
            session_id: 会话 ID

        Returns:
            消息列表
        """
        import asyncio
        return await asyncio.to_thread(
            self.get_conversation_history,
            session_id
        )


# 全局单例
engine = ConversationEngine()