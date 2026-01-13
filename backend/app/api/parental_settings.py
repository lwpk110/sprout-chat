"""
父母设置管理 API 端点 (LWP-5)

允许父母设置使用限制、学习目标和家教行为偏好
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from collections import defaultdict

router = APIRouter(prefix="/api/v1/parental", tags=["父母设置"])

# 内存存储（生产环境应使用数据库）
_settings_storage: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
    "usage_limits": {
        "daily_time_limit_minutes": None,
        "weekly_time_limit_minutes": None
    },
    "learning_goals": {
        "daily_problem_count_goal": None,
        "accuracy_rate_goal": None
    },
    "tutor_preferences": {
        "scaffolding_level": "medium",
        "teaching_style": "socratic"
    }
})


# Pydantic 模型
class UsageLimits(BaseModel):
    """使用限制设置"""
    daily_time_limit_minutes: Optional[int] = Field(None, ge=0, description="每日时间限制（分钟）")
    weekly_time_limit_minutes: Optional[int] = Field(None, ge=0, description="每周时间限制（分钟）")


class LearningGoals(BaseModel):
    """学习目标设置"""
    daily_problem_count_goal: Optional[int] = Field(None, ge=1, description="每日题目数量目标")
    accuracy_rate_goal: Optional[float] = Field(None, ge=0.0, le=1.0, description="准确率目标（0-1）")


class TutorPreferences(BaseModel):
    """家教行为偏好"""
    scaffolding_level: str = Field("medium", pattern="^(low|medium|high)$", description="脚手架层级")
    teaching_style: str = Field("socratic", pattern="^(socratic|interactive|direct)$", description="教学风格")


class AllSettings(BaseModel):
    """所有设置"""
    student_id: str
    usage_limits: UsageLimits
    learning_goals: LearningGoals
    tutor_preferences: TutorPreferences


# API 端点
@router.put("/settings/{student_id}/usage-limits")
async def set_usage_limits(student_id: str, limits: UsageLimits):
    """
    设置使用限制

    Args:
        student_id: 学生 ID
        limits: 使用限制设置

    Returns:
        更新后的使用限制
    """
    try:
        # 获取现有设置
        settings = _settings_storage[student_id]

        # 更新使用限制
        settings["usage_limits"] = {
            "daily_time_limit_minutes": limits.daily_time_limit_minutes,
            "weekly_time_limit_minutes": limits.weekly_time_limit_minutes
        }

        return {
            "student_id": student_id,
            **settings["usage_limits"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/{student_id}/usage-limits")
async def get_usage_limits(student_id: str):
    """
    获取使用限制

    Args:
        student_id: 学生 ID

    Returns:
        使用限制设置
    """
    try:
        settings = _settings_storage.get(student_id)

        if not settings:
            return {
                "student_id": student_id,
                "daily_time_limit_minutes": None,
                "weekly_time_limit_minutes": None
            }

        return {
            "student_id": student_id,
            **settings["usage_limits"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings/{student_id}/learning-goals")
async def set_learning_goals(student_id: str, goals: LearningGoals):
    """
    设置学习目标

    Args:
        student_id: 学生 ID
        goals: 学习目标设置

    Returns:
        更新后的学习目标
    """
    try:
        # 获取现有设置
        settings = _settings_storage[student_id]

        # 更新学习目标
        settings["learning_goals"] = {
            "daily_problem_count_goal": goals.daily_problem_count_goal,
            "accuracy_rate_goal": goals.accuracy_rate_goal
        }

        return {
            "student_id": student_id,
            **settings["learning_goals"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/{student_id}/learning-goals")
async def get_learning_goals(student_id: str):
    """
    获取学习目标

    Args:
        student_id: 学生 ID

    Returns:
        学习目标设置
    """
    try:
        settings = _settings_storage.get(student_id)

        if not settings:
            return {
                "student_id": student_id,
                "daily_problem_count_goal": None,
                "accuracy_rate_goal": None
            }

        return {
            "student_id": student_id,
            **settings["learning_goals"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings/{student_id}/tutor-preferences")
async def set_tutor_preferences(student_id: str, preferences: TutorPreferences):
    """
    设置家教行为偏好

    Args:
        student_id: 学生 ID
        preferences: 家教偏好设置

    Returns:
        更新后的家教偏好
    """
    try:
        # 获取现有设置
        settings = _settings_storage[student_id]

        # 更新家教偏好
        settings["tutor_preferences"] = {
            "scaffolding_level": preferences.scaffolding_level,
            "teaching_style": preferences.teaching_style
        }

        return {
            "student_id": student_id,
            **settings["tutor_preferences"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/{student_id}/tutor-preferences")
async def get_tutor_preferences(student_id: str):
    """
    获取家教行为偏好

    Args:
        student_id: 学生 ID

    Returns:
        家教偏好设置
    """
    try:
        settings = _settings_storage.get(student_id)

        if not settings:
            return {
                "student_id": student_id,
                "scaffolding_level": "medium",
                "teaching_style": "socratic"
            }

        return {
            "student_id": student_id,
            **settings["tutor_preferences"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/{student_id}")
async def get_all_settings(student_id: str):
    """
    获取所有设置

    Args:
        student_id: 学生 ID

    Returns:
        所有设置（使用限制、学习目标、家教偏好）
    """
    try:
        settings = _settings_storage.get(student_id)

        if not settings:
            # 返回默认设置
            return {
                "student_id": student_id,
                "usage_limits": {
                    "daily_time_limit_minutes": None,
                    "weekly_time_limit_minutes": None
                },
                "learning_goals": {
                    "daily_problem_count_goal": None,
                    "accuracy_rate_goal": None
                },
                "tutor_preferences": {
                    "scaffolding_level": "medium",
                    "teaching_style": "socratic"
                }
            }

        return {
            "student_id": student_id,
            **settings
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
