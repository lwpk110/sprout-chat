"""
父母报告 API 端点 (LWP-4) - 简化版本

为父母仪表板提供学习进度和活动报告

注意：使用内存存储，生产环境应替换为数据库查询
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.learning import AnswerResult, ProblemType

router = APIRouter(prefix="/api/v1", tags=["父母报告"])

# 内存存储（用于演示）
_records_storage: Dict[str, List[Dict[str, Any]]] = defaultdict(list)


@router.get("/reports/{student_id}")
async def get_report_summary(
    student_id: str,
    period: str = Query("week", description="报告周期: day, week, month")
):
    """
    获取学习报告摘要

    Args:
        student_id: 学生 ID
        period: 报告周期（day/week/month）

    Returns:
        报告摘要，包含总学习时间、会话数、准确率、主题列表
    """
    try:
        # 从内存存储获取该学生的所有记录
        records = _records_storage.get(student_id, [])

        if not records:
            return {
                "student_id": student_id,
                "period": period,
                "total_sessions": 0,
                "total_time_minutes": 0,
                "accuracy_rate": 0.0,
                "topics_practiced": [],
                "subjects_studied": []
            }

        # 聚合统计
        total_sessions = len(records)
        total_time_seconds = sum(
            r.get("response_duration", 0) for r in records
        )
        total_time_minutes = int(total_time_seconds / 60) if total_time_seconds else 0

        correct_count = 0
        topics = set()
        subjects = set()

        for r in records:
            # 检查答案结果
            answer_result = r.get("answer_result")
            if answer_result:
                if isinstance(answer_result, str):
                    if answer_result == "correct":
                        correct_count += 1
                elif hasattr(answer_result, 'value'):
                    if answer_result.value == "correct":
                        correct_count += 1

            # 收集主题
            problem_type = r.get("problem_type")
            if problem_type:
                if isinstance(problem_type, str):
                    topics.add(problem_type)
                elif hasattr(problem_type, 'value'):
                    topics.add(problem_type.value)

            # 收集科目
            subject = r.get("subject")
            if subject:
                subjects.add(subject)

        accuracy_rate = correct_count / total_sessions if total_sessions > 0 else 0.0

        return {
            "student_id": student_id,
            "period": period,
            "total_sessions": total_sessions,
            "total_time_minutes": total_time_minutes,
            "accuracy_rate": round(accuracy_rate, 2),
            "topics_practiced": list(topics),
            "subjects_studied": list(subjects)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{student_id}/struggling-topics")
async def get_struggling_topics(student_id: str):
    """
    识别困难主题

    Args:
        student_id: 学生 ID

    Returns:
        困难主题列表
    """
    try:
        records = _records_storage.get(student_id, [])

        # 按问题类型分组
        topic_stats = {}

        for r in records:
            # 获取问题类型
            problem_type_str = None
            problem_type = r.get("problem_type")
            if problem_type:
                if isinstance(problem_type, str):
                    problem_type_str = problem_type
                elif hasattr(problem_type, 'value'):
                    problem_type_str = problem_type.value

            if not problem_type_str:
                continue

            if problem_type_str not in topic_stats:
                topic_stats[problem_type_str] = {
                    "problem_type": problem_type_str,
                    "total": 0,
                    "correct": 0,
                    "hints": 0
                }

            topic_stats[problem_type_str]["total"] += 1

            # 检查是否正确
            answer_result = r.get("answer_result")
            if answer_result:
                is_correct = False
                if isinstance(answer_result, str):
                    is_correct = answer_result == "correct"
                elif hasattr(answer_result, 'value'):
                    is_correct = answer_result.value == "correct"

                if is_correct:
                    topic_stats[problem_type_str]["correct"] += 1

            # 统计提示
            hints_used = r.get("hints_used", 0)
            if hints_used:
                topic_stats[problem_type_str]["hints"] += hints_used

        # 识别困难主题
        struggling = []
        for topic, stats in topic_stats.items():
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            avg_hints = stats["hints"] / stats["total"] if stats["total"] > 0 else 0

            if accuracy < 0.5 or avg_hints > 1:
                struggling.append({
                    "problem_type": topic,
                    "accuracy_rate": round(accuracy, 2),
                    "avg_hints_needed": round(avg_hints, 1),
                    "total_attempts": stats["total"],
                    "severity": "high" if accuracy < 0.3 else "medium"
                })

        # 按准确率排序
        struggling.sort(key=lambda x: x["accuracy_rate"])

        return {
            "student_id": student_id,
            "struggling_topics": struggling
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
