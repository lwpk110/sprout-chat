"""
多科目扩展测试 - TDD Red Phase

测试多科目支持功能：
- 科目配置
- 题目管理
- 学习进度追踪
- 多科目报告
"""

import pytest
from datetime import datetime
from app.services.multi_subject import MultiSubjectManager
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
    EnglishProblemType
)


@pytest.fixture
def manager():
    """创建多科目管理器实例"""
    manager = MultiSubjectManager()
    # 清理测试数据
    manager.clear_all_data()
    yield manager
    # 清理
    manager.clear_all_data()


class TestSubjectConfiguration:
    """测试：科目配置"""

    def test_create_subject_config(self, manager):
        """
        测试：创建科目配置

        验证能够为不同科目创建配置
        """
        config = manager.create_subject_config(
            subject=Subject.MATH,
            difficulty_level="中等",
            teaching_style="引导式"
        )

        assert config is not None
        assert config.subject == Subject.MATH
        assert config.difficulty_level == "中等"
        assert config.enabled == True

    def test_enable_disable_subject(self, manager):
        """
        测试：启用/禁用科目

        验证能够控制科目的启用状态
        """
        # 创建数学配置
        config = manager.create_subject_config(
            subject=Subject.MATH,
            enabled=True
        )

        # 禁用数学
        updated = manager.update_subject_status(
            student_id="test_student",
            subject=Subject.MATH,
            enabled=False
        )

        assert updated.enabled == False

    def test_get_available_subjects(self, manager):
        """
        测试：获取可用科目

        验证能够获取所有启用的科目列表
        """
        # 创建多个科目配置
        manager.create_subject_config(subject=Subject.MATH, enabled=True)
        manager.create_subject_config(subject=Subject.CHINESE, enabled=True)
        manager.create_subject_config(subject=Subject.ENGLISH, enabled=False)

        # 获取可用科目
        subjects = manager.get_available_subjects()

        assert Subject.MATH in subjects
        assert Subject.CHINESE in subjects
        assert Subject.ENGLISH not in subjects


class TestProblemManagement:
    """测试：题目管理"""

    def test_create_math_problem(self, manager):
        """
        测试：创建数学题目

        验证能够创建数学题目
        """
        problem = manager.create_problem(
            subject=Subject.MATH,
            problem_type=MathProblemType.ADDITION.value,
            content="5 + 3 = ?",
            correct_answer="8",
            difficulty="简单"
        )

        assert problem is not None
        assert problem.subject == Subject.MATH
        assert problem.problem_type == "加法"
        assert problem.content == "5 + 3 = ?"

    def test_create_chinese_problem(self, manager):
        """
        测试：创建语文题目

        验证能够创建语文题目（拼音、识字等）
        """
        problem = manager.create_problem(
            subject=Subject.CHINESE,
            problem_type=ChineseProblemType.PINYIN.value,
            content="'苹果'的拼音是？",
            options=["píng guǒ", "pín gǒ", "píng gǔ", "pīn gǒ"],
            correct_answer="píng guǒ",
            difficulty="简单"
        )

        assert problem.subject == Subject.CHINESE
        assert problem.problem_type == "拼音"
        assert len(problem.options) == 4

    def test_create_english_problem(self, manager):
        """
        测试：创建英语题目

        验证能够创建英语题目（字母、词汇等）
        """
        problem = manager.create_problem(
            subject=Subject.ENGLISH,
            problem_type=EnglishProblemType.ALPHABET.value,
            content="字母 'A' 的大写是？",
            options=["a", "A", "B", "b"],
            correct_answer="A",
            difficulty="简单"
        )

        assert problem.subject == Subject.ENGLISH
        assert problem.problem_type == "字母"

    def test_get_problems_by_subject(self, manager):
        """
        测试：按科目获取题目

        验证能够按科目筛选题目
        """
        # 创建不同科目的题目
        manager.create_problem(
            subject=Subject.MATH,
            problem_type=MathProblemType.ADDITION.value,
            content="5 + 3 = ?",
            correct_answer="8"
        )

        manager.create_problem(
            subject=Subject.CHINESE,
            problem_type=ChineseProblemType.PINYIN.value,
            content="拼音题目",
            correct_answer="píng guǒ"
        )

        # 获取数学题目
        math_problems = manager.get_problems_by_subject(Subject.MATH)

        assert len(math_problems) == 1
        assert math_problems[0].subject == Subject.MATH


class TestProgressTracking:
    """测试：进度追踪"""

    def test_record_math_answer(self, manager):
        """
        测试：记录数学答题

        验证能够记录数学答题结果
        """
        answer = manager.record_answer(
            student_id="student_001",
            problem_id="problem_001",
            subject=Subject.MATH,
            problem_type=MathProblemType.ADDITION.value,
            student_answer="8",
            is_correct=True
        )

        assert answer is not None
        assert answer.subject == Subject.MATH
        assert answer.is_correct == True

    def test_get_subject_progress(self, manager):
        """
        测试：获取科目进度

        验证能够获取特定科目的学习进度
        """
        student_id = "student_progress"

        # 记录3次数学答题（2对1错）
        manager.record_answer(
            student_id=student_id,
            problem_id="math_001",
            subject=Subject.MATH,
            problem_type=MathProblemType.ADDITION.value,
            student_answer="8",
            is_correct=True
        )

        manager.record_answer(
            student_id=student_id,
            problem_id="math_002",
            subject=Subject.MATH,
            problem_type=MathProblemType.ADDITION.value,
            student_answer="7",
            is_correct=True
        )

        manager.record_answer(
            student_id=student_id,
            problem_id="math_003",
            subject=Subject.MATH,
            problem_type=MathProblemType.SUBTRACTION.value,
            student_answer="5",
            is_correct=False
        )

        # 获取数学进度
        progress = manager.get_subject_progress(student_id, Subject.MATH)

        assert progress.total_problems == 3
        assert progress.correct_count == 2
        assert progress.accuracy_rate == 2/3

    def test_multi_subject_tracking(self, manager):
        """
        测试：多科目追踪

        验证能够同时追踪多个科目的进度
        """
        student_id = "student_multi"

        # 数学答题
        manager.record_answer(
            student_id=student_id,
            problem_id="math_001",
            subject=Subject.MATH,
            problem_type=MathProblemType.ADDITION.value,
            student_answer="8",
            is_correct=True
        )

        # 语文答题
        manager.record_answer(
            student_id=student_id,
            problem_id="chinese_001",
            subject=Subject.CHINESE,
            problem_type=ChineseProblemType.PINYIN.value,
            student_answer="píng guǒ",
            is_correct=True
        )

        # 英语答题
        manager.record_answer(
            student_id=student_id,
            problem_id="english_001",
            subject=Subject.ENGLISH,
            problem_type=EnglishProblemType.ALPHABET.value,
            student_answer="A",
            is_correct=False
        )

        # 获取多科目汇总
        summary = manager.get_multi_subject_summary(student_id)

        assert summary.total_problems == 3
        assert summary.total_correct == 2
        assert Subject.MATH.value in summary.subject_progress
        assert Subject.CHINESE.value in summary.subject_progress
        assert Subject.ENGLISH.value in summary.subject_progress


class TestSubjectReporting:
    """测试：科目报告"""

    def test_generate_subject_report(self, manager):
        """
        测试：生成科目报告

        验证能够生成特定科目的学习报告
        """
        student_id = "student_report"

        # 记录一些答题
        for i in range(5):
            manager.record_answer(
                student_id=student_id,
                problem_id=f"math_{i}",
                subject=Subject.MATH,
                problem_type=MathProblemType.ADDITION.value,
                student_answer=str(i + 3),
                is_correct=i < 4  # 4/5 正确
            )

        # 生成数学报告
        report = manager.generate_subject_report(
            student_id=student_id,
            subject=Subject.MATH,
            days=7
        )

        assert report is not None
        assert report.student_id == student_id
        assert report.subject == Subject.MATH
        assert report.total_problems == 5

    def test_multi_subject_comparison(self, manager):
        """
        测试：多科目对比

        验证能够对比不同科目的表现
        """
        student_id = "student_compare"

        # 数学（表现好）
        for i in range(5):
            manager.record_answer(
                student_id=student_id,
                problem_id=f"math_{i}",
                subject=Subject.MATH,
                problem_type=MathProblemType.ADDITION.value,
                student_answer=str(i + 3),
                is_correct=True  # 全对
            )

        # 英语（表现差）
        for i in range(5):
            manager.record_answer(
                student_id=student_id,
                problem_id=f"english_{i}",
                subject=Subject.ENGLISH,
                problem_type=EnglishProblemType.ALPHABET.value,
                student_answer="A",
                is_correct=i < 2  # 2/5 正确
            )

        # 获取汇总
        summary = manager.get_multi_subject_summary(student_id)

        # 验证最强和最弱科目
        assert summary.strongest_subject == "数学"
        assert summary.weakest_subject == "英语"


class TestCrossSubjectFeatures:
    """测试：跨科目功能"""

    def test_knowledge_transfer(self, manager):
        """
        测试：知识点迁移

        验证能够识别跨科目的知识点
        """
        # 数学和语文都涉及数字
        math_problem = manager.create_problem(
            subject=Subject.MATH,
            problem_type=MathProblemType.ADDITION.value,
            content="5 + 3 = ?",
            correct_answer="8",
            knowledge_points=["数字认知", "加法运算"]
        )

        chinese_problem = manager.create_problem(
            subject=Subject.CHINESE,
            problem_type=ChineseProblemType.RECOGNITION.value,
            content="认读数字'五'",
            correct_answer="五",
            knowledge_points=["数字认知"]
        )

        # 验证知识点关联
        math_points = set(math_problem.knowledge_points)
        chinese_points = set(chinese_problem.knowledge_points)

        assert len(math_points & chinese_points) > 0  # 有共同知识点

    def test_personalized_learning_path(self, manager):
        """
        测试：个性化学习路径

        验证能够根据多科目表现推荐学习路径
        """
        student_id = "student_path"

        # 记录不同科目的表现
        # 数学强
        for i in range(5):
            manager.record_answer(
                student_id=student_id,
                problem_id=f"math_{i}",
                subject=Subject.MATH,
                problem_type=MathProblemType.ADDITION.value,
                student_answer=str(i + 3),
                is_correct=True
            )

        # 英语弱
        for i in range(5):
            manager.record_answer(
                student_id=student_id,
                problem_id=f"english_{i}",
                subject=Subject.ENGLISH,
                problem_type=EnglishProblemType.ALPHABET.value,
                student_answer="A",
                is_correct=False
            )

        # 获取建议
        summary = manager.get_multi_subject_summary(student_id)
        recommendations = manager.generate_learning_recommendations(student_id)

        # 应该包含加强英语的建议
        assert any("英语" in rec for rec in recommendations)


# Red Phase 标记
# pytestmark = pytest.mark.red_phase
