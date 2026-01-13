"""
测试父母报告 API (LWP-4)

测试覆盖：
- 学习报告摘要 API
- 详细进度数据 API
- 会话记录 API
- 数据聚合和统计
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.services.learning_tracker import LearningTracker
from app.models.learning import AnswerResult, ProblemType


client = TestClient(app)


@pytest.fixture
def tracker():
    """创建学习追踪器实例"""
    return LearningTracker()


class TestReportSummaryAPI:
    """测试学习报告摘要 API"""

    def test_get_weekly_report_summary(self, tracker):
        """
        测试：获取本周学习报告摘要

        Given: 学生本周有多次学习记录
        When: 请求周报告摘要
        Then: 返回总学习时间、会话数、主题列表、准确率
        """
        student_id = "student_001"

        # 创建本周的学习记录
        today = datetime.now()
        for i in range(5):
            tracker.create_record(
                session_id=f"session_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text="5 + 3 = ?",
                student_answer="8",
                answer_result=AnswerResult.CORRECT if i < 4 else AnswerResult.INCORRECT,
                attempts=1,
                hints_used=0,
                response_duration=300.0  # 5 分钟
            )

        response = client.get(f"/api/v1/reports/{student_id}?period=week")

        assert response.status_code == 200
        data = response.json()

        assert data["student_id"] == student_id
        assert data["period"] == "week"
        assert data["total_sessions"] == 5
        assert data["total_time_minutes"] >= 25  # 5 次 × 5 分钟
        assert "accuracy_rate" in data
        assert "topics_practiced" in data
        assert len(data["topics_practiced"]) > 0

    def test_get_daily_report_summary(self, tracker):
        """
        测试：获取今日学习报告摘要

        Given: 学生今天有学习记录
        When: 请求日报告摘要
        Then: 返回今日统计
        """
        student_id = "student_002"

        tracker.create_record(
            session_id="session_today",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.SUBTRACTION,
            problem_text="10 - 4 = ?",
            student_answer="6",
            answer_result=AnswerResult.CORRECT,
            response_duration=600.0  # 10 分钟
        )

        response = client.get(f"/api/v1/reports/{student_id}?period=day")

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "day"
        assert data["total_sessions"] == 1
        assert data["total_time_minutes"] == 10


class TestProgressDetailAPI:
    """测试详细进度数据 API"""

    def test_get_progress_by_subject(self, tracker):
        """
        测试：按科目获取进度

        Given: 学生有数学和语文的学习记录
        When: 请求按科目分组的进度
        Then: 返回每个科目的准确率和主题
        """
        student_id = "student_003"

        # 数学记录
        tracker.create_record(
            session_id="session_math",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT,
            response_duration=300.0
        )

        # 语文记录
        tracker.create_record(
            session_id="session_chinese",
            student_id=student_id,
            student_age=6,
            subject="语文",
            problem_type=ProblemType.WORD_PROBLEM,
            problem_text="阅读理解",
            student_answer="答案",
            answer_result=AnswerResult.CORRECT,
            response_duration=400.0
        )

        response = client.get(f"/api/v1/progress/{student_id}")

        assert response.status_code == 200
        data = response.json()

        assert "subjects" in data
        assert len(data["subjects"]) == 2
        assert any(s["subject"] == "数学" for s in data["subjects"])
        assert any(s["subject"] == "语文" for s in data["subjects"])

    def test_get_accuracy_trend(self, tracker):
        """
        测试：获取准确率趋势

        Given: 学生有连续多天的学习记录
        When: 请求准确率趋势
        Then: 返回时间序列数据
        """
        student_id = "student_004"

        # 创建 7 天的学习记录
        for day in range(7):
            for i in range(5):
                is_correct = i < (3 + day // 2)  # 逐步改善
                tracker.create_record(
                    session_id=f"session_{day}_{i}",
                    student_id=student_id,
                    student_age=6,
                    subject="数学",
                    problem_type=ProblemType.ADDITION,
                    problem_text=f"题目 {day}_{i}",
                    student_answer="答案",
                    answer_result=AnswerResult.CORRECT if is_correct else AnswerResult.INCORRECT,
                    response_duration=300.0,
                    timestamp=datetime.now() - timedelta(days=6-day)
                )

        response = client.get(f"/api/v1/progress/{student_id}/trend?metric=accuracy")

        assert response.status_code == 200
        data = response.json()

        assert "trend" in data
        assert len(data["trend"]) == 7
        assert all("date" in point and "value" in point for point in data["trend"])


class TestSessionsAPI:
    """测试会话记录 API"""

    def test_get_all_sessions(self, tracker):
        """
        测试：获取所有会话记录

        Given: 学生有多次学习会话
        When: 请求会话列表
        Then: 返回会话摘要列表
        """
        student_id = "student_005"

        # 创建 3 个会话
        for i in range(3):
            tracker.create_record(
                session_id=f"session_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"题目 {i}",
                student_answer=f"答案 {i}",
                answer_result=AnswerResult.CORRECT,
                response_duration=300.0
            )

        response = client.get(f"/api/v1/sessions/{student_id}")

        assert response.status_code == 200
        data = response.json()

        assert "sessions" in data
        assert len(data["sessions"]) == 3
        assert all("session_id" in s and "timestamp" in s for s in data["sessions"])

    def test_get_session_detail(self, tracker):
        """
        测试：获取单个会话详情

        Given: 学生有特定会话
        When: 请求会话详情
        Then: 返回会话的完整信息（不含敏感对话内容）
        """
        student_id = "student_006"
        session_id = "session_detail"

        tracker.create_record(
            session_id=session_id,
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT,
            hints_used=1,
            response_duration=450.0
        )

        response = client.get(f"/api/v1/sessions/{student_id}/{session_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == session_id
        assert "subject" in data
        assert "accuracy" in data
        assert "time_spent_minutes" in data
        # 不应包含完整对话内容（隐私保护）
        assert "conversation" not in data or "summary" in data


class TestDataAggregation:
    """测试数据聚合和统计"""

    def test_calculate_total_time_spent(self, tracker):
        """
        测试：计算总学习时间

        Given: 学生有多次学习记录
        When: 聚合时间数据
        Then: 返回准确的总时间（分钟）
        """
        student_id = "student_007"

        # 创建不同时长的会话
        durations = [300, 450, 600]  # 5, 7.5, 10 分钟
        for i, duration in enumerate(durations):
            tracker.create_record(
                session_id=f"session_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text="题目",
                student_answer="答案",
                answer_result=AnswerResult.CORRECT,
                response_duration=float(duration)
            )

        response = client.get(f"/api/v1/reports/{student_id}/stats?metric=time")

        assert response.status_code == 200
        data = response.json()

        expected_total = sum(durations) / 60  # 转换为分钟
        assert data["total_time_minutes"] == expected_total

    def test_identify_struggling_topics(self, tracker):
        """
        测试：识别困难主题

        Given: 学生在特定主题上准确率低
        When: 分析学习数据
        Then: 标记困难主题
        """
        student_id = "student_008"

        # 在几何题上表现差
        for i in range(5):
            tracker.create_record(
                session_id=f"session_geo_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.GEOMETRY,
                problem_text=f"几何题 {i}",
                student_answer="错误答案",
                answer_result=AnswerResult.INCORRECT,
                hints_used=2,
                response_duration=600.0
            )

        # 在算术题上表现好
        for i in range(5):
            tracker.create_record(
                session_id=f"session_arith_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"算术题 {i}",
                student_answer="正确答案",
                answer_result=AnswerResult.CORRECT,
                hints_used=0,
                response_duration=300.0
            )

        response = client.get(f"/api/v1/reports/{student_id}/struggling-topics")

        assert response.status_code == 200
        data = response.json()

        assert "struggling_topics" in data
        # 几何应该被标记为困难主题
        assert any(t["problem_type"] == "GEOMETRY" for t in data["struggling_topics"])
