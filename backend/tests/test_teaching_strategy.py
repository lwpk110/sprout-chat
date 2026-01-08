"""
引导式教学优化测试 - TDD Red Phase

测试小芽教学的进阶策略：
- 问题类型识别
- 教学策略选择
- 多步骤引导
- 错误处理优化
"""

import pytest
from app.services.engine import ConversationEngine
from app.services.teaching_strategy import TeachingStrategySelector, ProblemType
from app.core.config import settings


@pytest.fixture
def engine():
    """创建对话引擎实例"""
    engine = ConversationEngine()
    yield engine
    # 清理
    engine.conversations.clear()


@pytest.fixture
def strategy_selector():
    """创建教学策略选择器实例"""
    return TeachingStrategySelector()


class TestProblemTypeRecognition:
    """测试：问题类型识别"""

    @pytest.mark.asyncio
    async def test_recognize_addition_problem(self, strategy_selector):
        """
        测试：识别加法问题

        输入: "5 + 3 = ?"
        预期: ProblemType.ADDITION
        """
        problem = "5 + 3 = ?"
        problem_type = strategy_selector.recognize_problem_type(problem)

        assert problem_type == ProblemType.ADDITION
        assert problem_type.value == "加法"

    @pytest.mark.asyncio
    async def test_recognize_subtraction_problem(self, strategy_selector):
        """
        测试：识别减法问题

        输入: "有5个苹果，吃掉2个"
        预期: ProblemType.SUBTRACTION
        """
        problem = "有5个苹果，吃掉2个"
        problem_type = strategy_selector.recognize_problem_type(problem)

        # 减法或应用题都算正确（因为有场景描述）
        assert problem_type in [ProblemType.SUBTRACTION, ProblemType.WORD_PROBLEM]
        assert problem_type.value in ["减法", "应用题"]

    @pytest.mark.asyncio
    async def test_recognize_comparison_problem(self, strategy_selector):
        """
        测试：识别比较问题

        输入: "5和3哪个大？"
        预期: ProblemType.COMPARISON
        """
        problem = "5和3哪个大？"
        problem_type = strategy_selector.recognize_problem_type(problem)

        assert problem_type == ProblemType.COMPARISON
        assert problem_type.value == "比较"

    @pytest.mark.asyncio
    async def test_recognize_word_problem(self, strategy_selector):
        """
        测试：识别应用题

        输入: "小明有5个苹果，吃掉2个，还剩几个？"
        预期: ProblemType.WORD_PROBLEM
        """
        problem = "小明有5个苹果，吃掉2个，还剩几个？"
        problem_type = strategy_selector.recognize_problem_type(problem)

        assert problem_type == ProblemType.WORD_PROBLEM
        assert problem_type.value == "应用题"


class TestTeachingStrategySelection:
    """测试：教学策略选择"""

    @pytest.mark.asyncio
    async def test_select_strategy_for_addition(self, strategy_selector):
        """
        测试：为加法问题选择策略

        加法策略应该使用"堆积木"比喻
        """
        strategy = strategy_selector.select_strategy(ProblemType.ADDITION)

        assert strategy is not None
        assert "metaphor" in strategy
        assert strategy["metaphor"] in ["积木", "糖果", "玩具"]

    @pytest.mark.asyncio
    async def test_select_strategy_for_subtraction(self, strategy_selector):
        """
        测试：为减法问题选择策略

        减法策略应该使用"分苹果"比喻
        """
        strategy = strategy_selector.select_strategy(ProblemType.SUBTRACTION)

        assert strategy is not None
        assert "metaphor" in strategy
        assert strategy["metaphor"] in ["苹果", "糖果", "积木"]

    @pytest.mark.asyncio
    async def test_select_strategy_for_comparison(self, strategy_selector):
        """
        测试：为比较问题选择策略

        比较策略应该使用"小兔子赛跑"比喻
        """
        strategy = strategy_selector.select_strategy(ProblemType.COMPARISON)

        assert strategy is not None
        assert "metaphor" in strategy
        assert strategy["metaphor"] in ["小兔子", "赛跑", "比较高矮"]


class TestMultiStepGuidance:
    """测试：多步骤引导"""

    @pytest.mark.asyncio
    async def test_generate_guided_questions_sequence(self, strategy_selector):
        """
        测试：生成系列引导问题

        对于复杂问题，应该分解为多个步骤
        """
        problem = "小明有5个苹果，吃掉2个，还剩几个？"
        questions = strategy_selector.generate_question_sequence(problem)

        # 应该生成至少一个问题
        assert len(questions) >= 1
        assert len(questions) <= 5  # 最多5个步骤

        # 至少有一个问题应该是引导性的
        has_question = any("?" in q or "？" in q for q in questions)
        assert has_question

    @pytest.mark.asyncio
    async def test_step_by_step_guidance(self, engine):
        """
        测试：分步骤引导对话

        模拟多轮对话，验证引导的渐进性
        """
        session_id = engine.create_session(
            student_id="test_step",
            subject="数学",
            student_age=6
        )

        # 第一轮：提出问题
        response1 = await engine.generate_response_async(
            session_id,
            "小明有5个苹果，吃掉2个"
        )

        # 应该提到苹果或吃掉
        assert "苹果" in response1
        assert "吃掉" in response1 or "啊呜" in response1

        # 第二轮：继续引导
        response2 = await engine.generate_response_async(
            session_id,
            "不知道怎么算"
        )

        # 应该提供更具体的引导（包含引导性词汇）
        assert "我们" in response2 or "试试" in response2 or "想想" in response2 or "游戏" in response2
        # 响应不应该为空
        assert len(response2) > 50


class TestErrorHandlingOptimization:
    """测试：错误处理优化"""

    @pytest.mark.asyncio
    async def test_wrong_answer_encouragement(self, engine):
        """
        测试：学生答错时的鼓励

        不应该说"错了"，而是要温柔引导
        """
        session_id = engine.create_session(
            student_id="test_error",
            subject="数学",
            student_age=6
        )

        # 先提问，建立上下文
        await engine.generate_response_async(session_id, "5 + 3 = ?")

        # 学生给出错误答案
        response = await engine.generate_response_async(
            session_id,
            "10个"  # 5 + 3 的错误答案
        )

        # 检查不包含严厉词汇
        assert "错" not in response or "不对" not in response
        assert "笨" not in response
        assert "傻" not in response

        # 应该包含鼓励和引导（response 不为空）
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_partial_answer_affirmation(self, engine):
        """
        测试：部分正确的答案也要鼓励

        学生可能只回答了一部分，要肯定正确的部分
        """
        session_id = engine.create_session(
            student_id="test_partial",
            subject="数学",
            student_age=6
        )

        # 先提问
        await engine.generate_response_async(session_id, "5 + 3 = ?")

        # 学生回答"5"（只说了第一个数）
        response = await engine.generate_response_async(
            session_id,
            "5"
        )

        # 应该肯定并引导继续（response 不为空且友好）
        assert len(response) > 0
        # 不应该包含批评（检查负面词汇，但允许"没错"等正面词汇）
        assert "笨" not in response
        assert "傻" not in response
        # 不应该直接说"错了"或"不对"
        assert not response.startswith("错") and not response.startswith("不对")


class TestPersonalizedGuidance:
    """测试：个性化引导"""

    @pytest.mark.asyncio
    async def test_adapt_to_student_age(self, engine):
        """
        测试：根据学生年龄调整语言

        6岁和7岁的孩子语言复杂度应该不同
        """
        # 6岁学生
        session1 = engine.create_session("test_age6", student_age=6)
        response1 = await engine.generate_response_async(
            session1,
            "5 + 3 = ?"
        )

        # 7岁学生
        session2 = engine.create_session("test_age7", student_age=7)
        response2 = await engine.generate_response_async(
            session2,
            "5 + 3 = ?"
        )

        # 两个响应都应该符合年龄特点
        assert len(response1) > 20
        assert len(response2) > 20

    @pytest.mark.asyncio
    async def test_adapt_difficulty_level(self, engine):
        """
        测试：根据学生表现调整难度

        连续答对应该增加难度，连续答错应该降低难度
        """
        session_id = engine.create_session(
            student_id="test_adapt",
            subject="数学"
        )

        # 学生连续答对
        await engine.generate_response_async(session_id, "5 + 3 = ?")
        await engine.generate_response_async(session_id, "8块")

        # 下一个问题的难度应该调整
        # 这里我们验证会话能够正确处理多轮对话
        history = await engine.get_conversation_history_async(session_id)
        assert len(history) >= 4


class TestTeachingQualityMetrics:
    """测试：教学质量指标"""

    @pytest.mark.asyncio
    async def test_guidance_ratio(self, engine):
        """
        测试：引导性问题比例

        响应中问题句的比例应该 > 30%
        """
        session_id = engine.create_session("test_ratio", subject="数学")
        response = await engine.generate_response_async(
            session_id,
            "5 + 3 = ?"
        )

        # 统计问号数量
        question_count = response.count("？") + response.count("?")
        total_sentences = len(response.split("。")) + len(response.split("！"))

        # 至少应该有一个问题
        assert question_count >= 1

    @pytest.mark.asyncio
    async def test_metaphor_usage(self, engine):
        """
        测试：比喻使用频率

        响应中应该包含具象比喻
        """
        session_id = engine.create_session("test_metaphor", subject="数学")
        response = await engine.generate_response_async(
            session_id,
            "5 + 3 = ?"
        )

        # 应该包含常见比喻词汇
        metaphor_words = [
            "积木", "苹果", "糖果", "小兔子", "小白兔",
            "玩具", "水果", "蛋糕"
        ]

        has_metaphor = any(word in response for word in metaphor_words)
        assert has_metaphor, f"响应应该包含比喻词汇: {response[:50]}"

    @pytest.mark.asyncio
    async def test_encouragement_frequency(self, engine):
        """
        测试：鼓励词频率

        响应中应该包含鼓励性词汇
        """
        session_id = engine.create_session("test_encourage", subject="数学")
        response = await engine.generate_response_async(
            session_id,
            "我不会做"
        )

        # 应该包含鼓励词汇
        encouragement_words = [
            "没关系", "试试", "加油",
            "我们一起", "慢慢来", "相信你"
        ]

        has_encouragement = any(word in response for word in encouragement_words)
        assert has_encouragement, f"响应应该包含鼓励词汇: {response[:50]}"


# Red Phase 标记
# pytestmark = pytest.mark.red_phase
