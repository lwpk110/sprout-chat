"""
知识点图谱 API 端点（Phase 2.2 - US4）

提供知识点图谱的建立、掌握度追踪和学习路径推荐 API 接口
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.services.knowledge_tracker import KnowledgeTrackerService
from app.models.database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/v1/knowledge-points", tags=["知识点图谱"])

# 服务实例
tracker_service = KnowledgeTrackerService()


# =============================================================================
# 请求/响应模型
# =============================================================================

class UpdateMasteryRequest(BaseModel):
    """更新掌握度请求"""
    mastery_percentage: float = Field(..., ge=0, le=100, description="掌握度百分比（0-100）")


class KnowledgePointListItem(BaseModel):
    """知识点列表项"""
    id: int
    name: str
    subject: str
    difficulty_level: int
    description: Optional[str] = None
    parent_id: Optional[int] = None


class KnowledgePointsListResponse(BaseModel):
    """知识点列表响应"""
    total: int
    knowledge_points: List[KnowledgePointListItem]


class GraphNode(BaseModel):
    """图谱节点"""
    id: int
    name: str
    subject: str
    difficulty_level: int


class GraphEdge(BaseModel):
    """图谱边"""
    from_: int = Field(..., alias="from")
    to: int
    type: str


class KnowledgeGraphResponse(BaseModel):
    """知识点图谱响应"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]

    model_config = {"populate_by_name": True}


class MasteryRecord(BaseModel):
    """掌握记录"""
    id: int
    knowledge_point_id: int
    knowledge_point_name: str
    mastery_percentage: float
    status: str
    last_updated: Optional[str] = None


class StudentMasteryResponse(BaseModel):
    """学生掌握情况响应"""
    student_id: int
    total_points: int
    mastered_count: int
    in_progress_count: int
    not_started_count: int
    mastery_records: List[MasteryRecord]


class UpdateMasteryResponse(BaseModel):
    """更新掌握度响应"""
    id: int
    student_id: int
    knowledge_point_id: int
    mastery_percentage: float
    status: str


class LearningPathItem(BaseModel):
    """学习路径项"""
    order: int
    knowledge_point: Dict[str, Any]
    prerequisites_met: bool
    reason: str


class LearningPathResponse(BaseModel):
    """学习路径响应"""
    student_id: int
    recommended_path: List[LearningPathItem]


# =============================================================================
# API 端点
# =============================================================================

@router.get("/graph", response_model=KnowledgeGraphResponse, status_code=200)
async def get_knowledge_graph(
    subject: Optional[str] = None,
    db: Session = Depends(get_db)
) -> KnowledgeGraphResponse:
    """
    获取知识点图谱（T043）

    返回 DAG 结构的知识点图谱。
    """
    try:
        result = tracker_service.get_knowledge_graph(
            db=db,
            subject=subject
        )

        return KnowledgeGraphResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取知识点图谱失败: {str(e)}"
        )


@router.get("", response_model=KnowledgePointsListResponse, status_code=200)
async def get_knowledge_points(
    subject: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    db: Session = Depends(get_db)
) -> KnowledgePointsListResponse:
    """
    获取知识点列表（T043）

    返回知识点列表，支持按科目和难度筛选。
    """
    try:
        result = tracker_service.get_knowledge_points(
            db=db,
            subject=subject,
            difficulty_level=difficulty_level
        )

        return KnowledgePointsListResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取知识点列表失败: {str(e)}"
        )


@router.get("/{knowledge_point_id}", response_model=Dict[str, Any], status_code=200)
async def get_knowledge_point_detail(
    knowledge_point_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取知识点详情（T043）

    返回指定知识点的详细信息。
    """
    try:
        result = tracker_service.get_knowledge_point_detail(
            db=db,
            knowledge_point_id=knowledge_point_id
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"知识点 {knowledge_point_id} 不存在"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取知识点详情失败: {str(e)}"
        )


# 创建掌握度相关的路由
mastery_router = APIRouter(prefix="/api/v1/knowledge-mastery", tags=["知识点掌握度"])


@mastery_router.get("", response_model=StudentMasteryResponse, status_code=200)
async def get_student_mastery(
    student_id: int,
    subject: Optional[str] = None,
    db: Session = Depends(get_db)
) -> StudentMasteryResponse:
    """
    获取学生知识点掌握情况（T043）

    返回学生对各知识点的掌握情况。
    """
    try:
        result = tracker_service.get_student_mastery(
            db=db,
            student_id=student_id,
            subject=subject
        )

        return StudentMasteryResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取掌握情况失败: {str(e)}"
        )


@mastery_router.get("/recommendations", response_model=LearningPathResponse, status_code=200)
async def get_learning_path_recommendations(
    student_id: int,
    subject: Optional[str] = None,
    db: Session = Depends(get_db)
) -> LearningPathResponse:
    """
    获取学习路径推荐（T043）

    基于前置知识点掌握情况生成学习路径推荐。
    """
    try:
        result = tracker_service.generate_learning_path(
            db=db,
            student_id=student_id,
            subject=subject
        )

        return LearningPathResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成学习路径失败: {str(e)}"
        )


@mastery_router.patch("/{mastery_id}", response_model=UpdateMasteryResponse, status_code=200)
async def update_mastery(
    mastery_id: int,
    request: UpdateMasteryRequest,
    db: Session = Depends(get_db)
) -> UpdateMasteryResponse:
    """
    更新知识点掌握度（T043）

    更新指定知识点的掌握度。
    """
    try:
        # 获取掌握记录
        from app.models.database import KnowledgePointMastery
        mastery = db.query(KnowledgePointMastery).filter(
            KnowledgePointMastery.id == mastery_id
        ).first()

        if not mastery:
            raise HTTPException(
                status_code=404,
                detail=f"掌握记录 {mastery_id} 不存在"
            )

        result = tracker_service.update_mastery(
            db=db,
            student_id=mastery.student_id,
            knowledge_point_id=mastery.knowledge_point_id,
            mastery_percentage=request.mastery_percentage
        )

        return UpdateMasteryResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新掌握度失败: {str(e)}"
        )


@mastery_router.get("/health")
async def health_check():
    """
    健康检查

    验证知识点追踪服务是否正常运行
    """
    return {
        "status": "healthy",
        "service": "知识点追踪服务",
        "features": {
            "knowledge_points_query": "available",
            "mastery_tracking": "available",
            "learning_path_generation": "available"
        }
    }
