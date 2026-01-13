"""
脚手架管理 API (LWP-15)

提供脚手架层级和表现指标的管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.models.database import get_db
from app.models.scaffolding import ScaffoldingLevelRecord, PerformanceMetric
from app.models.socratic import ScaffoldingLevel
from app.services.scaffolding_persistence import ScaffoldingPersistenceService


router = APIRouter(prefix="/api/v1/scaffolding", tags=["scaffolding"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ScaffoldingLevelResponse(BaseModel):
    """脚手架层级响应"""
    student_id: int
    problem_domain: str
    level: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PerformanceMetricResponse(BaseModel):
    """表现指标响应"""
    id: int
    student_id: int
    conversation_id: str
    problem_domain: str
    is_correct: bool
    hints_needed: int
    response_time_seconds: Optional[float]
    self_corrected: bool
    scaffolding_level_at_time: str
    question_type: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class PerformanceStatsResponse(BaseModel):
    """表现统计响应"""
    total_attempts: int
    correct_count: int
    accuracy: float
    avg_hints_needed: float
    avg_response_time: Optional[float]
    current_level: str


class SetScaffoldingLevelRequest(BaseModel):
    """设置脚手架层级请求"""
    level: ScaffoldingLevel = Field(..., description="新的脚手架层级")
    problem_domain: str = Field(default="general", description="问题领域")


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/students/{student_id}/level", response_model=ScaffoldingLevelResponse)
async def get_scaffolding_level(
    student_id: int,
    problem_domain: str = Query("general", description="问题领域（math, reading, general）"),
    db: Session = Depends(get_db)
):
    """
    获取学生当前脚手架层级

    Args:
        student_id: 学生 ID
        problem_domain: 问题领域
        db: 数据库会话

    Returns:
        脚手架层级记录
    """
    try:
        service = ScaffoldingPersistenceService(db)
        record = service.get_current_level(student_id, problem_domain)

        return ScaffoldingLevelResponse(
            student_id=record.student_id,
            problem_domain=record.problem_domain,
            level=record.level.value,
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取脚手架层级失败: {str(e)}")


@router.post("/students/{student_id}/level", response_model=ScaffoldingLevelResponse)
async def set_scaffolding_level(
    student_id: int,
    request: SetScaffoldingLevelRequest,
    db: Session = Depends(get_db)
):
    """
    手动设置学生脚手架层级（家长/教师功能）

    Args:
        student_id: 学生 ID
        request: 设置请求
        db: 数据库会话

    Returns:
        更新后的脚手架层级记录
    """
    try:
        service = ScaffoldingPersistenceService(db)
        record = service.update_level(
            student_id,
            request.problem_domain,
            request.level
        )

        return ScaffoldingLevelResponse(
            student_id=record.student_id,
            problem_domain=record.problem_domain,
            level=record.level.value,
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置脚手架层级失败: {str(e)}")


@router.get("/students/{student_id}/performance", response_model=List[PerformanceMetricResponse])
async def get_performance_metrics(
    student_id: int,
    problem_domain: Optional[str] = Query(None, description="问题领域（可选）"),
    limit: int = Query(20, ge=1, le=100, description="返回的最大记录数"),
    db: Session = Depends(get_db)
):
    """
    获取学生表现历史

    Args:
        student_id: 学生 ID
        problem_domain: 问题领域（可选，不指定则返回所有领域）
        limit: 返回的最大记录数
        db: 数据库会话

    Returns:
        表现指标列表
    """
    try:
        service = ScaffoldingPersistenceService(db)

        if problem_domain:
            metrics = service.get_recent_metrics(student_id, problem_domain, limit)
        else:
            # 查询所有领域的指标
            metrics = db.query(PerformanceMetric).filter(
                PerformanceMetric.student_id == student_id
            ).order_by(
                PerformanceMetric.created_at.desc()
            ).limit(limit).all()

        return [
            PerformanceMetricResponse(
                id=m.id,
                student_id=m.student_id,
                conversation_id=m.conversation_id,
                problem_domain=m.problem_domain,
                is_correct=m.is_correct,
                hints_needed=m.hints_needed,
                response_time_seconds=m.response_time_seconds,
                self_corrected=m.self_corrected,
                scaffolding_level_at_time=m.scaffolding_level_at_time.value,
                question_type=m.question_type,
                created_at=m.created_at.isoformat()
            )
            for m in metrics
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取表现指标失败: {str(e)}")


@router.get("/students/{student_id}/performance/stats", response_model=PerformanceStatsResponse)
async def get_performance_stats(
    student_id: int,
    problem_domain: str = Query("general", description="问题领域"),
    db: Session = Depends(get_db)
):
    """
    获取学生表现统计

    Args:
        student_id: 学生 ID
        problem_domain: 问题领域
        db: 数据库会话

    Returns:
        表现统计数据
    """
    try:
        service = ScaffoldingPersistenceService(db)
        stats = service.get_performance_stats(student_id, problem_domain)

        return PerformanceStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取表现统计失败: {str(e)}")
