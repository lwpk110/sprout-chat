"""
家长控制服务测试 - TDD Red Phase

测试家长的控制功能：
- 时间限制
- 难度调整
- 内容过滤
- 提醒设置
"""

import pytest
from datetime import datetime, time, timedelta
from app.services.parental_control import ParentalControlService
from app.models.parental_control import (
    TimeRestriction,
    DifficultySettings,
    ContentFilter,
    ReminderSettings,
    ParentalControlConfig,
    ControlCheck,
    DifficultyLevel,
    TimeLimitType,
    ContentType,
    FilterType
)


@pytest.fixture
def service():
    """创建家长控制服务实例"""
    service = ParentalControlService()
    # 清理测试数据
    service.clear_all_data()
    yield service
    # 清理
    service.clear_all_data()


class TestTimeRestrictions:
    """测试：时间限制"""

    def test_create_daily_time_limit(self, service):
        """
        测试：创建每日时间限制

        验证能够设置每日最大学习时长
        """
        restriction = service.create_time_restriction(
            student_id="student_001",
            limit_type=TimeLimitType.DAILY,
            max_minutes=60
        )

        assert restriction is not None
        assert restriction.student_id == "student_001"
        assert restriction.limit_type == TimeLimitType.DAILY
        assert restriction.max_minutes == 60

    def test_check_time_limit_not_exceeded(self, service):
        """
        测试：检查时间限制（未超限）

        验证在时间限制内允许学习
        """
        student_id = "student_time_check"

        # 设置每日限制60分钟
        service.create_time_restriction(
            student_id=student_id,
            limit_type=TimeLimitType.DAILY,
            max_minutes=60
        )

        # 记录30分钟使用
        service.record_usage(student_id, 30)

        # 检查是否允许
        check = service.check_time_limit(student_id)

        assert check.allowed == True
        assert check.remaining_minutes == 30

    def test_check_time_limit_exceeded(self, service):
        """
        测试：检查时间限制（已超限）

        验证超过时间限制后拒绝学习
        """
        student_id = "student_exceeded"

        # 设置每日限制30分钟
        service.create_time_restriction(
            student_id=student_id,
            limit_type=TimeLimitType.DAILY,
            max_minutes=30
        )

        # 记录35分钟使用
        service.record_usage(student_id, 35)

        # 检查是否允许
        check = service.check_time_limit(student_id)

        assert check.allowed == False
        assert "超过时间限制" in check.reason or "时间限制" in check.reason

    def test_time_window_restriction(self, service):
        """
        测试：时间窗口限制

        验证只能在指定时间段内学习
        """
        student_id = "student_window"

        # 设置只能在8:00-20:00学习
        service.create_time_restriction(
            student_id=student_id,
            limit_type=TimeLimitType.DAILY,
            max_minutes=120,
            allowed_start=time(8, 0),
            allowed_end=time(20, 0)
        )

        # 检查当前时间是否在允许窗口内
        check = service.check_time_window(student_id)

        # 根据当前时间判断结果
        current_hour = datetime.now().hour
        if 8 <= current_hour < 20:
            assert check.allowed == True
        else:
            assert check.allowed == False


class TestDifficultyAdjustment:
    """测试：难度调整"""

    def test_create_difficulty_settings(self, service):
        """
        测试：创建难度设置

        验证能够设置学习难度
        """
        settings = service.create_difficulty_settings(
            student_id="student_001",
            subject="数学",
            current_level=DifficultyLevel.MEDIUM
        )

        assert settings is not None
        assert settings.student_id == "student_001"
        assert settings.current_level == DifficultyLevel.MEDIUM

    def test_adaptive_difficulty_increase(self, service):
        """
        测试：自适应难度提升

        验证正确率高时自动提升难度
        """
        student_id = "student_adaptive_increase"

        # 启用自适应
        service.create_difficulty_settings(
            student_id=student_id,
            subject="数学",
            current_level=DifficultyLevel.MEDIUM,
            adaptive_enabled=True
        )

        # 模拟高正确率（85%）
        for i in range(20):
            service.record_answer(
                student_id=student_id,
                subject="数学",
                problem_type="加法",
                correct=i < 17  # 17/20 = 85%
            )

        # 获取调整建议
        adjustment = service.suggest_difficulty_adjustment(student_id, "数学")

        assert adjustment is not None
        assert adjustment.suggested_level == DifficultyLevel.HARD

    def test_adaptive_difficulty_decrease(self, service):
        """
        测试：自适应难度降低

        验证正确率低时自动降低难度
        """
        student_id = "student_adaptive_decrease"

        # 启用自适应
        service.create_difficulty_settings(
            student_id=student_id,
            subject="数学",
            current_level=DifficultyLevel.MEDIUM,
            adaptive_enabled=True
        )

        # 模拟低正确率（40%）
        for i in range(20):
            service.record_answer(
                student_id=student_id,
                subject="数学",
                problem_type="加法",
                correct=i < 8  # 8/20 = 40%
            )

        # 获取调整建议
        adjustment = service.suggest_difficulty_adjustment(student_id, "数学")

        assert adjustment is not None
        assert adjustment.suggested_level == DifficultyLevel.EASY

    def test_manual_difficulty_adjustment(self, service):
        """
        测试：手动调整难度

        验证家长可以手动设置难度
        """
        student_id = "student_manual"

        # 创建设置
        settings = service.create_difficulty_settings(
            student_id=student_id,
            subject="数学",
            current_level=DifficultyLevel.EASY
        )

        # 手动调整
        updated = service.update_difficulty_level(
            student_id=student_id,
            subject="数学",
            new_level=DifficultyLevel.HARD
        )

        assert updated.current_level == DifficultyLevel.HARD


class TestContentFiltering:
    """测试：内容过滤"""

    def test_create_content_filter(self, service):
        """
        测试：创建内容过滤器

        验证能够设置内容过滤规则
        """
        filter = service.create_content_filter(
            student_id="student_001",
            filter_type=FilterType.BLOCK,
            content_types=[ContentType.MULTIPLICATION, ContentType.DIVISION]
        )

        assert filter is not None
        assert filter.student_id == "student_001"
        assert filter.filter_type == FilterType.BLOCK
        assert len(filter.content_types) == 2

    def test_check_content_allowed(self, service):
        """
        测试：检查内容是否允许（允许）

        验证未过滤的内容可以学习
        """
        student_id = "student_filter"

        # 屏蔽乘法和除法
        service.create_content_filter(
            student_id=student_id,
            filter_type=FilterType.BLOCK,
            content_types=[ContentType.MULTIPLICATION, ContentType.DIVISION]
        )

        # 检查加法（应该允许）
        result = service.check_content(
            student_id=student_id,
            content_type=ContentType.ADDITION
        )

        assert result.allowed == True

    def test_check_content_blocked(self, service):
        """
        测试：检查内容是否允许（屏蔽）

        验证已过滤的内容不能学习
        """
        student_id = "student_blocked"

        # 屏蔽乘法和除法
        service.create_content_filter(
            student_id=student_id,
            filter_type=FilterType.BLOCK,
            content_types=[ContentType.MULTIPLICATION, ContentType.DIVISION]
        )

        # 检查乘法（应该屏蔽）
        result = service.check_content(
            student_id=student_id,
            content_type=ContentType.MULTIPLICATION
        )

        assert result.allowed == False
        assert result.filtered_content == "乘法"

    def test_get_alternative_content(self, service):
        """
        测试：获取替代内容

        验证为被屏蔽的内容提供替代方案
        """
        student_id = "student_alternative"

        # 屏蔽乘除法
        service.create_content_filter(
            student_id=student_id,
            filter_type=FilterType.BLOCK,
            content_types=[ContentType.MULTIPLICATION, ContentType.DIVISION]
        )

        # 获取乘法的替代内容
        result = service.check_content(
            student_id=student_id,
            content_type=ContentType.MULTIPLICATION
        )

        assert result.allowed == False
        # 应该提供加法或减法作为替代
        assert len(result.alternatives) > 0


class TestReminderSettings:
    """测试：提醒设置"""

    def test_create_reminder_settings(self, service):
        """
        测试：创建提醒设置

        验证能够设置学习提醒
        """
        settings = service.create_reminder_settings(
            student_id="student_001",
            reminder_before_end=5,
            break_reminder=20
        )

        assert settings is not None
        assert settings.student_id == "student_001"
        assert settings.reminder_before_end == 5
        assert settings.break_reminder == 20

    def test_check_time_reminder(self, service):
        """
        测试：检查时间提醒

        验证在接近时间限制时发送提醒
        """
        student_id = "student_reminder"

        # 设置每日限制30分钟，提前5分钟提醒
        service.create_time_restriction(
            student_id=student_id,
            limit_type=TimeLimitType.DAILY,
            max_minutes=30
        )

        service.create_reminder_settings(
            student_id=student_id,
            reminder_before_end=5
        )

        # 记录26分钟使用（还剩4分钟）
        service.record_usage(student_id, 26)

        # 检查是否需要提醒
        reminder = service.check_reminder(student_id)

        assert reminder["should_remind"] == True

    def test_check_break_reminder(self, service):
        """
        测试：检查休息提醒

        验证连续学习一定时间后提醒休息
        """
        student_id = "student_break"

        # 设置每20分钟提醒休息
        service.create_reminder_settings(
            student_id=student_id,
            break_reminder=20
        )

        # 记录20分钟连续学习
        service.record_usage(student_id, 20)

        # 检查是否需要休息
        reminder = service.check_break_reminder(student_id)

        assert reminder["should_remind"] == True


class TestParentalControlConfig:
    """测试：家长控制总配置"""

    def test_create_full_config(self, service):
        """
        测试：创建完整配置

        验证能够创建包含所有控制的完整配置
        """
        config = service.create_parental_control_config(
            student_id="student_001",
            parent_id="parent_001"
        )

        assert config is not None
        assert config.student_id == "student_001"
        assert config.parent_id == "parent_001"

    def test_get_config(self, service):
        """
        测试：获取配置

        验证能够获取学生的家长控制配置
        """
        student_id = "student_get_config"

        # 创建配置
        service.create_parental_control_config(
            student_id=student_id,
            parent_id="parent_001"
        )

        # 获取配置
        config = service.get_parental_control_config(student_id)

        assert config is not None
        assert config.student_id == student_id

    def test_update_config(self, service):
        """
        测试：更新配置

        验证能够更新家长控制配置
        """
        student_id = "student_update_config"

        # 创建配置
        service.create_parental_control_config(
            student_id=student_id,
            parent_id="parent_001"
        )

        # 添加时间限制
        service.create_time_restriction(
            student_id=student_id,
            limit_type=TimeLimitType.DAILY,
            max_minutes=60
        )

        # 获取更新后的配置
        config = service.get_parental_control_config(student_id)

        assert len(config.time_restrictions) == 1


# Red Phase 标记
# pytestmark = pytest.mark.red_phase
