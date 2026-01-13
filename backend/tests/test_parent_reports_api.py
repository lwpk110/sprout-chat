"""
测试父母报告 API (LWP-4) - 简化版本

测试核心报告功能
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.learning_tracker import LearningTracker
from app.models.learning import AnswerResult, ProblemType
from app.api.parent_reports import _records_storage


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    """
    自动清理存储，确保测试隔离

    autouse=True 使得每个测试自动使用此 fixture
    """
    # 测试前清理
    _records_storage.clear()
    yield
    # 测试后清理
    _records_storage.clear()


@pytest.fixture
def tracker():
    """创建学习追踪器实例"""
    return LearningTracker()


def _sync_tracker_to_storage(tracker, student_id):
    """
    辅助函数：将 tracker 的记录同步到 API 的内存存储

    注意：这是测试专用的桥接函数，实际应用应使用数据库
    """
    # 获取该学生的所有记录（tracker.records 是 Dict[str, LearningRecord]，键是 record_id）
    student_records = [
        record for record_id, record in tracker.records.items()
        if record.student_id == student_id
    ]

    # 转换为字典格式并存入 API 存储
    for record in student_records:
        record_dict = {
            "session_id": record.session_id,
            "student_id": record.student_id,
            "student_age": record.student_age,
            "subject": record.subject,
            "problem_type": record.problem_type,
            "problem_text": record.problem_text,
            "student_answer": record.student_answer,
            "answer_result": record.answer_result,
            "attempts": record.attempts,
            "hints_used": record.hints_used,
            "response_duration": record.response_duration,
            "strategy_used": record.strategy_used,
            "metaphor_used": record.metaphor_used,
            "question_time": record.question_time,
            "answer_time": record.answer_time
        }
        _records_storage[student_id].append(record_dict)


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
                response_duration=300.0  # 5 分钟
            )

        # 同步 tracker 数据到 API 存储
        _sync_tracker_to_storage(tracker, student_id)

        response = client.get(f"/api/v1/reports/{student_id}?period=week")

        assert response.status_code == 200
        data = response.json()

        assert data["student_id"] == student_id
        assert data["period"] == "week"
        assert data["total_sessions"] == 5
        assert data["total_time_minutes"] >= 25  # 5 次 × 5 分钟
        assert "accuracy_rate" in data
        assert data["accuracy_rate"] == 0.8  # 4/5 正确

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

        # 同步 tracker 数据到 API 存储
        _sync_tracker_to_storage(tracker, student_id)

        response = client.get(f"/api/v1/reports/{student_id}?period=day")

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "day"
        assert data["total_sessions"] == 1
        assert data["total_time_minutes"] == 10


class TestStrugglingTopics:
    """测试困难主题识别"""

    def test_identify_struggling_topics(self, tracker):
        """
        测试：识别困难主题

        Given: 学生在特定主题上准确率低
        When: 分析学习数据
        Then: 标记困难主题
        """
        student_id = "student_003"

        # 在应用题上表现差
        for i in range(5):
            tracker.create_record(
                session_id=f"session_word_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.WORD_PROBLEM,
                problem_text=f"应用题 {i}",
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

        # 同步 tracker 数据到 API 存储
        _sync_tracker_to_storage(tracker, student_id)

        response = client.get(f"/api/v1/reports/{student_id}/struggling-topics")

        assert response.status_code == 200
        data = response.json()

        assert "struggling_topics" in data
        # 应用题应该被标记为困难主题
        assert any(t["problem_type"] == "应用题" for t in data["struggling_topics"])
        # 加法题不应被标记
        assert not any(t["problem_type"] == "加法" for t in data["struggling_topics"])
