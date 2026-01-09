"""
多科目管理服务

实现多科目支持、题目管理、进度追踪等功能
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

from app.models.subjects import (
    Subject,
    SubjectConfig,
    Problem,
    StudentAnswer,
    SubjectProgress,
    SubjectReport,
    MultiSubjectSummary,
    MathProblemType,
    ChineseProblemType,
    EnglishProblemType,
    ScienceProblemType
)


class MultiSubjectManager:
    """
    多科目管理器

    负责管理多个科目的配置、题目、进度和报告
    """

    def __init__(self):
        """初始化多科目管理器"""
        # 内存存储（生产环境应使用数据库）
        self.subject_configs: Dict[str, SubjectConfig] = {}
        self.problems: Dict[str, Problem] = {}
        self.answers: Dict[str, StudentAnswer] = {}
        self.student_subjects: Dict[str, Dict[str, SubjectConfig]] = defaultdict(dict)

    # ============ 科目配置 ============

    def create_subject_config(
        self,
        subject: Subject,
        difficulty_level: str = "简单",
        teaching_style: str = "引导式",
        enabled: bool = True,
        **kwargs
    ) -> SubjectConfig:
        """
        创建科目配置

        Args:
            subject: 科目
            difficulty_level: 难度等级
            teaching_style: 教学风格
            enabled: 是否启用
            **kwargs: 其他配置

        Returns:
            科目配置
        """
        config = SubjectConfig(
            subject=subject,
            enabled=enabled,
            difficulty_level=difficulty_level,
            teaching_style=teaching_style,
            **kwargs
        )

        key = f"default_{subject.value}"
        self.subject_configs[key] = config

        return config

    def update_subject_status(
        self,
        student_id: str,
        subject: Subject,
        enabled: bool
    ) -> SubjectConfig:
        """
        更新科目启用状态

        Args:
            student_id: 学生 ID
            subject: 科目
            enabled: 是否启用

        Returns:
            更新后的配置
        """
        key = f"{student_id}_{subject.value}"

        if key not in self.student_subjects[student_id]:
            # 创建默认配置
            self.student_subjects[student_id][subject.value] = SubjectConfig(
                subject=subject,
                enabled=enabled
            )
        else:
            self.student_subjects[student_id][subject.value].enabled = enabled

        return self.student_subjects[student_id][subject.value]

    def get_available_subjects(self, student_id: str = "default") -> List[Subject]:
        """
        获取可用科目

        Args:
            student_id: 学生 ID（可选）

        Returns:
            可用科目列表
        """
        if student_id == "default":
            # 返回全局启用的科目
            return [
                config.subject
                for config in self.subject_configs.values()
                if config.enabled
            ]
        else:
            # 返回学生启用的科目
            return [
                Subject(config.subject)
                for config in self.student_subjects[student_id].values()
                if config.enabled
            ]

    # ============ 题目管理 ============

    def create_problem(
        self,
        subject: Subject,
        problem_type: str,
        content: str,
        correct_answer: str,
        options: Optional[List[str]] = None,
        difficulty: str = "简单",
        **kwargs
    ) -> Problem:
        """
        创建题目

        Args:
            subject: 科目
            problem_type: 题型
            content: 题目内容
            correct_answer: 正确答案
            options: 选项（选择题）
            difficulty: 难度
            **kwargs: 其他属性

        Returns:
            题目
        """
        problem = Problem(
            problem_id=str(uuid.uuid4()),
            subject=subject,
            problem_type=problem_type,
            content=content,
            options=options,
            correct_answer=correct_answer,
            difficulty=difficulty,
            **kwargs
        )

        self.problems[problem.problem_id] = problem

        return problem

    def get_problems_by_subject(
        self,
        subject: Subject,
        difficulty: Optional[str] = None,
        limit: int = 100
    ) -> List[Problem]:
        """
        按科目获取题目

        Args:
            subject: 科目
            difficulty: 难度筛选（可选）
            limit: 返回数量限制

        Returns:
            题目列表
        """
        problems = [
            p for p in self.problems.values()
            if p.subject == subject
        ]

        if difficulty:
            problems = [p for p in problems if p.difficulty == difficulty]

        return problems[:limit]

    def get_problem_by_id(self, problem_id: str) -> Optional[Problem]:
        """
        根据 ID 获取题目

        Args:
            problem_id: 题目 ID

        Returns:
            题目或 None
        """
        return self.problems.get(problem_id)

    # ============ 答题记录 ============

    def record_answer(
        self,
        student_id: str,
        problem_id: str,
        subject: Subject,
        problem_type: str,
        student_answer: str,
        is_correct: bool,
        attempts: int = 1,
        response_duration: Optional[float] = None
    ) -> StudentAnswer:
        """
        记录答题结果

        Args:
            student_id: 学生 ID
            problem_id: 题目 ID
            subject: 科目
            problem_type: 题型
            student_answer: 学生答案
            is_correct: 是否正确
            attempts: 尝试次数
            response_duration: 响应时长

        Returns:
            答题记录
        """
        answer = StudentAnswer(
            answer_id=str(uuid.uuid4()),
            student_id=student_id,
            problem_id=problem_id,
            subject=subject,
            problem_type=problem_type,
            student_answer=student_answer,
            is_correct=is_correct,
            attempts=attempts,
            answer_time=datetime.now(),
            response_duration=response_duration
        )

        self.answers[answer.answer_id] = answer

        return answer

    def get_answers_by_student(
        self,
        student_id: str,
        subject: Optional[Subject] = None
    ) -> List[StudentAnswer]:
        """
        获取学生的答题记录

        Args:
            student_id: 学生 ID
            subject: 科目筛选（可选）

        Returns:
            答题记录列表
        """
        answers = [
            a for a in self.answers.values()
            if a.student_id == student_id
        ]

        if subject:
            answers = [a for a in answers if a.subject == subject]

        return answers

    # ============ 进度追踪 ============

    def get_subject_progress(
        self,
        student_id: str,
        subject: Subject
    ) -> SubjectProgress:
        """
        获取科目进度

        Args:
            student_id: 学生 ID
            subject: 科目

        Returns:
            科目进度
        """
        # 获取该科目该学生的所有答题
        answers = self.get_answers_by_student(student_id, subject)

        # 计算统计
        total_problems = len(answers)
        correct_count = sum(1 for a in answers if a.is_correct)
        accuracy_rate = correct_count / total_problems if total_problems > 0 else 0.0

        # 按题型统计
        by_problem_type = defaultdict(lambda: {"total": 0, "correct": 0})
        for answer in answers:
            by_problem_type[answer.problem_type]["total"] += 1
            if answer.is_correct:
                by_problem_type[answer.problem_type]["correct"] += 1

        # 学习时长
        total_learning_time = sum(
            a.response_duration or 0 for a in answers
        )

        # 时间范围
        if answers:
            first_activity = min(a.question_time for a in answers)
            last_activity = max(a.question_time for a in answers)
        else:
            first_activity = None
            last_activity = None

        progress = SubjectProgress(
            student_id=student_id,
            subject=subject,
            total_problems=total_problems,
            correct_count=correct_count,
            accuracy_rate=accuracy_rate,
            by_problem_type=dict(by_problem_type),
            total_learning_time=total_learning_time,
            first_activity=first_activity,
            last_activity=last_activity
        )

        return progress

    def get_multi_subject_summary(self, student_id: str) -> MultiSubjectSummary:
        """
        获取多科目汇总

        Args:
            student_id: 学生 ID

        Returns:
            多科目汇总
        """
        subject_progress = {}

        # 获取所有科目的进度
        for subject in Subject:
            progress = self.get_subject_progress(student_id, subject)
            if progress.total_problems > 0:
                subject_progress[subject.value] = progress

        # 总体统计
        total_problems = sum(p.total_problems for p in subject_progress.values())
        total_correct = sum(p.correct_count for p in subject_progress.values())
        overall_accuracy = total_correct / total_problems if total_problems > 0 else 0.0

        # 最强和最弱科目
        if subject_progress:
            strongest_subject = max(
                subject_progress.items(),
                key=lambda x: x[1].accuracy_rate
            )[0]
            weakest_subject = min(
                subject_progress.items(),
                key=lambda x: x[1].accuracy_rate
            )[0]
        else:
            strongest_subject = None
            weakest_subject = None

        # 学习时长分布
        learning_time_by_subject = {
            subject: progress.total_learning_time
            for subject, progress in subject_progress.items()
        }

        summary = MultiSubjectSummary(
            student_id=student_id,
            subject_progress=subject_progress,
            total_problems=total_problems,
            total_correct=total_correct,
            overall_accuracy=overall_accuracy,
            strongest_subject=strongest_subject,
            weakest_subject=weakest_subject,
            learning_time_by_subject=learning_time_by_subject
        )

        return summary

    # ============ 报告生成 ============

    def generate_subject_report(
        self,
        student_id: str,
        subject: Subject,
        days: int = 7
    ) -> SubjectReport:
        """
        生成科目报告

        Args:
            student_id: 学生 ID
            subject: 科目
            days: 最近多少天

        Returns:
            科目报告
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 获取时间范围内的答题
        answers = [
            a for a in self.get_answers_by_student(student_id, subject)
            if start_date <= a.question_time <= end_date
        ]

        # 计算统计
        total_problems = len(answers)
        correct_count = sum(1 for a in answers if a.is_correct)
        accuracy_rate = correct_count / total_problems if total_problems > 0 else 0.0

        # 按题型统计
        by_problem_type = defaultdict(lambda: {"total": 0, "correct": 0})
        for answer in answers:
            by_problem_type[answer.problem_type]["total"] += 1
            if answer.is_correct:
                by_problem_type[answer.problem_type]["correct"] += 1

        # 学习趋势
        learning_trend = []
        for day in range(days):
            day_date = start_date + timedelta(days=day)
            day_start = day_date.replace(hour=0, minute=0, second=0)
            day_end = day_date.replace(hour=23, minute=59, second=59)

            day_answers = [
                a for a in answers
                if day_start <= a.question_time <= day_end
            ]

            if day_answers:
                day_correct = sum(1 for a in day_answers if a.is_correct)
                day_accuracy = day_correct / len(day_answers)

                learning_trend.append({
                    "date": day_date.strftime("%Y-%m-%d"),
                    "questions": len(day_answers),
                    "correct": day_correct,
                    "accuracy": day_accuracy
                })

        # 强弱项
        by_type_accuracy = {
            ptype: stats["correct"] / stats["total"]
            for ptype, stats in by_problem_type.items()
            if stats["total"] >= 3  # 至少3题
        }

        if by_type_accuracy:
            strong_areas = [
                ptype for ptype, acc in by_type_accuracy.items()
                if acc >= 0.8
            ]
            weak_areas = [
                ptype for ptype, acc in by_type_accuracy.items()
                if acc < 0.6
            ]
        else:
            strong_areas = []
            weak_areas = []

        # 建议
        recommendations = self._generate_subject_recommendations(
            subject, by_type_accuracy, strong_areas, weak_areas
        )

        report = SubjectReport(
            report_id=str(uuid.uuid4()),
            student_id=student_id,
            subject=subject,
            start_date=start_date,
            end_date=end_date,
            total_problems=total_problems,
            correct_count=correct_count,
            accuracy_rate=accuracy_rate,
            by_problem_type=dict(by_problem_type),
            learning_trend=learning_trend,
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            recommendations=recommendations
        )

        return report

    def generate_learning_recommendations(
        self,
        student_id: str
    ) -> List[str]:
        """
        生成学习建议

        基于多科目表现生成个性化建议

        Args:
            student_id: 学生 ID

        Returns:
            建议列表
        """
        summary = self.get_multi_subject_summary(student_id)
        recommendations = []

        # 基于最弱科目的建议
        if summary.weakest_subject:
            weakest_progress = summary.subject_progress.get(summary.weakest_subject)
            if weakest_progress and weakest_progress.accuracy_rate < 0.6:
                recommendations.append(
                    f"建议加强{summary.weakest_subject}的学习，当前正确率较低"
                )

        # 基于最强科目的建议
        if summary.strongest_subject:
            strongest_progress = summary.subject_progress.get(summary.strongest_subject)
            if strongest_progress and strongest_progress.accuracy_rate > 0.9:
                recommendations.append(
                    f"{summary.strongest_subject}掌握得很好，可以尝试更有挑战性的内容"
                )

        # 平衡发展建议
        if len(summary.subject_progress) > 1:
            recommendations.append("建议保持多科目平衡发展")

        return recommendations

    def clear_all_data(self):
        """清空所有数据（用于测试）"""
        self.subject_configs.clear()
        self.problems.clear()
        self.answers.clear()
        self.student_subjects.clear()

    # ============ 私有方法 ============

    def _generate_subject_recommendations(
        self,
        subject: Subject,
        by_type_accuracy: Dict[str, float],
        strong_areas: List[str],
        weak_areas: List[str]
    ) -> List[str]:
        """生成科目建议"""
        recommendations = []

        # 基于弱项
        for area in weak_areas:
            recommendations.append(f"建议加强{area}的练习")

        # 基于强项
        for area in strong_areas:
            recommendations.append(f"{area}掌握得很好")

        # 科目特定建议
        if subject == Subject.MATH:
            recommendations.append("数学学习要注重理解概念，不要死记硬背")
        elif subject == Subject.CHINESE:
            recommendations.append("语文学习要多读多写，培养语感")
        elif subject == Subject.ENGLISH:
            recommendations.append("英语学习要注重听说读写全面发展")

        return recommendations
