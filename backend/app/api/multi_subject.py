"""
多科目支持与个性化推荐 API (LWP-6)

支持多科目学习记录追踪和基于学习模式的主题推荐
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from collections import defaultdict
from datetime import datetime

router = APIRouter(prefix="/api/v1/multi-subject", tags=["多科目学习"])

# 内存存储（生产环境应使用数据库）
_learning_records: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
_recommendation_cache: Dict[str, List[Dict[str, Any]]] = {}


# Pydantic 模型
class LearningRecord(BaseModel):
    """学习记录"""
    subject: str = Field(..., description="科目")
    topic: str = Field(..., description="主题")
    problem_type: str = Field(..., description="问题类型")
    difficulty: int = Field(..., ge=1, le=5, description="难度等级")
    is_correct: bool = Field(..., description="是否正确")
    time_spent_seconds: int = Field(..., ge=0, description="用时（秒）")
    hints_used: int = Field(..., ge=0, description="提示使用次数")


class SubjectProgress(BaseModel):
    """科目进度"""
    subject: str
    total_records: int
    correct_count: int
    accuracy_rate: float
    total_time_seconds: int
    avg_time_seconds: float
    topics_practiced: List[str]


class CrossSubjectProgress(BaseModel):
    """跨科目进度"""
    student_id: str
    subjects: List[SubjectProgress]
    total_records: int
    total_time_seconds: int


class TopicRecommendation(BaseModel):
    """主题推荐"""
    subject: str
    topic: str
    difficulty: int
    priority: str  # high, medium, low
    reason: str
    estimated_time_minutes: int


class LearningPathTopic(BaseModel):
    """学习路径主题"""
    subject: str
    topic: str
    difficulty: int
    priority_order: int
    mastery_level: str  # not_started, learning, mastered
    reason: str


class LearningPath(BaseModel):
    """学习路径"""
    student_id: str
    path: List[LearningPathTopic]
    total_topics: int


# 辅助函数
def _calculate_topic_stats(student_id: str, subject: Optional[str] = None) -> Dict[str, Dict]:
    """
    计算主题统计

    Returns:
        {topic: {accuracy, total_count, avg_time, hints_per_problem}}
    """
    records = _learning_records.get(student_id, [])

    if subject:
        records = [r for r in records if r["subject"] == subject]

    topic_stats = defaultdict(lambda: {
        "correct": 0,
        "total": 0,
        "total_time": 0,
        "hints": 0
    })

    for record in records:
        topic = record["topic"]
        topic_stats[topic]["total"] += 1
        if record["is_correct"]:
            topic_stats[topic]["correct"] += 1
        topic_stats[topic]["total_time"] += record["time_spent_seconds"]
        topic_stats[topic]["hints"] += record["hints_used"]

    # 计算派生指标
    result = {}
    for topic, stats in topic_stats.items():
        result[topic] = {
            "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else 0,
            "total_count": stats["total"],
            "avg_time": stats["total_time"] / stats["total"] if stats["total"] > 0 else 0,
            "hints_per_problem": stats["hints"] / stats["total"] if stats["total"] > 0 else 0
        }

    return result


def _get_available_topics(subject: str, difficulty: int) -> List[str]:
    """
    获取可用主题列表（简化版本）

    生产环境应从数据库或配置文件读取
    """
    topic_map = {
        "数学": {
            1: ["加法运算", "减法运算", "数字比较"],
            2: ["乘法入门", "除法入门", "简单应用题"],
            3: ["混合运算", "两步应用题", "时间计算"]
        },
        "阅读": {
            1: ["拼音识别", "汉字笔画", "简单词汇"],
            2: ["句子理解", "标点符号", "段落阅读"],
            3: ["阅读理解", "古诗背诵", "看图说话"]
        }
    }

    return topic_map.get(subject, {}).get(difficulty, [])


# API 端点
@router.post("/{student_id}/record")
async def record_learning(student_id: str, record: LearningRecord):
    """
    记录学习数据

    Args:
        student_id: 学生 ID
        record: 学习记录

    Returns:
        保存的记录
    """
    try:
        record_dict = {
            "student_id": student_id,
            "subject": record.subject,
            "topic": record.topic,
            "problem_type": record.problem_type,
            "difficulty": record.difficulty,
            "is_correct": record.is_correct,
            "time_spent_seconds": record.time_spent_seconds,
            "hints_used": record.hints_used,
            "timestamp": datetime.now().isoformat()
        }

        _learning_records[student_id].append(record_dict)

        # 清除推荐缓存
        if student_id in _recommendation_cache:
            del _recommendation_cache[student_id]

        return {
            "student_id": student_id,
            **record.model_dump()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}/progress")
async def get_cross_subject_progress(student_id: str):
    """
    获取跨科目学习进度

    Args:
        student_id: 学生 ID

    Returns:
        各科目的学习进度统计
    """
    try:
        records = _learning_records.get(student_id, [])

        if not records:
            return {
                "student_id": student_id,
                "subjects": [],
                "total_records": 0,
                "total_time_seconds": 0
            }

        # 按科目分组
        subject_records = defaultdict(list)
        for record in records:
            subject_records[record["subject"]].append(record)

        # 计算每个科目的进度
        subjects_progress = []
        for subject, subj_records in subject_records.items():
            correct_count = sum(1 for r in subj_records if r["is_correct"])
            total_time = sum(r["time_spent_seconds"] for r in subj_records)
            topics = list(set(r["topic"] for r in subj_records))

            subjects_progress.append({
                "subject": subject,
                "total_records": len(subj_records),
                "correct_count": correct_count,
                "accuracy_rate": round(correct_count / len(subj_records), 2),
                "total_time_seconds": total_time,
                "avg_time_seconds": round(total_time / len(subj_records), 1),
                "topics_practiced": topics
            })

        return {
            "student_id": student_id,
            "subjects": subjects_progress,
            "total_records": len(records),
            "total_time_seconds": sum(r["time_spent_seconds"] for r in records)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}/recommendations")
async def get_recommendations(student_id: str):
    """
    获取个性化主题推荐

    Args:
        student_id: 学生 ID

    Returns:
        推荐的主题列表
    """
    try:
        # 检查缓存
        if student_id in _recommendation_cache:
            return {"recommendations": _recommendation_cache[student_id]}

        recommendations = []
        records = _learning_records.get(student_id, [])

        if not records:
            # 新学生：返回基础主题推荐
            for subject in ["数学", "阅读"]:
                for topic in _get_available_topics(subject, 1):
                    recommendations.append({
                        "subject": subject,
                        "topic": topic,
                        "difficulty": 1,
                        "priority": "medium",
                        "reason": "基础入门",
                        "estimated_time_minutes": 15
                    })
        else:
            # 计算主题统计
            topic_stats = _calculate_topic_stats(student_id)

            # 为每个科目生成推荐
            for subject in ["数学", "阅读"]:
                # 查找该科目的薄弱主题
                subject_topics = {k: v for k, v in topic_stats.items()
                                if any(r["subject"] == subject and r["topic"] == k
                                      for r in records)}

                if subject_topics:
                    # 按准确率排序，优先推荐薄弱环节
                    sorted_topics = sorted(subject_topics.items(),
                                          key=lambda x: x[1]["accuracy"])

                    for topic, stats in sorted_topics[:3]:  # 取前3个最需要改进的主题
                        if stats["accuracy"] < 0.6:
                            priority = "high"
                            reason = "weak_area"
                        elif stats["accuracy"] < 0.8:
                            priority = "medium"
                            reason = "needs_practice"
                        else:
                            priority = "low"
                            reason = "maintenance"

                        # 判断是否需要提升难度
                        difficulty = 1
                        if stats["accuracy"] >= 0.8 and stats["hints_per_problem"] < 1 and stats["avg_time"] < 30:
                            difficulty = 2
                            reason = "ready_for_advance"

                        recommendations.append({
                            "subject": subject,
                            "topic": topic,
                            "difficulty": difficulty,
                            "priority": priority,
                            "reason": reason,
                            "estimated_time_minutes": int(stats["avg_time"] / 60) + 5
                        })
                else:
                    # 该科目还没有记录，推荐基础主题
                    for topic in _get_available_topics(subject, 1)[:2]:
                        recommendations.append({
                            "subject": subject,
                            "topic": topic,
                            "difficulty": 1,
                            "priority": "medium",
                            "reason": "new_subject",
                            "estimated_time_minutes": 15
                        })

        # 缓存推荐结果
        _recommendation_cache[student_id] = recommendations

        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}/learning-path")
async def generate_learning_path(student_id: str):
    """
    生成个性化学习路径

    Args:
        student_id: 学生 ID

    Returns:
        按优先级排序的学习路径
    """
    try:
        records = _learning_records.get(student_id, [])

        if not records:
            # 新学生：返回基础学习路径
            return {
                "student_id": student_id,
                "path": [
                    {
                        "subject": "数学",
                        "topic": topic,
                        "difficulty": 1,
                        "priority_order": i + 1,
                        "mastery_level": "not_started",
                        "reason": "基础入门"
                    }
                    for i, topic in enumerate(_get_available_topics("数学", 1)[:3])
                ],
                "total_topics": 3
            }

        # 计算主题统计
        topic_stats = _calculate_topic_stats(student_id)

        # 构建学习路径
        path_topics = []

        for topic, stats in topic_stats.items():
            # 判断掌握程度
            if stats["accuracy"] >= 0.8 and stats["total_count"] >= 5:
                mastery = "mastered"
                reason = "已掌握"
            elif stats["total_count"] >= 3:
                mastery = "learning"
                reason = "学习中"
            else:
                mastery = "not_started"
                reason = "需要加强"

            # 从记录中获取科目和难度
            topic_record = next((r for r in records if r["topic"] == topic), None)
            if topic_record:
                path_topics.append({
                    "subject": topic_record["subject"],
                    "topic": topic,
                    "difficulty": topic_record["difficulty"],
                    "mastery_level": mastery,
                    "reason": reason,
                    "stats": stats  # 用于后续排序
                })

        # 排序规则：
        # 1. 未掌握 > 学习中 > 已掌握
        # 2. 准确率低的优先
        # 3. 同等条件下，总次数少的优先（需要更多练习）
        mastery_order = {"not_started": 0, "learning": 1, "mastered": 2}

        path_topics.sort(key=lambda x: (
            mastery_order.get(x["mastery_level"], 3),
            x["stats"]["accuracy"],  # 准确率低的排在前面（不使用负号）
            x["stats"]["total_count"]  # 次数少的优先
        ))

        # 添加优先级序号并移除 stats 字段
        path = []
        for i, topic in enumerate(path_topics):
            topic_data = {
                "subject": topic["subject"],
                "topic": topic["topic"],
                "difficulty": topic["difficulty"],
                "priority_order": i + 1,
                "mastery_level": topic["mastery_level"],
                "reason": topic["reason"]
            }
            path.append(LearningPathTopic(**topic_data))

        return {
            "student_id": student_id,
            "path": [t.model_dump() for t in path],
            "total_topics": len(path)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
