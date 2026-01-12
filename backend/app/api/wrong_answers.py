"""
错题本 API 端点（Phase 2.2 - US3）

提供错题本的记录、查询、统计和练习推荐 API 接口
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.services.practice_recommender import PracticeRecommenderService
from app.models.database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/v1/wrong-answers", tags=["错题本"])

# 服务实例
practice_service = PracticeRecommenderService()


# =============================================================================
# 请求/响应模型
# =============================================================================

class UpdateWrongAnswerStatusRequest(BaseModel):
    """更新错题状态请求"""
    is_resolved: bool = Field(..., description="是否已解决")


class WrongAnswerDetailResponse(BaseModel):
    """错题详情响应"""
    id: int
    student_id: int
    question_content: str
    student_answer: str
    correct_answer: str
    error_type: str
    guidance_type: Optional[str] = None
    guidance_content: Optional[str] = None
    is_resolved: bool
    attempts_count: int
    last_attempt_at: Optional[str] = None
    created_at: Optional[str] = None


class WrongAnswerListItem(BaseModel):
    """错题列表项"""
    id: int
    student_id: int
    question_content: str
    student_answer: str
    correct_answer: str
    error_type: str
    is_resolved: bool
    attempts_count: int
    created_at: Optional[str] = None


class WrongAnswersListResponse(BaseModel):
    """错题列表响应"""
    total: int
    page: int
    page_size: int
    wrong_answers: List[WrongAnswerListItem]


class StatisticsResponse(BaseModel):
    """错题统计响应"""
    student_id: int
    total_wrong_answers: int
    resolved_count: int
    unresolved_count: int
    by_error_type: Dict[str, int]
    most_common_errors: List[str]


class SimilarQuestion(BaseModel):
    """相似题目"""
    id: int
    question_content: str
    difficulty_level: int
    question_type: str


class RecommendationItem(BaseModel):
    """推荐项"""
    priority: str
    error_type: str
    similar_questions: List[SimilarQuestion]
    reason: str


class RecommendationsResponse(BaseModel):
    """练习推荐响应"""
    student_id: int
    recommendations: List[RecommendationItem]
    total_count: int


class UpdateStatusResponse(BaseModel):
    """更新状态响应"""
    id: int
    is_resolved: bool
    resolved_at: Optional[str] = None


# =============================================================================
# API 端点
# =============================================================================

@router.get("/statistics", response_model=StatisticsResponse, status_code=200)
async def get_statistics(
    student_id: int,
    db: Session = Depends(get_db)
) -> StatisticsResponse:
    """
    获取错题统计（T033）

    返回学生的错题统计数据。
    """
    try:
        result = practice_service.get_statistics(
            db=db,
            student_id=student_id
        )

        return StatisticsResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取错题统计失败: {str(e)}"
        )


@router.get("/recommendations", response_model=RecommendationsResponse, status_code=200)
async def get_recommendations(
    student_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> RecommendationsResponse:
    """
    获取练习推荐（T033）

    基于错题记录生成针对性的练习推荐。
    """
    try:
        result = practice_service.generate_recommendations(
            db=db,
            student_id=student_id,
            limit=limit
        )

        return RecommendationsResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成练习推荐失败: {str(e)}"
        )


@router.get("", response_model=WrongAnswersListResponse, status_code=200)
async def get_wrong_answers(
    student_id: int,
    error_type: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
) -> WrongAnswersListResponse:
    """
    获取错题列表（T033）

    返回学生的错题记录，支持分页和筛选。
    """
    try:
        result = practice_service.get_wrong_answers(
            db=db,
            student_id=student_id,
            error_type=error_type,
            is_resolved=is_resolved,
            page=page,
            page_size=page_size
        )

        return WrongAnswersListResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取错题列表失败: {str(e)}"
        )


@router.get("/{wrong_answer_id}", response_model=Dict[str, Any], status_code=200)
async def get_wrong_answer_detail(
    wrong_answer_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取错题详情（T033）

    返回指定错题记录的详细信息。
    """
    try:
        result = practice_service.get_wrong_answer_detail(
            db=db,
            wrong_answer_id=wrong_answer_id
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"错题记录 {wrong_answer_id} 不存在"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取错题详情失败: {str(e)}"
        )


@router.patch("/{wrong_answer_id}", response_model=UpdateStatusResponse, status_code=200)
async def update_wrong_answer_status(
    wrong_answer_id: int,
    request: UpdateWrongAnswerStatusRequest,
    db: Session = Depends(get_db)
) -> UpdateStatusResponse:
    """
    更新错题状态（T033）

    标记错题为已解决或未解决。
    """
    try:
        result = practice_service.update_wrong_answer_status(
            db=db,
            wrong_answer_id=wrong_answer_id,
            is_resolved=request.is_resolved
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"错题记录 {wrong_answer_id} 不存在"
            )

        return UpdateStatusResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新错题状态失败: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    健康检查

    验证错题本服务是否正常运行
    """
    return {
        "status": "healthy",
        "service": "错题本服务",
        "features": {
            "wrong_answers_query": "available",
            "statistics": "available",
            "practice_recommendations": "available"
        }
    }
