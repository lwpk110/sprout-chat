"""
对话 API 路由

处理语音/文字输入、会话管理、对话历史
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

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

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


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