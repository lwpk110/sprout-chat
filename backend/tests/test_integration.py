"""
集成测试 - 教学策略与对话引擎

测试 TeachingStrategySelector 与 ConversationEngine 的集成
"""

import pytest
from app.services.engine import ConversationEngine
from app.services.teaching_strategy import TeachingStrategySelector, ProblemType


class TestTeachingStrategyIntegration:
    """测试：教学策略集成"""

    def test_engine_has_strategy_selector(self):
        """
        测试：引擎包含策略选择器

        验证 ConversationEngine 正确初始化了 TeachingStrategySelector
        """
        engine = ConversationEngine()

        assert hasattr(engine, 'strategy_selector')
        assert isinstance(engine.strategy_selector, TeachingStrategySelector)

    def test_guided_prompt_generation(self):
        """
        测试：引导式 Prompt 生成

        验证策略选择器能正确生成引导式 Prompt
        """
        engine = ConversationEngine()

        # 测试加法问题
        prompt = engine.strategy_selector.generate_guided_prompt(
            problem="5 + 3 = ?",
            student_age=6
        )

        # 验证 Prompt 包含关键元素
        assert "小芽老师" in prompt
        assert "5" in prompt or "五" in prompt
        assert "3" in prompt or "三" in prompt
        assert "堆积木" in prompt or "游戏" in prompt

    def test_problem_type_recognition_integration(self):
        """
        测试：问题类型识别集成

        验证引擎能正确识别数学问题类型
        """
        engine = ConversationEngine()

        # 加法
        assert engine.strategy_selector.recognize_problem_type("5 + 3") == ProblemType.ADDITION

        # 减法
        problem_type = engine.strategy_selector.recognize_problem_type("有5个苹果，吃掉2个")
        assert problem_type in [ProblemType.SUBTRACTION, ProblemType.WORD_PROBLEM]

        # 比较
        assert engine.strategy_selector.recognize_problem_type("5和3哪个大") == ProblemType.COMPARISON

    def test_question_sequence_generation(self):
        """
        测试：引导问题序列生成

        验证能为复杂问题生成分步骤引导
        """
        engine = ConversationEngine()

        # 应用题应该生成多个步骤
        questions = engine.strategy_selector.generate_question_sequence(
            "小明有5个苹果，吃掉2个，还剩几个？"
        )

        assert len(questions) > 0
        assert len(questions) <= 5

        # 至少有一个问题是引导性的
        has_question = any("?" in q or "？" in q or "几" in q for q in questions)
        assert has_question

    def test_strategy_selection_for_different_types(self):
        """
        测试：不同问题类型的策略选择

        验证每种问题类型都有对应的教学策略
        """
        engine = ConversationEngine()

        # 测试所有问题类型
        problem_types = [
            (ProblemType.ADDITION, "5 + 3 = ?"),
            (ProblemType.SUBTRACTION, "10 - 5 = ?"),
            (ProblemType.MULTIPLICATION, "3 × 4 = ?"),
            (ProblemType.DIVISION, "12 ÷ 4 = ?"),
            (ProblemType.COMPARISON, "5和3哪个大？"),
            (ProblemType.WORD_PROBLEM, "小明有5个苹果"),
        ]

        for expected_type, problem in problem_types:
            strategy = engine.strategy_selector.select_strategy(expected_type)

            # 验证策略存在且包含必要字段
            assert strategy is not None
            assert "metaphor" in strategy
            assert "action" in strategy
            assert "questions" in strategy
            assert len(strategy["questions"]) > 0


class TestEngineResponseGeneration:
    """测试：引擎响应生成"""

    def test_session_creation_with_strategy(self):
        """
        测试：创建会话时策略选择器可用

        验证创建会话后，策略选择器仍然正常工作
        """
        engine = ConversationEngine()
        session_id = engine.create_session(
            student_id="test_integration",
            subject="数学",
            student_age=6
        )

        # 验证会话创建成功
        session = engine.get_session(session_id)
        assert session is not None
        assert session["student_id"] == "test_integration"

        # 验证策略选择器仍然可用
        assert engine.strategy_selector is not None
        assert isinstance(engine.strategy_selector, TeachingStrategySelector)

    def test_conversation_flow_with_strategy(self, monkeypatch):
        """
        测试：对话流程中的策略应用

        注意: 此测试不需要实际调用 AI API，只验证逻辑
        """
        engine = ConversationEngine()
        session_id = engine.create_session("test_flow", student_age=6)

        # 验证会话状态
        assert engine.is_session_valid(session_id)

        # 验证消息列表初始化
        session = engine.get_session(session_id)
        assert "messages" in session
        assert len(session["messages"]) == 0
