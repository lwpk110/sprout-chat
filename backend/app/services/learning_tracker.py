"""
学习追踪服务

实现学生的学习进度追踪、记录保存和报告生成功能
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

from app.models.learning import (
    LearningRecord,
    StudentProgress,
    LearningReport,
    ProgressSummary,
    AnswerResult,
    ProblemType
)


class LearningTracker:
    """
    学习追踪器

    负责记录学生的学习过程、统计学习进度、生成学习报告
    """

    def __init__(self):
        """初始化学习追踪器"""
        # 内存存储（生产环境应使用数据库）
        self.records: Dict[str, LearningRecord] = {}
        self.progress_cache: Dict[str, StudentProgress] = {}

    def create_record(
        self,
        session_id: str,
        student_id: str,
        student_age: int,
        subject: str,
        problem_type: ProblemType,
        problem_text: str,
        student_answer: str,
        answer_result: AnswerResult,
        problem_image_url: Optional[str] = None,
        attempts: int = 1,
        hints_used: int = 0,
        response_duration: Optional[float] = None,
        strategy_used: Optional[str] = None,
        metaphor_used: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> LearningRecord:
        """
        创建学习记录

        Args:
            session_id: 会话 ID
            student_id: 学生 ID
            student_age: 学生年龄
            subject: 科目
            problem_type: 问题类型
            problem_text: 问题文本
            student_answer: 学生答案
            answer_result: 答题结果
            problem_image_url: 问题图片 URL（可选）
            attempts: 尝试次数
            hints_used: 使用提示次数
            response_duration: 响应时长（秒）
            strategy_used: 使用的教学策略
            metaphor_used: 使用的比喻
            metadata: 额外数据

        Returns:
            创建的学习记录
        """
        record_id = str(uuid.uuid4())

        record = LearningRecord(
            id=record_id,
            session_id=session_id,
            student_id=student_id,
            student_age=student_age,
            subject=subject,
            problem_type=problem_type,
            problem_text=problem_text,
            problem_image_url=problem_image_url,
            student_answer=student_answer,
            answer_result=answer_result,
            attempts=attempts,
            hints_used=hints_used,
            question_time=datetime.now(),
            answer_time=datetime.now(),
            response_duration=response_duration,
            strategy_used=strategy_used,
            metaphor_used=metaphor_used,
            metadata=metadata or {}
        )

        # 保存记录
        self.records[record_id] = record

        # 更新进度缓存
        self._update_progress_cache(record)

        return record

    def get_student_progress(
        self,
        student_id: str,
        subject: str
    ) -> StudentProgress:
        """
        获取学生进度

        Args:
            student_id: 学生 ID
            subject: 科目

        Returns:
            学生进度统计
        """
        cache_key = f"{student_id}_{subject}"

        if cache_key in self.progress_cache:
            return self.progress_cache[cache_key]

        # 如果缓存中没有，计算进度
        progress = self._calculate_progress(student_id, subject)
        self.progress_cache[cache_key] = progress

        return progress

    def generate_report(
        self,
        student_id: str,
        subject: str,
        days: int = 7
    ) -> LearningReport:
        """
        生成学习报告

        Args:
            student_id: 学生 ID
            subject: 科目
            days: 最近多少天

        Returns:
            学习报告
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 获取时间范围内的记录
        records = self._get_records_by_date_range(
            student_id, subject, start_date, end_date
        )

        # 计算统计数据
        total_sessions = len(set(r.session_id for r in records))
        total_questions = len(records)
        total_learning_time = sum(r.response_duration or 0 for r in records)

        # 计算正确率
        if total_questions > 0:
            correct_count = sum(
                1 for r in records
                if r.answer_result == AnswerResult.CORRECT
            )
            overall_accuracy = correct_count / total_questions
        else:
            overall_accuracy = 0.0

        # 按题型统计
        by_problem_type = self._analyze_by_problem_type(records)

        # 学习趋势
        learning_trend = self._calculate_learning_trend(records, days)

        # 强弱项分析
        strong_areas, weak_areas = self._identify_strengths_weaknesses(
            by_problem_type
        )

        # 生成建议
        recommendations = self._generate_recommendations(
            by_problem_type, strong_areas, weak_areas
        )

        # 日报正确率
        daily_accuracy = self._calculate_daily_accuracy(records, days)

        report = LearningReport(
            report_id=str(uuid.uuid4()),
            student_id=student_id,
            subject=subject,
            start_date=start_date,
            end_date=end_date,
            total_sessions=total_sessions,
            total_questions=total_questions,
            total_learning_time=total_learning_time,
            overall_accuracy=overall_accuracy,
            daily_accuracy=daily_accuracy,
            by_problem_type=by_problem_type,
            learning_trend=learning_trend,
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            recommendations=recommendations
        )

        return report

    def get_progress_summary(
        self,
        student_id: str,
        subject: str
    ) -> ProgressSummary:
        """
        获取进度摘要

        Args:
            student_id: 学生 ID
            subject: 科目

        Returns:
            进度摘要
        """
        progress = self.get_student_progress(student_id, subject)

        # 找出最强和最弱的题型
        mastery_items = list(progress.mastery_level.items())
        if mastery_items:
            strongest_type = max(mastery_items, key=lambda x: x[1])[0]
            weakest_type = min(mastery_items, key=lambda x: x[1])[0]
        else:
            strongest_type = None
            weakest_type = None

        summary = ProgressSummary(
            student_id=student_id,
            total_questions=progress.total_questions,
            correct_count=progress.total_correct,
            accuracy_rate=progress.accuracy_rate,
            learning_time_minutes=progress.total_learning_time / 60,
            current_streak=progress.current_streak,
            strongest_type=strongest_type,
            weakest_type=weakest_type,
            last_activity=progress.last_activity
        )

        return summary

    def get_recent_records(
        self,
        student_id: str,
        subject: str,
        limit: int = 10
    ) -> List[LearningRecord]:
        """
        获取最近的学习记录

        Args:
            student_id: 学生 ID
            subject: 科目
            limit: 返回数量限制

        Returns:
            学习记录列表（按时间倒序）
        """
        records = [
            r for r in self.records.values()
            if r.student_id == student_id and r.subject == subject
        ]

        # 按时间倒序排序
        records.sort(key=lambda x: x.question_time, reverse=True)

        return records[:limit]

    def get_records_by_date_range(
        self,
        student_id: str,
        subject: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[LearningRecord]:
        """
        按日期范围获取记录

        Args:
            student_id: 学生 ID
            subject: 科目
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            学习记录列表
        """
        return self._get_records_by_date_range(
            student_id, subject, start_date, end_date
        )

    def clear_all_records(self):
        """清空所有记录（用于测试）"""
        self.records.clear()
        self.progress_cache.clear()

    # ============ 私有方法 ============

    def _update_progress_cache(self, record: LearningRecord):
        """更新进度缓存"""
        cache_key = f"{record.student_id}_{record.subject}"

        if cache_key not in self.progress_cache:
            self.progress_cache[cache_key] = StudentProgress(
                student_id=record.student_id,
                subject=record.subject,
                student_age=record.student_age
            )

        progress = self.progress_cache[cache_key]

        # 更新总体统计
        progress.total_questions += 1
        if record.answer_result == AnswerResult.CORRECT:
            progress.total_correct += 1
            progress.current_streak += 1
            if progress.current_streak > progress.longest_streak:
                progress.longest_streak = progress.current_streak
        elif record.answer_result == AnswerResult.INCORRECT:
            progress.total_incorrect += 1
            progress.current_streak = 0
        elif record.answer_result == AnswerResult.PARTIAL:
            progress.total_partial += 1

        # 更新题型统计（处理枚举和字符串两种情况）
        if isinstance(record.problem_type, ProblemType):
            problem_type_str = record.problem_type.value
        else:
            problem_type_str = record.problem_type

        if problem_type_str not in progress.by_problem_type:
            progress.by_problem_type[problem_type_str] = {
                "total": 0,
                "correct": 0,
                "incorrect": 0,
                "partial": 0
            }

        progress.by_problem_type[problem_type_str]["total"] += 1
        if record.answer_result == AnswerResult.CORRECT:
            progress.by_problem_type[problem_type_str]["correct"] += 1
        elif record.answer_result == AnswerResult.INCORRECT:
            progress.by_problem_type[problem_type_str]["incorrect"] += 1
        elif record.answer_result == AnswerResult.PARTIAL:
            progress.by_problem_type[problem_type_str]["partial"] += 1

        # 更新学习时长
        if record.response_duration:
            progress.total_learning_time += record.response_duration
            # 更新平均响应时间
            if progress.total_questions > 0:
                progress.average_response_time = (
                    progress.total_learning_time / progress.total_questions
                )

        # 更新时间范围
        if progress.first_activity is None:
            progress.first_activity = record.question_time
        progress.last_activity = record.question_time

        # 更新掌握度
        self._update_mastery_level(progress, problem_type_str)

    def _update_mastery_level(self, progress: StudentProgress, problem_type: str):
        """更新掌握度"""
        if problem_type not in progress.by_problem_type:
            return

        type_stats = progress.by_problem_type[problem_type]
        total = type_stats["total"]
        correct = type_stats["correct"]

        if total > 0:
            mastery = correct / total
        else:
            mastery = 0.0

        progress.mastery_level[problem_type] = mastery

    def _calculate_progress(
        self,
        student_id: str,
        subject: str
    ) -> StudentProgress:
        """计算学生进度"""
        records = [
            r for r in self.records.values()
            if r.student_id == student_id and r.subject == subject
        ]

        if not records:
            return StudentProgress(
                student_id=student_id,
                subject=subject,
                student_age=0
            )

        # 使用第一条记录的年龄
        student_age = records[0].student_age

        progress = StudentProgress(
            student_id=student_id,
            subject=subject,
            student_age=student_age
        )

        # 聚合所有记录
        for record in records:
            self._update_progress_cache(record)

        return self.progress_cache[f"{student_id}_{subject}"]

    def _get_records_by_date_range(
        self,
        student_id: str,
        subject: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[LearningRecord]:
        """按日期范围获取记录"""
        return [
            r for r in self.records.values()
            if (r.student_id == student_id and
                r.subject == subject and
                start_date <= r.question_time <= end_date)
        ]

    def _analyze_by_problem_type(
        self,
        records: List[LearningRecord]
    ) -> Dict[str, Dict[str, Any]]:
        """按题型分析"""
        by_type = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
            "accuracy": 0.0
        })

        for record in records:
            # 处理枚举和字符串两种情况
            if isinstance(record.problem_type, ProblemType):
                problem_type = record.problem_type.value
            else:
                problem_type = record.problem_type

            by_type[problem_type]["total"] += 1
            if record.answer_result == AnswerResult.CORRECT:
                by_type[problem_type]["correct"] += 1
            elif record.answer_result == AnswerResult.INCORRECT:
                by_type[problem_type]["incorrect"] += 1

        # 计算正确率
        for problem_type, stats in by_type.items():
            if stats["total"] > 0:
                stats["accuracy"] = stats["correct"] / stats["total"]

        return dict(by_type)

    def _calculate_learning_trend(
        self,
        records: List[LearningRecord],
        days: int
    ) -> List[Dict[str, Any]]:
        """计算学习趋势"""
        trend = []

        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            date_start = date.replace(hour=0, minute=0, second=0)
            date_end = date.replace(hour=23, minute=59, second=59)

            day_records = [
                r for r in records
                if date_start <= r.question_time <= date_end
            ]

            if day_records:
                correct = sum(
                    1 for r in day_records
                    if r.answer_result == AnswerResult.CORRECT
                )
                accuracy = correct / len(day_records) if day_records else 0.0

                trend.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "questions": len(day_records),
                    "correct": correct,
                    "accuracy": accuracy
                })

        return list(reversed(trend))

    def _identify_strengths_weaknesses(
        self,
        by_problem_type: Dict[str, Dict[str, Any]]
    ) -> tuple:
        """识别强项和弱项"""
        # 过滤掉题目太少的题型（至少3题）
        valid_types = {
            k: v for k, v in by_problem_type.items()
            if v["total"] >= 3
        }

        if not valid_types:
            return [], []

        # 排序
        sorted_types = sorted(
            valid_types.items(),
            key=lambda x: x[1]["accuracy"],
            reverse=True
        )

        # 前25%为强项，后25%为弱项
        n = len(sorted_types)
        strong_count = max(1, n // 4)
        weak_count = max(1, n // 4)

        strong_areas = [
            {"type": t[0], "accuracy": t[1]["accuracy"]}
            for t in sorted_types[:strong_count]
        ]

        weak_areas = [
            {"type": t[0], "accuracy": t[1]["accuracy"]}
            for t in sorted_types[-weak_count:]
        ]

        return strong_areas, weak_areas

    def _generate_recommendations(
        self,
        by_problem_type: Dict[str, Dict[str, Any]],
        strong_areas: List[Dict],
        weak_areas: List[Dict]
    ) -> List[str]:
        """生成学习建议"""
        recommendations = []

        # 基于弱项的建议
        for area in weak_areas:
            if area["accuracy"] < 0.5:
                recommendations.append(
                    f"建议加强{area['type']}练习，当前正确率较低"
                )
            elif area["accuracy"] < 0.7:
                recommendations.append(
                    f"继续巩固{area['type']}，有提升空间"
                )

        # 基于强项的建议
        if strong_areas:
            strongest = strong_areas[0]
            if strongest["accuracy"] > 0.9:
                recommendations.append(
                    f"{strongest['type']}掌握得很好，可以尝试更有挑战性的题目"
                )

        # 通用建议
        if not recommendations:
            recommendations.append("继续保持，每天坚持练习")

        return recommendations

    def _calculate_daily_accuracy(
        self,
        records: List[LearningRecord],
        days: int
    ) -> Dict[str, float]:
        """计算每日正确率"""
        daily_accuracy = {}

        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            date_str = date.strftime("%Y-%m-%d")

            date_start = date.replace(hour=0, minute=0, second=0)
            date_end = date.replace(hour=23, minute=59, second=59)

            day_records = [
                r for r in records
                if date_start <= r.question_time <= date_end
            ]

            if day_records:
                correct = sum(
                    1 for r in day_records
                    if r.answer_result == AnswerResult.CORRECT
                )
                daily_accuracy[date_str] = correct / len(day_records)

        return daily_accuracy
