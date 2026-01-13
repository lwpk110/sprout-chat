"""
对话 API 路由

处理语音/文字输入、会话管理、对话历史
集成苏格拉底响应服务 (LWP-14)
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from app.models.schemas import (
    CreateSessionRequest,
    SessionResponse,
    VoiceInputRequest,
    TextInputRequest,
    ConversationResponse,
    HistoryResponse,
    SessionStatsResponse,
    ErrorResponse
)
from app.services.engine import engine
from app.services.socratic_response import SocraticResponseService
from app.services.context_extractor import InteractionContextExtractor
from app.services.scaffolding_manager import ScaffoldingLevelManager

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

# 初始化苏格拉底相关服务
socratic_service = SocraticResponseService()
context_extractor = InteractionContextExtractor(engine)
scaffolding_manager = ScaffoldingLevelManager()


@router.post(
    "/create",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新的对话会话"
)
async def create_session(request: CreateSessionRequest) -> SessionResponse:
    """
    创建新的学生对话会话

    - **student_id**: 学生唯一标识
    - **subject**: 学习科目（数学、语文等）
    - **student_age**: 学生年龄（影响语言复杂度）
    - **topic**: 对话主题
    """
    try:
        session_id = engine.create_session(
            student_id=request.student_id,
            subject=request.subject,
            student_age=request.student_age
        )

        session = engine.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="会话创建失败"
            )

        return SessionResponse(
            session_id=session_id,
            student_id=session["student_id"],
            subject=session["subject"],
            student_age=session["student_age"],
            created_at=session["created_at"],
            is_valid=True
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话时出错: {str(e)}"
        )


@router.post(
    "/voice",
    response_model=ConversationResponse,
    summary="语音输入处理"
)
async def voice_input(request: VoiceInputRequest) -> ConversationResponse:
    """
    处理语音识别后的文本输入

    - **session_id**: 会话 ID
    - **transcript**: 语音识别的文本
    - **confidence**: 识别置信度（可选）
    """
    try:
        # 生成响应
        response = engine.generate_response(
            session_id=request.session_id,
            user_input=request.transcript
        )

        session = engine.get_session(request.session_id)

        return ConversationResponse(
            session_id=request.session_id,
            response=response,
            timestamp=session["last_activity"].isoformat() if session else ""
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理语音输入时出错: {str(e)}"
        )


@router.post(
    "/message",
    response_model=ConversationResponse,
    summary="文字输入处理"
)
async def text_input(request: TextInputRequest) -> ConversationResponse:
    """
    处理文字输入（应急交互方式）

    - **session_id**: 会话 ID
    - **content**: 文字内容
    """
    try:
        # 生成响应
        response = engine.generate_response(
            session_id=request.session_id,
            user_input=request.content
        )

        session = engine.get_session(request.session_id)

        return ConversationResponse(
            session_id=request.session_id,
            response=response,
            timestamp=session["last_activity"].isoformat() if session else ""
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理文字输入时出错: {str(e)}"
        )


@router.get(
    "/{session_id}/history",
    response_model=HistoryResponse,
    summary="获取对话历史"
)
async def get_history(session_id: str, limit: int = 10) -> HistoryResponse:
    """
    获取会话的对话历史记录

    - **session_id**: 会话 ID
    - **limit**: 返回的消息数量限制
    """
    try:
        messages = engine.get_conversation_history(session_id, limit)

        return HistoryResponse(
            session_id=session_id,
            messages=[
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"]
                }
                for msg in messages
            ],
            total_count=len(messages)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史记录时出错: {str(e)}"
        )


@router.get(
    "/{session_id}/stats",
    response_model=SessionStatsResponse,
    summary="获取会话统计"
)
async def get_session_stats(session_id: str) -> SessionStatsResponse:
    """
    获取会话的统计信息

    - **session_id**: 会话 ID
    """
    try:
        stats = engine.get_session_stats(session_id)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        return SessionStatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话统计时出错: {str(e)}"
        )


@router.delete(
    "/{session_id}",
    summary="删除会话"
)
async def delete_session(session_id: str) -> dict:
    """
    删除指定的会话

    - **session_id**: 会话 ID
    """
    try:
        success = engine.clear_session(session_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        return {"message": f"会话 {session_id} 已删除"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除会话时出错: {str(e)}"
        )


# ============================================================
# 苏格拉底响应端点 (LWP-14)
# ============================================================

@router.post(
    "/{conversation_id}/voice-socratic",
    response_model=ConversationResponse,
    summary="语音输入处理（苏格拉底引导式）"
)
async def voice_input_socratic(
    conversation_id: str,
    transcript: str,
    confidence: Optional[float] = None,
    scaffolding_level: Optional[str] = None
) -> ConversationResponse:
    """
    处理语音识别后的文本输入，返回苏格拉底引导式响应

    ## 流程
    1. 提取交互上下文（对话历史、学生信息）
    2. 确定脚手架层级（基于学生表现）
    3. 调用苏格拉底响应服务生成引导式响应
    4. 保存对话记录

    ## 参数
    - **conversation_id**: 会话 ID
    - **transcript**: 语音识别的文本
    - **confidence**: 识别置信度（可选）
    - **scaffolding_level**: 脚手架层级（可选，默认自动调整）
      - `highly_guided`: 高度引导
      - `moderate`: 中度引导
      - `minimal`: 最小引导

    ## 响应示例
    ```json
    {
        "session_id": "student_001_20250113...",
        "response": "🌱 你觉得如果有 1 个苹果，妈妈又给了你 1 个，现在有几个呢？",
        "timestamp": "2025-01-13T10:00:00Z",
        "response_type": "socratic",
        "is_socratic": true,
        "scaffolding_level": "moderate",
        "validation_score": 0.95
    }
    ```
    """
    try:
        # 1. 提取交互上下文
        context = context_extractor.extract_context(
            conversation_id=conversation_id,
            student_input=transcript,
            input_type="voice"
        )

        # 2. 确定脚手架层级
        if scaffolding_level:
            # 用户指定层级
            level = scaffolding_level
        else:
            # 根据表现自动调整
            performance_history = _get_performance_history(conversation_id)
            level_obj = scaffolding_manager.determine_level(
                conversation_id=conversation_id,
                performance_history=performance_history
            )
            level = level_obj.value

        # 3. 生成苏格拉底响应
        socratic_response = await socratic_service.generate_response(
            student_message=transcript,
            problem_context=None,  # 可以后续集成 OCR
            scaffolding_level=level,
            conversation_history=context_extractor.convert_to_ai_history_format(
                context["conversation_history"]
            ),
            conversation_id=conversation_id,
            student_level=f"一年级（{context['student_age']}岁）"
        )

        # 4. 保存对话记录到引擎
        engine.add_message(conversation_id, "user", transcript)
        engine.add_message(conversation_id, "assistant", socratic_response.response)

        session = engine.get_session(conversation_id)

        # 5. 返回响应（扩展格式）
        return ConversationResponse(
            session_id=conversation_id,
            response=socratic_response.response,
            timestamp=session["last_activity"].isoformat() if session else ""
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理语音输入时出错: {str(e)}"
        )


@router.post(
    "/{conversation_id}/message-socratic",
    response_model=ConversationResponse,
    summary="文字输入处理（苏格拉底引导式）"
)
async def text_input_socratic(
    conversation_id: str,
    content: str,
    scaffolding_level: Optional[str] = None
) -> ConversationResponse:
    """
    处理文字输入，返回苏格拉底引导式响应

    ## 流程
    1. 提取交互上下文
    2. 确定脚手架层级
    3. 调用苏格拉底响应服务
    4. 保存对话记录

    ## 参数
    - **conversation_id**: 会话 ID
    - **content**: 文字内容
    - **scaffolding_level**: 脚手架层级（可选）

    ## 响应示例
    ```json
    {
        "session_id": "student_001_20250113...",
        "response": "🌱 你觉得这道题应该先算哪一步？为什么？",
        "timestamp": "2025-01-13T10:00:00Z"
    }
    ```
    """
    try:
        # 1. 提取交互上下文
        context = context_extractor.extract_context(
            conversation_id=conversation_id,
            student_input=content,
            input_type="text"
        )

        # 2. 确定脚手架层级
        if scaffolding_level:
            level = scaffolding_level
        else:
            performance_history = _get_performance_history(conversation_id)
            level_obj = scaffolding_manager.determine_level(
                conversation_id=conversation_id,
                performance_history=performance_history
            )
            level = level_obj.value

        # 3. 生成苏格拉底响应
        socratic_response = await socratic_service.generate_response(
            student_message=content,
            problem_context=None,
            scaffolding_level=level,
            conversation_history=context_extractor.convert_to_ai_history_format(
                context["conversation_history"]
            ),
            conversation_id=conversation_id,
            student_level=f"一年级（{context['student_age']}岁）"
        )

        # 4. 保存对话记录
        engine.add_message(conversation_id, "user", content)
        engine.add_message(conversation_id, "assistant", socratic_response.response)

        session = engine.get_session(conversation_id)

        return ConversationResponse(
            session_id=conversation_id,
            response=socratic_response.response,
            timestamp=session["last_activity"].isoformat() if session else ""
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理文字输入时出错: {str(e)}"
        )


# ============================================================
# 辅助函数
# ============================================================

def _get_performance_history(conversation_id: str) -> Optional[List[dict]]:
    """
    获取学生表现历史（用于确定脚手架层级）

    Args:
        conversation_id: 会话 ID

    Returns:
        表现历史列表或 None
    """
    # 从对话历史中推断表现（简单版本）
    # TODO: 未来可以从数据库查询真实的学习记录
    history = engine.get_conversation_history(conversation_id, limit=10)

    # 简单的启发式规则：
    # - 如果学生连续回答"对"、"是的"、"正确"等，算作正确
    # - 如果学生说"不知道"、"不会"等，算作错误
    performance = []
    for msg in history:
        if msg["role"] == "user":
            content = msg["content"].lower()
            if any(word in content for word in ["对", "是的", "正确", "好的"]):
                performance.append({"is_correct": True})
            elif any(word in content for word in ["不知道", "不会", "不懂"]):
                performance.append({"is_correct": False})

    return performance if performance else None
