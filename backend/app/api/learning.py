"""
学习追踪 API 端点

提供家长监控功能的 API 接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.services.learning_tracker import LearningTracker
from app.models.learning import (
    ProgressUpdate,
    ReportRequest,
    ProgressSummary,
    LearningRecord,
    StudentProgress,
    LearningReport
)


router = APIRouter(prefix="/api/v1/learning", tags=["学习追踪"])

# 全局学习追踪器实例
tracker = LearningTracker()


@router.post("/record")
async def create_learning_record(update: ProgressUpdate):
    """
    创建学习记录

    记录一次完整的问答交互，用于后续进度追踪和报告生成
    """
    try:
        record = tracker.create_record(
            session_id=update.session_id,
            student_id=update.student_id,
            student_age=6,  # TODO: 从会话中获取
            subject="数学",  # TODO: 从会话中获取
            problem_type=update.problem_type,
            problem_text=update.problem_text,
            student_answer=update.student_answer,
            answer_result=update.answer_result,
            attempts=update.attempts,
            hints_used=update.hints_used,
            response_duration=update.response_duration,
            strategy_used=update.strategy_used,
            metaphor_used=update.metaphor_used
        )

        return {
            "success": True,
            "record_id": record.id,
            "message": "学习记录已保存"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.get("/progress/{student_id}")
async def get_student_progress(
    student_id: str,
    subject: str = Query("数学", description="科目")
) -> StudentProgress:
    """
    获取学生进度

    返回学生的详细学习进度统计
    """
    try:
        progress = tracker.get_student_progress(
            student_id=student_id,
            subject=subject
        )

        return progress

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/progress/{student_id}/summary")
async def get_progress_summary(
    student_id: str,
    subject: str = Query("数学", description="科目")
) -> ProgressSummary:
    """
    获取进度摘要

    返回简洁的进度摘要，适合家长快速查看
    """
    try:
        summary = tracker.get_progress_summary(
            student_id=student_id,
            subject=subject
        )

        return summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/report")
async def generate_learning_report(request: ReportRequest) -> LearningReport:
    """
    生成学习报告

    生成指定时间范围内的学习报告，包含详细的统计分析
    """
    try:
        report = tracker.generate_report(
            student_id=request.student_id,
            subject=request.subject,
            days=request.days
        )

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/records/{student_id}")
async def get_recent_records(
    student_id: str,
    subject: str = Query("数学", description="科目"),
    limit: int = Query(10, ge=1, le=100, description="返回数量")
):
    """
    获取最近的学习记录

    返回最近的答题记录，用于查看详细历史
    """
    try:
        records = tracker.get_recent_records(
            student_id=student_id,
            subject=subject,
            limit=limit
        )

        return {
            "student_id": student_id,
            "subject": subject,
            "count": len(records),
            "records": records
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查

    验证学习追踪服务是否正常运行
    """
    return {
        "status": "healthy",
        "service": "学习追踪服务",
        "total_records": len(tracker.records),
        "cached_progress": len(tracker.progress_cache)
    }
