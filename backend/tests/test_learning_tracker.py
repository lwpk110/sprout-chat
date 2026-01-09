"""
学习追踪服务测试 - TDD Red Phase

测试小芽家教的家长监控功能：
- 学习记录保存
- 进度统计更新
- 学习报告生成
"""

import pytest
from datetime import datetime, timedelta
from app.services.learning_tracker import LearningTracker
from app.models.learning import (
    LearningRecord,
    StudentProgress,
    LearningReport,
    AnswerResult,
    ProblemType
)


@pytest.fixture
def tracker():
    """创建学习追踪器实例"""
    tracker = LearningTracker()
    # 清理测试数据
    tracker.clear_all_records()
    yield tracker
    # 清理
    tracker.clear_all_records()


class TestLearningRecordCreation:
    """测试：学习记录创建"""

    def test_create_basic_record(self, tracker):
        """
        测试：创建基本学习记录

        验证能够正确保存一次问答记录
        """
        record = tracker.create_record(
            session_id="test_session_001",
            student_id="student_001",
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT
        )

        assert record is not None
        assert record.session_id == "test_session_001"
        assert record.student_id == "student_001"
        assert record.problem_type == ProblemType.ADDITION
        assert record.answer_result == AnswerResult.CORRECT

    def test_create_record_with_image(self, tracker):
        """
        测试：创建包含图像的学习记录

        验证能够保存图像识别的问答记录
        """
        record = tracker.create_record(
            session_id="test_session_002",
            student_id="student_001",
            student_age=6,
            subject="数学",
            problem_type=ProblemType.WORD_PROBLEM,
            problem_text="小明有5个苹果",
            problem_image_url="https://example.com/image.jpg",
            student_answer="5",
            answer_result=AnswerResult.CORRECT
        )

        assert record.problem_image_url == "https://example.com/image.jpg"

    def test_create_record_with_timing(self, tracker):
        """
        测试：创建包含时间信息的记录

        验证能够记录答题时长
        """
        record = tracker.create_record(
            session_id="test_session_003",
            student_id="student_001",
            student_age=6,
            subject="数学",
            problem_type=ProblemType.SUBTRACTION,
            problem_text="10 - 5 = ?",
            student_answer="5",
            answer_result=AnswerResult.CORRECT,
            response_duration=12.5
        )

        assert record.response_duration == 12.5

    def test_create_record_with_teaching_info(self, tracker):
        """
        测试：创建包含教学信息的记录

        验证能够记录使用的教学策略和比喻
        """
        record = tracker.create_record(
            session_id="test_session_004",
            student_id="student_001",
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT,
            strategy_used="堆积木",
            metaphor_used="积木"
        )

        assert record.strategy_used == "堆积木"
        assert record.metaphor_used == "积木"


class TestProgressTracking:
    """测试：进度追踪"""

    def test_update_student_progress(self, tracker):
        """
        测试：更新学生进度

        验证正确答题后进度统计更新
        """
        # 记录一次正确答题
        tracker.create_record(
            session_id="test_progress_001",
            student_id="student_progress",
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT
        )

        # 获取进度
        progress = tracker.get_student_progress(
            student_id="student_progress",
            subject="数学"
        )

        assert progress.total_questions == 1
        assert progress.total_correct == 1
        assert progress.accuracy_rate == 1.0

    def test_multiple_records_aggregation(self, tracker):
        """
        测试：多条记录聚合

        验证能够正确统计多次答题
        """
        # 记录3次答题（2对1错）
        tracker.create_record(
            session_id="test_agg_001",
            student_id="student_agg",
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT
        )

        tracker.create_record(
            session_id="test_agg_002",
            student_id="student_agg",
            student_age=6,
            subject="数学",
            problem_type=ProblemType.SUBTRACTION,
            problem_text="10 - 5 = ?",
            student_answer="5",
            answer_result=AnswerResult.CORRECT
        )

        tracker.create_record(
            session_id="test_agg_003",
            student_id="student_agg",
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="7 + 2 = ?",
            student_answer="10",
            answer_result=AnswerResult.INCORRECT
        )

        # 获取进度
        progress = tracker.get_student_progress(
            student_id="student_agg",
            subject="数学"
        )

        assert progress.total_questions == 3
        assert progress.total_correct == 2
        assert progress.total_incorrect == 1
        assert progress.accuracy_rate == 2/3

    def test_streak_tracking(self, tracker):
        """
        测试：连续答对追踪

        验证能够追踪连续答对次数
        """
        student_id = "student_streak"

        # 连续答对3次
        for i in range(3):
            tracker.create_record(
                session_id=f"streak_00{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"{i} + 1 = ?",
                student_answer=str(i + 1),
                answer_result=AnswerResult.CORRECT
            )

        progress = tracker.get_student_progress(student_id, "数学")

        assert progress.current_streak == 3
        assert progress.longest_streak == 3

    def test_problem_type_breakdown(self, tracker):
        """
        测试：按题型分类统计

        验证能够分别统计不同题型的表现
        """
        student_id = "student_breakdown"

        # 加法题（2对）
        tracker.create_record(
            session_id="breakdown_001",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT
        )

        tracker.create_record(
            session_id="breakdown_002",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="4 + 2 = ?",
            student_answer="6",
            answer_result=AnswerResult.CORRECT
        )

        # 减法题（1对1错）
        tracker.create_record(
            session_id="breakdown_003",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.SUBTRACTION,
            problem_text="10 - 3 = ?",
            student_answer="7",
            answer_result=AnswerResult.CORRECT
        )

        tracker.create_record(
            session_id="breakdown_004",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.SUBTRACTION,
            problem_text="8 - 2 = ?",
            student_answer="5",
            answer_result=AnswerResult.INCORRECT
        )

        progress = tracker.get_student_progress(student_id, "数学")

        # 验证按题型统计
        assert "加法" in progress.by_problem_type
        assert "减法" in progress.by_problem_type
        assert progress.by_problem_type["加法"]["correct"] == 2
        assert progress.by_problem_type["减法"]["correct"] == 1
        assert progress.by_problem_type["减法"]["incorrect"] == 1

    def test_learning_time_tracking(self, tracker):
        """
        测试：学习时长追踪

        验证能够累计学习时长
        """
        student_id = "student_time"

        # 模拟3次答题，每次约10秒
        for i in range(3):
            tracker.create_record(
                session_id=f"time_00{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"{i} + 1 = ?",
                student_answer=str(i + 1),
                answer_result=AnswerResult.CORRECT,
                response_duration=10.0
            )

        progress = tracker.get_student_progress(student_id, "数学")

        assert progress.total_learning_time == 30.0
        assert progress.average_response_time == 10.0


class TestReportGeneration:
    """测试：报告生成"""

    def test_generate_daily_report(self, tracker):
        """
        测试：生成日报

        验证能够生成最近一天的学习报告
        """
        student_id = "student_daily"

        # 创建今天的记录
        tracker.create_record(
            session_id="daily_001",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT
        )

        report = tracker.generate_report(
            student_id=student_id,
            subject="数学",
            days=1
        )

        assert report is not None
        assert report.student_id == student_id
        assert report.total_questions >= 1

    def test_generate_weekly_report(self, tracker):
        """
        测试：生成周报

        验证能够生成最近7天的学习报告
        """
        student_id = "student_weekly"

        # 创建最近7天的记录
        for i in range(7):
            tracker.create_record(
                session_id=f"weekly_00{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"{i} + 1 = ?",
                student_answer=str(i + 1),
                answer_result=AnswerResult.CORRECT
            )

        report = tracker.generate_report(
            student_id=student_id,
            subject="数学",
            days=7
        )

        assert report.total_questions == 7
        assert report.overall_accuracy > 0

    def test_report_includes_trends(self, tracker):
        """
        测试：报告包含学习趋势

        验证报告包含学习趋势分析
        """
        student_id = "student_trends"

        # 创建多天记录
        for day in range(5):
            for i in range(3):
                tracker.create_record(
                    session_id=f"trends_{day}_{i}",
                    student_id=student_id,
                    student_age=6,
                    subject="数学",
                    problem_type=ProblemType.ADDITION,
                    problem_text=f"{i} + {day} = ?",
                    student_answer=str(i + day),
                    answer_result=AnswerResult.CORRECT
                )

        report = tracker.generate_report(
            student_id=student_id,
            subject="数学",
            days=7
        )

        # 验证趋势数据
        assert len(report.learning_trend) > 0

    def test_report_identifies_strengths_weaknesses(self, tracker):
        """
        测试：报告识别强项和弱项

        验证报告能够分析学生的强项和弱项
        """
        student_id = "student_sw"

        # 加法表现好（3对）
        for i in range(3):
            tracker.create_record(
                session_id=f"sw_add_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"{i} + 1 = ?",
                student_answer=str(i + 1),
                answer_result=AnswerResult.CORRECT
            )

        # 减法表现差（1对2错）
        tracker.create_record(
            session_id="sw_sub_0",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.SUBTRACTION,
            problem_text="10 - 5 = ?",
            student_answer="5",
            answer_result=AnswerResult.CORRECT
        )

        for i in range(2):
            tracker.create_record(
                session_id=f"sw_sub_{i+1}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.SUBTRACTION,
                problem_text=f"{10-i} - {i} = ?",
                student_answer=str(10),
                answer_result=AnswerResult.INCORRECT
            )

        report = tracker.generate_report(
            student_id=student_id,
            subject="数学",
            days=7
        )

        # 验证强项弱项识别
        assert len(report.strong_areas) > 0
        assert len(report.weak_areas) > 0

    def test_report_generates_recommendations(self, tracker):
        """
        测试：报告生成建议

        验证报告能够提供学习建议
        """
        student_id = "student_rec"

        # 创建一些记录
        for i in range(5):
            tracker.create_record(
                session_id=f"rec_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"{i} + 1 = ?",
                student_answer=str(i + 1),
                answer_result=AnswerResult.CORRECT
            )

        report = tracker.generate_report(
            student_id=student_id,
            subject="数学",
            days=7
        )

        # 验证建议生成
        assert len(report.recommendations) > 0


class TestProgressQuery:
    """测试：进度查询"""

    def test_get_progress_summary(self, tracker):
        """
        测试：获取进度摘要

        验证能够获取简洁的进度摘要
        """
        student_id = "student_summary"

        # 创建记录
        for i in range(5):
            tracker.create_record(
                session_id=f"summary_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"{i} + 1 = ?",
                student_answer=str(i + 1),
                answer_result=AnswerResult.CORRECT
            )

        summary = tracker.get_progress_summary(
            student_id=student_id,
            subject="数学"
        )

        assert summary.total_questions == 5
        assert summary.correct_count == 5
        assert summary.accuracy_rate == 1.0
        assert summary.learning_time_minutes >= 0

    def test_get_recent_records(self, tracker):
        """
        测试：获取最近记录

        验证能够获取最近的答题记录
        """
        student_id = "student_recent"

        # 创建多条记录
        for i in range(10):
            tracker.create_record(
                session_id=f"recent_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"{i} + 1 = ?",
                student_answer=str(i + 1),
                answer_result=AnswerResult.CORRECT
            )

        # 获取最近5条
        records = tracker.get_recent_records(
            student_id=student_id,
            subject="数学",
            limit=5
        )

        assert len(records) == 5

    def test_get_records_by_date_range(self, tracker):
        """
        测试：按日期范围获取记录

        验证能够获取指定日期范围内的记录
        """
        student_id = "student_daterange"

        # 创建记录
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        # 今天的记录
        tracker.create_record(
            session_id="daterange_today",
            student_id=student_id,
            student_age=6,
            subject="数学",
            problem_type=ProblemType.ADDITION,
            problem_text="5 + 3 = ?",
            student_answer="8",
            answer_result=AnswerResult.CORRECT
        )

        # 获取今天的记录
        records = tracker.get_records_by_date_range(
            student_id=student_id,
            subject="数学",
            start_date=today.replace(hour=0, minute=0, second=0),
            end_date=today.replace(hour=23, minute=59, second=59)
        )

        assert len(records) >= 1


class TestMasteryCalculation:
    """测试：掌握度计算"""

    def test_calculate_mastery_by_type(self, tracker):
        """
        测试：按题型计算掌握度

        验证能够计算各知识点的掌握程度
        """
        student_id = "student_mastery"

        # 加法：5对0错 → 100% 掌握
        for i in range(5):
            tracker.create_record(
                session_id=f"mastery_add_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.ADDITION,
                problem_text=f"{i} + 1 = ?",
                student_answer=str(i + 1),
                answer_result=AnswerResult.CORRECT
            )

        # 减法：3对2错 → 60% 掌握
        for i in range(3):
            tracker.create_record(
                session_id=f"mastery_sub_correct_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.SUBTRACTION,
                problem_text=f"{10-i} - {i} = ?",
                student_answer=str(10 - 2*i),
                answer_result=AnswerResult.CORRECT
            )

        for i in range(2):
            tracker.create_record(
                session_id=f"mastery_sub_wrong_{i}",
                student_id=student_id,
                student_age=6,
                subject="数学",
                problem_type=ProblemType.SUBTRACTION,
                problem_text=f"{8-i} - {i} = ?",
                student_answer="5",
                answer_result=AnswerResult.INCORRECT
            )

        progress = tracker.get_student_progress(student_id, "数学")

        # 验证掌握度计算
        assert "加法" in progress.mastery_level
        assert "减法" in progress.mastery_level
        assert progress.mastery_level["加法"] == 1.0
        assert progress.mastery_level["减法"] == 0.6


# Red Phase 标记
# pytestmark = pytest.mark.red_phase
