"""
测试多科目支持与个性化推荐 API (LWP-6)

测试覆盖：
- 多科目学习记录追踪
- 跨科目学习进度统计
- 基于学习模式的主题推荐
- 个性化学习路径生成
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_data():
    """
    自动清理存储，确保测试隔离
    """
    from app.api.multi_subject import _learning_records, _recommendation_cache
    # 测试前清理
    _learning_records.clear()
    _recommendation_cache.clear()
    yield
    # 测试后清理
    _learning_records.clear()
    _recommendation_cache.clear()


class TestMultiSubjectTracking:
    """测试多科目学习记录追踪"""

    def test_record_math_learning(self):
        """
        测试：记录数学学习

        Given: 学生完成数学题目
        When: 记录学习数据
        Then: 成功保存并按科目分类
        """
        student_id = "student_001"

        response = client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "数学",
                "topic": "加法运算",
                "problem_type": "addition",
                "difficulty": 1,
                "is_correct": True,
                "time_spent_seconds": 30,
                "hints_used": 0
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["subject"] == "数学"
        assert data["topic"] == "加法运算"
        assert data["student_id"] == student_id

    def test_record_reading_learning(self):
        """
        测试：记录阅读学习

        Given: 学生完成阅读练习
        When: 记录学习数据
        Then: 成功保存并区分科目
        """
        student_id = "student_002"

        response = client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "阅读",
                "topic": "拼音识别",
                "problem_type": "pinyin",
                "difficulty": 1,
                "is_correct": True,
                "time_spent_seconds": 45,
                "hints_used": 1
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["subject"] == "阅读"
        assert data["topic"] == "拼音识别"

    def test_get_cross_subject_progress(self):
        """
        测试：获取跨科目学习进度

        Given: 学生在多个科目有学习记录
        When: 请求进度统计
        Then: 返回各科目的准确率、时间、练习次数
        """
        student_id = "student_003"

        # 记录数学学习
        client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "数学",
                "topic": "加法",
                "problem_type": "addition",
                "difficulty": 1,
                "is_correct": True,
                "time_spent_seconds": 30,
                "hints_used": 0
            }
        )

        # 记录阅读学习
        client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "阅读",
                "topic": "拼音",
                "problem_type": "pinyin",
                "difficulty": 1,
                "is_correct": False,
                "time_spent_seconds": 60,
                "hints_used": 2
            }
        )

        # 获取跨科目进度
        response = client.get(f"/api/v1/multi-subject/{student_id}/progress")

        assert response.status_code == 200
        data = response.json()

        assert "subjects" in data
        assert len(data["subjects"]) == 2

        # 验证数学科目数据
        math_progress = next(s for s in data["subjects"] if s["subject"] == "数学")
        assert math_progress["total_records"] == 1
        assert math_progress["accuracy_rate"] == 1.0

        # 验证阅读科目数据
        reading_progress = next(s for s in data["subjects"] if s["subject"] == "阅读")
        assert reading_progress["accuracy_rate"] == 0.0


class TestTopicRecommendations:
    """测试主题推荐"""

    def test_recommend_based_on_weak_areas(self):
        """
        测试：基于薄弱环节推荐主题

        Given: 学生在某主题准确率低
        When: 请求推荐
        Then: 优先推荐该主题的练习
        """
        student_id = "student_004"

        # 记录多次加法错误
        for i in range(5):
            client.post(
                f"/api/v1/multi-subject/{student_id}/record",
                json={
                    "subject": "数学",
                    "topic": "减法运算",
                    "problem_type": "subtraction",
                    "difficulty": 1,
                    "is_correct": False,
                    "time_spent_seconds": 60,
                    "hints_used": 2
                }
            )

        # 记录一次乘法正确
        client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "数学",
                "topic": "乘法入门",
                "problem_type": "multiplication",
                "difficulty": 1,
                "is_correct": True,
                "time_spent_seconds": 30,
                "hints_used": 0
            }
        )

        # 获取推荐
        response = client.get(f"/api/v1/multi-subject/{student_id}/recommendations")

        assert response.status_code == 200
        data = response.json()

        assert "recommendations" in data
        # 减法应该被优先推荐（因为准确率低）
        subtraction_rec = next(
            (r for r in data["recommendations"] if r["topic"] == "减法运算"),
            None
        )
        assert subtraction_rec is not None
        assert subtraction_rec["priority"] == "high"
        assert "weak_area" in subtraction_rec["reason"]

    def test_recommend_based_on_learning_velocity(self):
        """
        测试：基于学习速度推荐

        Given: 学生快速掌握某主题
        When: 请求推荐
        Then: 推荐更高难度的主题
        """
        student_id = "student_005"

        # 记录快速正确的加法练习
        for i in range(3):
            client.post(
                f"/api/v1/multi-subject/{student_id}/record",
                json={
                    "subject": "数学",
                    "topic": "加法运算",
                    "problem_type": "addition",
                    "difficulty": 1,
                    "is_correct": True,
                    "time_spent_seconds": 15,  # 快速
                    "hints_used": 0
                }
            )

        # 获取推荐
        response = client.get(f"/api/v1/multi-subject/{student_id}/recommendations")

        assert response.status_code == 200
        data = response.json()

        # 应该推荐更高难度的主题
        assert any(r["difficulty"] > 1 for r in data["recommendations"])

    def test_recommend_cross_subject(self):
        """
        测试：跨科目推荐

        Given: 学生在数学和阅读都有学习记录
        When: 请求推荐
        Then: 平衡推荐各科目的主题
        """
        student_id = "student_006"

        # 记录数学学习
        for i in range(3):
            client.post(
                f"/api/v1/multi-subject/{student_id}/record",
                json={
                    "subject": "数学",
                    "topic": "加法",
                    "problem_type": "addition",
                    "difficulty": 1,
                    "is_correct": True,
                    "time_spent_seconds": 30,
                    "hints_used": 0
                }
            )

        # 记录阅读学习
        client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "阅读",
                "topic": "拼音",
                "problem_type": "pinyin",
                "difficulty": 1,
                "is_correct": True,
                "time_spent_seconds": 40,
                "hints_used": 0
            }
        )

        # 获取推荐
        response = client.get(f"/api/v1/multi-subject/{student_id}/recommendations")

        assert response.status_code == 200
        data = response.json()

        # 应该包含数学和阅读的推荐
        subjects_in_recs = set(r["subject"] for r in data["recommendations"])
        assert "数学" in subjects_in_recs
        assert "阅读" in subjects_in_recs


class TestPersonalizedLearningPath:
    """测试个性化学习路径"""

    def test_generate_learning_path(self):
        """
        测试：生成学习路径

        Given: 学生有学习历史
        When: 请求学习路径
        Then: 返回按优先级排序的主题序列
        """
        student_id = "student_007"

        # 记录混合学习数据
        client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "数学",
                "topic": "减法运算",
                "problem_type": "subtraction",
                "difficulty": 1,
                "is_correct": False,
                "time_spent_seconds": 60,
                "hints_used": 2
            }
        )

        client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "数学",
                "topic": "加法运算",
                "problem_type": "addition",
                "difficulty": 1,
                "is_correct": True,
                "time_spent_seconds": 20,
                "hints_used": 0
            }
        )

        # 生成学习路径
        response = client.get(f"/api/v1/multi-subject/{student_id}/learning-path")

        assert response.status_code == 200
        data = response.json()

        assert "path" in data
        assert len(data["path"]) > 0

        # 第一个应该是减法（薄弱环节）
        first_topic = data["path"][0]
        assert first_topic["topic"] == "减法运算"
        assert first_topic["priority_order"] == 1

    def test_learning_path_with_mastery(self):
        """
        测试：学习路径考虑掌握程度

        Given: 学生已掌握某主题
        When: 生成学习路径
        Then: 已掌握主题优先级降低
        """
        student_id = "student_008"

        # 记录已掌握的主题（多次正确）
        for i in range(5):
            client.post(
                f"/api/v1/multi-subject/{student_id}/record",
                json={
                    "subject": "数学",
                    "topic": "加法运算",
                    "problem_type": "addition",
                    "difficulty": 1,
                    "is_correct": True,
                    "time_spent_seconds": 20,
                    "hints_used": 0
                }
            )

        # 记录未掌握的主题
        client.post(
            f"/api/v1/multi-subject/{student_id}/record",
            json={
                "subject": "数学",
                "topic": "乘法入门",
                "problem_type": "multiplication",
                "difficulty": 1,
                "is_correct": False,
                "time_spent_seconds": 90,
                "hints_used": 3
            }
        )

        # 生成学习路径
        response = client.get(f"/api/v1/multi-subject/{student_id}/learning-path")

        assert response.status_code == 200
        data = response.json()

        # 乘法应该在路径前面（未掌握）
        multiplication_idx = next(
            i for i, t in enumerate(data["path"]) if t["topic"] == "乘法入门"
        )
        addition_idx = next(
            i for i, t in enumerate(data["path"]) if t["topic"] == "加法运算"
        )
        assert multiplication_idx < addition_idx


class TestDefaultRecommendations:
    """测试默认推荐行为"""

    def test_recommendations_for_new_student(self):
        """
        测试：新学生的推荐

        Given: 学生没有任何学习记录
        When: 请求推荐
        Then: 返回基础主题推荐
        """
        student_id = "student_new"

        response = client.get(f"/api/v1/multi-subject/{student_id}/recommendations")

        assert response.status_code == 200
        data = response.json()

        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
        # 应该推荐基础主题
        assert all(r["difficulty"] == 1 for r in data["recommendations"])
