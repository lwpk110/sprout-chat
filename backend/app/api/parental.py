"""
家长控制 API 端点

提供家长控制功能的 API 接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.services.parental_control import ParentalControlService
from app.models.parental_control import (
    TimeRestriction,
    DifficultySettings,
    ContentFilter,
    ReminderSettings,
    ParentalControlConfig,
    ControlCheck,
    DifficultyAdjustment,
    ContentFilterResult,
    DifficultyLevel,
    TimeLimitType,
    ContentType,
    FilterType
)


router = APIRouter(prefix="/api/v1/parental", tags=["家长控制"])

# 全局家长控制服务实例
service = ParentalControlService()


# ============ 时间限制端点 ============

@router.post("/time-restriction")
async def create_time_restriction(restriction: TimeRestriction):
    """
    创建时间限制

    设置学生的学习时间限制
    """
    try:
        created = service.create_time_restriction(
            student_id=restriction.student_id,
            limit_type=restriction.limit_type,
            max_minutes=restriction.max_minutes,
            allowed_start=restriction.allowed_start,
            allowed_end=restriction.allowed_end,
            allowed_days=restriction.allowed_days
        )

        return {
            "success": True,
            "restriction_id": created.restriction_id,
            "message": "时间限制已创建"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/time-limit/{student_id}")
async def check_time_limit(student_id: str) -> ControlCheck:
    """
    检查时间限制

    返回学生是否还能继续学习
    """
    try:
        return service.check_time_limit(student_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")


@router.post("/usage/{student_id}")
async def record_usage(student_id: str, minutes: int):
    """
    记录使用时长

    记录学生的学习时长
    """
    try:
        service.record_usage(student_id, minutes)

        return {
            "success": True,
            "message": f"已记录 {minutes} 分钟使用时长"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录失败: {str(e)}")


# ============ 难度调整端点 ============

@router.post("/difficulty-settings")
async def create_difficulty_settings(settings: DifficultySettings):
    """
    创建难度设置

    设置学生的学习难度
    """
    try:
        created = service.create_difficulty_settings(
            student_id=settings.student_id,
            subject=settings.subject,
            current_level=settings.current_level,
            adaptive_enabled=settings.adaptive_enabled,
            increase_threshold=settings.increase_threshold,
            decrease_threshold=settings.decrease_threshold
        )

        return {
            "success": True,
            "settings_id": created.settings_id,
            "message": "难度设置已创建"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/difficulty-suggestion/{student_id}")
async def get_difficulty_suggestion(
    student_id: str,
    subject: str = Query("数学", description="科目")
) -> Optional[DifficultyAdjustment]:
    """
    获取难度调整建议

    基于最近的学习情况建议难度调整
    """
    try:
        return service.suggest_difficulty_adjustment(student_id, subject)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.put("/difficulty-level/{student_id}")
async def update_difficulty_level(
    student_id: str,
    subject: str = Query("数学", description="科目"),
    new_level: DifficultyLevel = Query(..., description="新难度")
):
    """
    更新难度等级

    家长手动调整学习难度
    """
    try:
        updated = service.update_difficulty_level(
            student_id=student_id,
            subject=subject,
            new_level=new_level
        )

        return {
            "success": True,
            "current_level": updated.current_level,
            "message": "难度已更新"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


# ============ 内容过滤端点 ============

@router.post("/content-filter")
async def create_content_filter(content_filter: ContentFilter):
    """
    创建内容过滤器

    设置要屏蔽或限制的内容类型
    """
    try:
        created = service.create_content_filter(
            student_id=content_filter.student_id,
            filter_type=content_filter.filter_type,
            content_types=content_filter.content_types,
            reason=content_filter.reason
        )

        return {
            "success": True,
            "filter_id": created.filter_id,
            "message": "内容过滤器已创建"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/content-check/{student_id}")
async def check_content(
    student_id: str,
    content_type: ContentType = Query(..., description="内容类型")
) -> ContentFilterResult:
    """
    检查内容是否允许

    返回内容是否被过滤以及替代建议
    """
    try:
        return service.check_content(student_id, content_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")


# ============ 提醒设置端点 ============

@router.post("/reminder-settings")
async def create_reminder_settings(settings: ReminderSettings):
    """
    创建提醒设置

    设置学习提醒和休息提醒
    """
    try:
        created = service.create_reminder_settings(
            student_id=settings.student_id,
            reminder_before_end=settings.reminder_before_end,
            break_reminder=settings.break_reminder,
            break_duration=settings.break_duration
        )

        return {
            "success": True,
            "reminder_id": created.reminder_id,
            "message": "提醒设置已创建"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/reminder/{student_id}")
async def check_reminder(student_id: str):
    """
    检查时间提醒

    返回是否需要发送时间提醒
    """
    try:
        return service.check_reminder(student_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")


@router.get("/break-reminder/{student_id}")
async def check_break_reminder(student_id: str):
    """
    检查休息提醒

    返回是否需要发送休息提醒
    """
    try:
        return service.check_break_reminder(student_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")


# ============ 配置管理端点 ============

@router.post("/config")
async def create_config(student_id: str, parent_id: str):
    """
    创建家长控制配置

    为学生创建完整的家长控制配置
    """
    try:
        config = service.create_parental_control_config(
            student_id=student_id,
            parent_id=parent_id
        )

        return {
            "success": True,
            "config_id": config.config_id,
            "message": "配置已创建"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/config/{student_id}")
async def get_config(student_id: str) -> Optional[ParentalControlConfig]:
    """
    获取家长控制配置

    返回学生的完整家长控制配置
    """
    try:
        return service.get_parental_control_config(student_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查

    验证家长控制服务是否正常运行
    """
    return {
        "status": "healthy",
        "service": "家长控制服务",
        "total_configs": len(service.configs),
        "usage_records": len(service.usage_records)
    }
