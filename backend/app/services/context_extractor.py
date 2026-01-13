"""
交互上下文提取服务 (LWP-14)

负责从对话会话中提取交互上下文，为苏格拉底响应生成提供必要信息
"""
from typing import Dict, List, Optional, Any


class InteractionContextExtractor:
    """
    交互上下文提取器

    从对话引擎的会话中提取结构化上下文信息
    """

    def __init__(self, engine):
        """
        初始化上下文提取器

        Args:
            engine: ConversationEngine 实例
        """
        self.engine = engine

    def extract_context(
        self,
        conversation_id: str,
        student_input: str,
        input_type: str = "text"
    ) -> Dict[str, Any]:
        """
        提取交互上下文

        Args:
            conversation_id: 会话 ID
            student_input: 学生输入内容
            input_type: 输入类型 (text, voice, image)

        Returns:
            上下文字典，包含：
            - student_input: 学生输入
            - input_type: 输入类型
            - conversation_history: 对话历史（最近 5 轮）
            - student_age: 学生年龄
            - subject: 科目
            - conversation_id: 会话 ID

        Raises:
            ValueError: 如果会话不存在
        """
        # 获取会话
        session = self.engine.get_session(conversation_id)
        if not session:
            raise ValueError(f"会话 {conversation_id} 不存在")

        # 获取对话历史（最近 5 轮，即最近 10 条消息）
        history = self.engine.get_conversation_history(conversation_id, limit=10)

        # 构建上下文
        context = {
            "student_input": student_input,
            "input_type": input_type,
            "conversation_history": history,
            "student_age": session.get("student_age", 6),
            "subject": session.get("subject", "数学"),
            "conversation_id": conversation_id,
            "topic": session.get("topic", "基础对话")
        }

        return context

    def convert_to_ai_history_format(
        self,
        conversation_history: List[Dict]
    ) -> List[Dict[str, str]]:
        """
        将对话历史转换为 AI API 格式

        Args:
            conversation_history: 对话历史列表

        Returns:
            AI 格式的消息列表 [{"role": "user", "content": "..."}, ...]
        """
        ai_history = []

        for msg in conversation_history:
            ai_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        return ai_history

    def extract_problem_context(
        self,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        提取问题背景（可选）

        从上下文中提取问题背景信息，例如：
        - OCR 识别的题目
        - 前几轮对话中提到的问题

        Args:
            context: 上下文字典

        Returns:
            问题背景字符串或 None
        """
        # 如果输入类型是 image，可以从历史中找到 OCR 结果
        if context["input_type"] == "image":
            # 查找最近的 OCR 结果
            for msg in reversed(context["conversation_history"]):
                if msg.get("role") == "system" and "OCR" in msg.get("content", ""):
                    return msg["content"]

        return None

    def format_context_for_socratic(
        self,
        context: Dict[str, Any]
    ) -> str:
        """
        格式化上下文为苏格拉底服务可用的字符串

        Args:
            context: 上下文字典

        Returns:
            格式化的上下文描述
        """
        parts = []

        # 添加科目和主题
        parts.append(f"科目: {context['subject']}")
        parts.append(f"主题: {context['topic']}")

        # 添加学生年龄
        parts.append(f"学生年龄: {context['student_age']} 岁")

        # 添加输入类型
        input_type_map = {
            "text": "文字",
            "voice": "语音",
            "image": "图片"
        }
        parts.append(f"输入方式: {input_type_map.get(context['input_type'], context['input_type'])}")

        return "\n".join(parts)
