"""
学习追踪 API 端点（Phase 2.2 扩展）

提供家长监控功能的 API 接口
- Phase 2.1: 内存存储（原有功能）
- Phase 2.2: 数据库持久化（新增功能）
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.services.learning_tracker import LearningTracker
from app.models.database import get_db
from app.models.database import (
    LearningRecord as LearningRecordModel,
    Student as StudentModel,
    WrongAnswerRecord as WrongAnswerRecordModel,
)
from app.models.learning import (
    ProgressUpdate,
    ReportRequest,
    ProgressSummary,
    LearningRecord,
    StudentProgress,
    LearningReport
)
from app.models.learning_requests import (
    CreateLearningRecordRequest,
    LearningRecordResponse,
    LearningRecordDetailResponse,
    LearningProgressResponse,
    LearningReportResponse,
    QuestionTypeStats,
    DifficultyLevelStats,
)


router = APIRouter(prefix="/api/v1/learning", tags=["学习追踪"])

# 全局学习追踪器实例
tracker = LearningTracker()


# =============================================================================
# Phase 2.2: 新端点（数据库持久化）
# =============================================================================

@router.post("/records", response_model=LearningRecordResponse, status_code=201)
async def create_learning_record(
    request: CreateLearningRecordRequest,
    db: Session = Depends(get_db)
):
    """
    创建学习记录（Phase 2.2）

    记录一次答题活动，包含问题内容、学生答案、正确答案等信息。
    如果学生答错，系统会自动创建错题记录。
    """
    # 判断答案是否正确
    is_correct = request.student_answer.strip() == request.correct_answer.strip()
    answer_result = "correct" if is_correct else "incorrect"

    # 创建学习记录
    record = LearningRecordModel(
        student_id=request.student_id,
        question_content=request.question_content,
        question_type=request.question_type,
        subject=request.subject,
        difficulty_level=request.difficulty_level,
        student_answer=request.student_answer,
        correct_answer=request.correct_answer,
        is_correct=is_correct,
        answer_result=answer_result,
        time_spent_seconds=request.time_spent_seconds,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    # 如果答错，创建错题记录
    if not is_correct:
        # 使用错误分类器判断错误类型
        from app.services.wrong_analyzer import WrongAnswerClassifier
        classifier = WrongAnswerClassifier()
        error_type = classifier.classify(
            question=request.question_content,
            student_answer=request.student_answer,
            correct_answer=request.correct_answer,
            attempts=1
        )

        wrong_record = WrongAnswerRecordModel(
            learning_record_id=record.id,
            error_type=error_type,
            guidance_type="hint",  # TODO: 根据错误类型和尝试次数选择引导类型
            guidance_content="让我来帮你检查一下。你一开始有 3 个苹果，妈妈又给了你 5 个，你能用手指或画图的方式数一数，一共有多少个苹果吗？",
            is_resolved=False,
            created_at=datetime.utcnow(),
        )
        db.add(wrong_record)
        db.commit()

    return record


@router.get("/records", response_model=dict)
async def list_learning_records(
    student_id: int = Query(...),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    is_correct: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    查询学习记录列表（Phase 2.2）

    查询指定学生的学习记录，支持按时间范围、题目类型、是否正确等条件筛选。
    """
    # 构建查询
    query = db.query(LearningRecordModel).filter(LearningRecordModel.student_id == student_id)

    # 应用筛选条件
    if start_date:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(LearningRecordModel.created_at >= start_datetime)

    if end_date:
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(LearningRecordModel.created_at <= end_datetime)

    if question_type:
        query = query.filter(LearningRecordModel.question_type == question_type)

    if is_correct is not None:
        query = query.filter(LearningRecordModel.is_correct == is_correct)

    # 计算总数
    total = query.count()

    # 分页
    records = query.order_by(LearningRecordModel.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 转换为字典列表（用于 JSON 序列化）
    records_data = []
    for record in records:
        record_dict = {
            "id": record.id,
            "student_id": record.student_id,
            "question_content": record.question_content,
            "question_type": record.question_type,
            "subject": record.subject,
            "difficulty_level": record.difficulty_level,
            "student_answer": record.student_answer,
            "correct_answer": record.correct_answer,
            "is_correct": record.is_correct,
            "time_spent_seconds": record.time_spent_seconds,
            "created_at": record.created_at,
        }
        records_data.append(record_dict)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "records": records_data
    }


@router.get("/records/{record_id}", response_model=LearningRecordDetailResponse)
async def get_learning_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    获取学习记录详情（Phase 2.2）

    获取指定学习记录的详细信息，包括错题记录（如果存在）。
    """
    record = db.query(LearningRecordModel).filter(LearningRecordModel.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Learning record not found")

    # 查询关联的错题记录
    wrong_record = db.query(WrongAnswerRecordModel).filter(
        WrongAnswerRecordModel.learning_record_id == record_id
    ).first()

    return {
        **record.__dict__,
        "wrong_answer_record": wrong_record
    }


@router.get("/progress", response_model=LearningProgressResponse)
async def get_learning_progress(
    student_id: int = Query(...),
    time_range: str = Query("all", pattern="^(today|week|month|all)$"),
    db: Session = Depends(get_db)
):
    """
    获取学习进度统计（Phase 2.2）

    获取学生的学习进度统计数据，包括总题数、正确率、连续答对次数等指标。
    """
    # 构建查询
    query = db.query(LearningRecordModel).filter(LearningRecordModel.student_id == student_id)

    # 应用时间范围筛选
    if time_range == "today":
        today = datetime.utcnow().date()
        query = query.filter(LearningRecordModel.created_at >= today)
    elif time_range == "week":
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(LearningRecordModel.created_at >= week_ago)
    elif time_range == "month":
        month_ago = datetime.utcnow() - timedelta(days=30)
        query = query.filter(LearningRecordModel.created_at >= month_ago)

    # 统计数据
    records = query.all()
    total_questions = len(records)
    correct_count = sum(1 for r in records if r.is_correct)
    wrong_count = total_questions - correct_count
    accuracy_rate = (correct_count / total_questions * 100) if total_questions > 0 else 0.0

    # 计算连续答对次数
    current_streak = 0
    for record in reversed(records):
        if record.is_correct:
            current_streak += 1
        else:
            break

    # TODO: 计算最长连续答对记录
    longest_streak = current_streak  # 简化实现

    # 时间统计
    total_time_spent = sum(r.time_spent_seconds for r in records)
    avg_time = total_time_spent / total_questions if total_questions > 0 else 0.0

    return {
        "student_id": student_id,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "accuracy_rate": accuracy_rate,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_time_spent_seconds": total_time_spent,
        "average_time_per_question_seconds": avg_time,
        "time_range": time_range
    }


@router.get("/report", response_model=LearningReportResponse)
async def generate_learning_report(
    student_id: int = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    生成学习进度报告（Phase 2.2）

    生成学生的学习进度报告，包含学习统计、按题型正确率分布、按难度等级表现等。
    """
    # 解析日期
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    # 构建查询
    query = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id,
        LearningRecordModel.created_at >= start_datetime,
        LearningRecordModel.created_at <= end_datetime
    )

    records = query.all()
    total_questions = len(records)
    correct_count = sum(1 for r in records if r.is_correct)
    wrong_count = total_questions - correct_count

    # 按题型统计
    question_type_stats = {}
    for record in records:
        qtype = record.question_type
        if qtype not in question_type_stats:
            question_type_stats[qtype] = {"total": 0, "correct": 0}
        question_type_stats[qtype]["total"] += 1
        if record.is_correct:
            question_type_stats[qtype]["correct"] += 1

    by_question_type = [
        QuestionTypeStats(
            question_type=qtype,
            total_count=stats["total"],
            correct_count=stats["correct"],
            accuracy_rate=(stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
        )
        for qtype, stats in question_type_stats.items()
    ]

    # 按难度统计
    difficulty_stats = {}
    for record in records:
        level = record.difficulty_level
        if level not in difficulty_stats:
            difficulty_stats[level] = {"total": 0, "correct": 0}
        difficulty_stats[level]["total"] += 1
        if record.is_correct:
            difficulty_stats[level]["correct"] += 1

    by_difficulty_level = [
        DifficultyLevelStats(
            difficulty_level=level,
            total_count=stats["total"],
            correct_count=stats["correct"],
            accuracy_rate=(stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
        )
        for level, stats in sorted(difficulty_stats.items())
    ]

    # 连续答对记录
    current_streak = 0
    for record in reversed(records):
        if record.is_correct:
            current_streak += 1
        else:
            break

    return {
        "student_id": student_id,
        "period_start": start_date,
        "period_end": end_date,
        "summary": {
            "total_questions": total_questions,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "accuracy_rate": (correct_count / total_questions * 100) if total_questions > 0 else 0.0,
            "total_time_seconds": sum(r.time_spent_seconds for r in records),
        },
        "by_question_type": by_question_type,
        "by_difficulty_level": by_difficulty_level,
        "streak_records": {
            "current_streak": current_streak,
            "longest_streak": current_streak,  # TODO: 实现真正的最长记录
        }
    }


# =============================================================================
# Phase 2.1: 原有端点（保留向后兼容）
# =============================================================================


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
