"""
测试父母设置管理 API (LWP-5)

测试覆盖：
- 使用限制设置（每日/每周时间）
- 学习目标配置（题目数量、准确率）
- 家教行为偏好（脚手架层级、教学风格）
- 设置的读取和更新
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from pydantic import ValidationError


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_settings():
    """
    自动清理设置存储，确保测试隔离
    """
    from app.api.parental_settings import _settings_storage
    # 测试前清理
    _settings_storage.clear()
    yield
    # 测试后清理
    _settings_storage.clear()


class TestUsageLimits:
    """测试使用限制设置"""

    def test_set_daily_time_limit(self):
        """
        测试：设置每日时间限制

        Given: 父母想要限制孩子每日使用时间
        When: 设置每日 60 分钟限制
        Then: 保存成功并可读取
        """
        student_id = "student_001"

        response = client.put(
            f"/api/v1/parental/settings/{student_id}/usage-limits",
            json={
                "daily_time_limit_minutes": 60,
                "weekly_time_limit_minutes": None
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["student_id"] == student_id
        assert data["daily_time_limit_minutes"] == 60
        assert data["weekly_time_limit_minutes"] is None

    def test_set_weekly_time_limit(self):
        """
        测试：设置每周时间限制

        Given: 父母想要限制孩子每周使用时间
        When: 设置每周 300 分钟限制
        Then: 保存成功并可读取
        """
        student_id = "student_002"

        response = client.put(
            f"/api/v1/parental/settings/{student_id}/usage-limits",
            json={
                "daily_time_limit_minutes": None,
                "weekly_time_limit_minutes": 300
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["weekly_time_limit_minutes"] == 300

    def test_get_usage_limits(self):
        """
        测试：获取使用限制设置

        Given: 已设置使用限制
        When: 请求获取设置
        Then: 返回正确的限制值
        """
        student_id = "student_003"

        # 先设置
        client.put(
            f"/api/v1/parental/settings/{student_id}/usage-limits",
            json={"daily_time_limit_minutes": 45}
        )

        # 再获取
        response = client.get(f"/api/v1/parental/settings/{student_id}/usage-limits")

        assert response.status_code == 200
        data = response.json()

        assert data["daily_time_limit_minutes"] == 45


class TestLearningGoals:
    """测试学习目标配置"""

    def test_set_learning_goals(self):
        """
        测试：设置学习目标

        Given: 父母想要为孩子设定学习目标
        When: 设置每日 10 题目标，80% 准确率目标
        Then: 保存成功并可读取
        """
        student_id = "student_004"

        response = client.put(
            f"/api/v1/parental/settings/{student_id}/learning-goals",
            json={
                "daily_problem_count_goal": 10,
                "accuracy_rate_goal": 0.8
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["daily_problem_count_goal"] == 10
        assert data["accuracy_rate_goal"] == 0.8

    def test_get_learning_goals(self):
        """
        测试：获取学习目标

        Given: 已设置学习目标
        When: 请求获取目标
        Then: 返回正确的目标值
        """
        student_id = "student_005"

        # 先设置
        client.put(
            f"/api/v1/parental/settings/{student_id}/learning-goals",
            json={
                "daily_problem_count_goal": 15,
                "accuracy_rate_goal": 0.85
            }
        )

        # 再获取
        response = client.get(f"/api/v1/parental/settings/{student_id}/learning-goals")

        assert response.status_code == 200
        data = response.json()

        assert data["daily_problem_count_goal"] == 15
        assert data["accuracy_rate_goal"] == 0.85


class TestTutorBehaviorPreferences:
    """测试家教行为偏好配置"""

    def test_set_scaffolding_level(self):
        """
        测试：设置脚手架层级

        Given: 父母想要调整家教的引导程度
        When: 设置脚手架层级为 medium
        Then: 保存成功并可读取
        """
        student_id = "student_006"

        response = client.put(
            f"/api/v1/parental/settings/{student_id}/tutor-preferences",
            json={"scaffolding_level": "medium"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["scaffolding_level"] == "medium"

    def test_set_teaching_style(self):
        """
        测试：设置教学风格

        Given: 父母想要选择教学风格
        When: 设置为 socratic（苏格拉底式）
        Then: 保存成功并可读取
        """
        student_id = "student_007"

        response = client.put(
            f"/api/v1/parental/settings/{student_id}/tutor-preferences",
            json={
                "scaffolding_level": "low",
                "teaching_style": "socratic"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["teaching_style"] == "socratic"
        assert data["scaffolding_level"] == "low"

    def test_get_tutor_preferences(self):
        """
        测试：获取家教偏好设置

        Given: 已设置家教偏好
        When: 请求获取偏好
        Then: 返回正确的偏好值
        """
        student_id = "student_008"

        # 先设置
        client.put(
            f"/api/v1/parental/settings/{student_id}/tutor-preferences",
            json={
                "scaffolding_level": "high",
                "teaching_style": "interactive"
            }
        )

        # 再获取
        response = client.get(f"/api/v1/parental/settings/{student_id}/tutor-preferences")

        assert response.status_code == 200
        data = response.json()

        assert data["scaffolding_level"] == "high"
        assert data["teaching_style"] == "interactive"


class TestComprehensiveSettings:
    """测试综合设置管理"""

    def test_get_all_settings(self):
        """
        测试：获取所有设置

        Given: 已设置各项配置
        When: 请求获取所有设置
        Then: 返回完整的配置信息
        """
        student_id = "student_009"

        # 设置各项配置
        client.put(
            f"/api/v1/parental/settings/{student_id}/usage-limits",
            json={"daily_time_limit_minutes": 60}
        )
        client.put(
            f"/api/v1/parental/settings/{student_id}/learning-goals",
            json={"daily_problem_count_goal": 10, "accuracy_rate_goal": 0.8}
        )
        client.put(
            f"/api/v1/parental/settings/{student_id}/tutor-preferences",
            json={"scaffolding_level": "medium", "teaching_style": "socratic"}
        )

        # 获取所有设置
        response = client.get(f"/api/v1/parental/settings/{student_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["student_id"] == student_id
        assert "usage_limits" in data
        assert "learning_goals" in data
        assert "tutor_preferences" in data
        assert data["usage_limits"]["daily_time_limit_minutes"] == 60
        assert data["learning_goals"]["daily_problem_count_goal"] == 10
        assert data["tutor_preferences"]["scaffolding_level"] == "medium"

    def test_default_settings_when_none_set(self):
        """
        测试：未设置时返回默认值

        Given: 学生没有任何设置
        When: 请求获取设置
        Then: 返回合理的默认值
        """
        student_id = "student_010"

        response = client.get(f"/api/v1/parental/settings/{student_id}")

        assert response.status_code == 200
        data = response.json()

        # 应该有默认设置
        assert "usage_limits" in data
        assert "learning_goals" in data
        assert "tutor_preferences" in data

        # 默认脚手架层级应该是 medium
        assert data["tutor_preferences"]["scaffolding_level"] == "medium"
