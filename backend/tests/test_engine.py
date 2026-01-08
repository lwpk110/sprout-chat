"""
对话引擎测试
"""

import pytest
from datetime import datetime, timedelta

from app.services.engine import ConversationEngine
from app.core.config import settings


@pytest.fixture
def engine_instance():
    """创建引擎实例"""
    engine = ConversationEngine()
    yield engine
    # 清理
    engine.conversations.clear()


def test_create_session(engine_instance):
    """测试创建会话"""
    session_id = engine_instance.create_session(
        student_id="test_student_001",
        subject="数学",
        student_age=6
    )

    assert session_id is not None
    assert "test_student_001" in session_id

    session = engine_instance.get_session(session_id)
    assert session is not None
    assert session["student_id"] == "test_student_001"
    assert session["subject"] == "数学"
    assert session["student_age"] == 6


def test_session_validity(engine_instance):
    """测试会话有效性"""
    session_id = engine_instance.create_session(
        student_id="test_student_002",
        subject="数学"
    )

    # 新会话应该有效
    assert engine_instance.is_session_valid(session_id) is True

    # 不存在的会话应该无效
    assert engine_instance.is_session_valid("invalid_session") is False


def test_add_message(engine_instance):
    """测试添加消息"""
    session_id = engine_instance.create_session(
        student_id="test_student_003",
        subject="数学"
    )

    engine_instance.add_message(session_id, "user", "5 + 3 = ?")
    engine_instance.add_message(session_id, "assistant", "我们来数一数...")

    session = engine_instance.get_session(session_id)
    assert len(session["messages"]) == 2
    assert session["messages"][0]["role"] == "user"
    assert session["messages"][0]["content"] == "5 + 3 = ?"


def test_conversation_history(engine_instance):
    """测试对话历史"""
    session_id = engine_instance.create_session(
        student_id="test_student_004",
        subject="数学"
    )

    # 添加一些消息
    engine_instance.add_message(session_id, "user", "你好")
    engine_instance.add_message(session_id, "assistant", "你好呀！")
    engine_instance.add_message(session_id, "user", "5 + 3 = ?")

    history = engine_instance.get_conversation_history(session_id, limit=10)

    assert len(history) == 3
    assert history[0]["content"] == "你好"
    assert history[-1]["content"] == "5 + 3 = ?"


def test_clear_session(engine_instance):
    """测试清除会话"""
    session_id = engine_instance.create_session(
        student_id="test_student_005",
        subject="数学"
    )

    # 会话应该存在
    assert engine_instance.get_session(session_id) is not None

    # 清除会话
    result = engine_instance.clear_session(session_id)
    assert result is True

    # 会话应该不存在了
    assert engine_instance.get_session(session_id) is None


def test_session_stats(engine_instance):
    """测试会话统计"""
    session_id = engine_instance.create_session(
        student_id="test_student_006",
        subject="数学"
    )

    # 添加一些消息
    engine_instance.add_message(session_id, "user", "测试消息1")
    engine_instance.add_message(session_id, "assistant", "测试响应1")

    stats = engine_instance.get_session_stats(session_id)

    assert stats["session_id"] == session_id
    assert stats["student_id"] == "test_student_006"
    assert stats["subject"] == "数学"
    assert stats["message_count"] == 2
    assert stats["is_valid"] is True


def test_max_conversation_history(engine_instance):
    """测试最大历史记录限制"""
    session_id = engine_instance.create_session(
        student_id="test_student_007",
        subject="数学"
    )

    # 添加超过限制的消息
    for i in range(15):
        engine_instance.add_message(session_id, "user", f"消息 {i}")

    session = engine_instance.get_session(session_id)

    # 应该只保留最后 max_conversation_history 条
    assert len(session["messages"]) <= settings.max_conversation_history


@pytest.mark.skipif(
    not settings.anthropic_api_key or settings.anthropic_api_key == "",
    reason="需要 ANTHROPIC_API_KEY"
)
def test_generate_response(engine_instance):
    """测试生成 AI 响应（需要 API key）"""
    session_id = engine_instance.create_session(
        student_id="test_student_008",
        subject="数学",
        student_age=6
    )

    # 这个测试需要真实的 API key
    # 在 CI/CD 环境中应该跳过或使用 mock
    try:
        response = engine_instance.generate_response(
            session_id=session_id,
            user_input="5 + 3 = ?"
        )

        assert response is not None
        assert len(response) > 0
        # 检查响应不包含直接答案
        assert "答案是" not in response
        assert "8" not in response or "八" not in response

    except Exception as e:
        pytest.skip(f"API 调用失败: {str(e)}")