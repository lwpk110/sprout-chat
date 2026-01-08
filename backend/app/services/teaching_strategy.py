"""
教学策略选择器

根据问题类型和学生情况，选择最优的引导式教学策略
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import re


class ProblemType(Enum):
    """问题类型枚举"""
    ADDITION = "加法"
    SUBTRACTION = "减法"
    MULTIPLICATION = "乘法"
    DIVISION = "除法"
    COMPARISON = "比较"
    WORD_PROBLEM = "应用题"
    UNKNOWN = "未知"


class TeachingStrategySelector:
    """
    教学策略选择器

    负责识别问题类型并选择最适合的引导式教学策略
    """

    def __init__(self):
        """初始化策略选择器"""
        # 每种问题类型的教学策略配置
        self.strategies = {
            ProblemType.ADDITION: {
                "metaphor": "积木",
                "action": "堆积木",
                "metaphor_alternatives": ["糖果", "玩具", "水果"],
                "key_phrases": ["+", "加", "一共有", "总共"],
                "template": "我们来玩个{action}的游戏吧！想象一下，有{metaphor}...",
                "questions": [
                    "这里有几个{metaphor}？",
                    "我们再加几个{metaphor}？",
                    "现在一共有几个{metaphor}了？"
                ]
            },
            ProblemType.SUBTRACTION: {
                "metaphor": "苹果",
                "action": "分苹果",
                "metaphor_alternatives": ["糖果", "积木", "蛋糕"],
                "key_phrases": ["-", "减", "剩", "吃掉", "拿走", "分给"],
                "template": "我们来分{metaphor}吧！本来有{metaphor}...",
                "questions": [
                    "原来有几个{metaphor}？",
                    "拿走（吃掉）了几个{metaphor}？",
                    "现在还剩几个{metaphor}？"
                ]
            },
            ProblemType.COMPARISON: {
                "metaphor": "小兔子",
                "action": "赛跑",
                "metaphor_alternatives": ["小朋友", "积木塔", "树"],
                "key_phrases": ["大", "小", "多", "少", "比较", "哪个"],
                "template": "我们来玩个小兔子赛跑的游戏吧！",
                "questions": [
                    "第一个小兔子跑了{metaphor}米",
                    "第二个小兔子跑了{metaphor}米",
                    "谁跑得快一些？"
                ]
            },
            ProblemType.WORD_PROBLEM: {
                "metaphor": "实物演示",
                "action": "场景还原",
                "metaphor_alternatives": ["画图", "摆弄", "表演"],
                "key_phrases": ["有", "个", "只", "还给", "剩下"],
                "template": "我们来把这个故事演一遍吧！",
                "questions": [
                    "故事里有谁？",
                    "发生了什么事？",
                    "一开始有多少{metaphor}？",
                    "后来发生了什么变化？",
                    "最后结果是什么？"
                ]
            },
            ProblemType.MULTIPLICATION: {
                "metaphor": "分组",
                "action": "分组数数",
                "metaphor_alternatives": ["阵列", "打包"],
                "key_phrases": ["×", "*", "乘", "倍", "每组", "共"],
                "template": "我们来分组数数吧！",
                "questions": [
                    "有几组？",
                    "每组有几个？",
                    "一共有多少个？"
                ]
            },
            ProblemType.DIVISION: {
                "metaphor": "平均分",
                "action": "分东西",
                "metaphor_alternatives": ["分享", "分配"],
                "key_phrases": ["÷", "/", "除", "平均", "平分"],
                "template": "我们来平均分{metaphor}吧！",
                "questions": [
                    "一共有多少{metaphor}？",
                    "要分给几个人？",
                    "每个人分到几个？"
                ]
            },
            ProblemType.UNKNOWN: {
                "metaphor": "一起思考",
                "action": "探索",
                "metaphor_alternatives": [],
                "key_phrases": [],
                "template": "我们一起来看看这道题！",
                "questions": [
                    "题目在说什么？",
                    "我们知道了什么？",
                    "要求我们做什么？"
                ]
            }
        }

    def recognize_problem_type(self, problem: str) -> ProblemType:
        """
        识别问题类型

        Args:
            problem: 问题文本

        Returns:
            ProblemType 枚举值
        """
        problem_lower = problem.lower()

        # 优先级：应用题 > 乘除 > 加减 > 比较

        # 检查是否为应用题（包含场景描述）
        word_problem_patterns = [
            r'小明|小红|有\s*\d+个|只|吃掉|拿走|分给|剩下|还给',
            r'买|卖|花|元|角|分',
            r'米|厘米|分米|克|千克'
        ]
        if any(re.search(pattern, problem_lower) for pattern in word_problem_patterns):
            # 应用题中可能包含加减法
            if '×' in problem or '*' in problem or '乘' in problem:
                return ProblemType.MULTIPLICATION
            elif '÷' in problem or '/' in problem or '除' in problem:
                return ProblemType.DIVISION
            else:
                return ProblemType.WORD_PROBLEM

        # 检查是否为乘法
        if '×' in problem or '*' in problem or '乘' in problem:
            return ProblemType.MULTIPLICATION

        # 检查是否为除法
        if '÷' in problem or '/' in problem or '除' in problem:
            return ProblemType.DIVISION

        # 检查是否为比较
        comparison_patterns = [
            r'哪个大|哪个小|谁多|谁少|比较|比',
            r'大一些|小一点|更多|更少',
            r'高|矮|长|短|重|轻'
        ]
        if any(re.search(pattern, problem_lower) for pattern in comparison_patterns):
            return ProblemType.COMPARISON

        # 检查是否为减法
        subtraction_patterns = [
            r'-|减|剩|少|吃|拿|分|给|用|花'
        ]
        if any(re.search(pattern, problem_lower) for pattern in subtraction_patterns):
            return ProblemType.SUBTRACTION

        # 检查是否为加法
        addition_patterns = [
            r'\+|加|和|共|总|凑|增'
        ]
        if any(re.search(pattern, problem_lower) for pattern in addition_patterns):
            return ProblemType.ADDITION

        # 默认为未知类型
        return ProblemType.UNKNOWN

    def select_strategy(self, problem_type: ProblemType) -> Dict[str, Any]:
        """
        为指定问题类型选择教学策略

        Args:
            problem_type: 问题类型

        Returns:
            策略配置字典
        """
        return self.strategies.get(problem_type, self.strategies[ProblemType.UNKNOWN])

    def generate_question_sequence(
        self,
        problem: str,
        max_steps: int = 5
    ) -> List[str]:
        """
        生成系列引导问题

        将复杂问题分解为多个引导步骤

        Args:
            problem: 原始问题
            max_steps: 最多步骤数

        Returns:
            引导问题列表
        """
        problem_type = self.recognize_problem_type(problem)
        strategy = self.select_strategy(problem_type)

        # 提取关键信息
        numbers = self._extract_numbers(problem)
        questions = []

        if problem_type == ProblemType.ADDITION:
            if len(numbers) >= 2:
                questions.append(
                    f"想象一下，这里有{numbers[0]}个{strategy['metaphor']}"
                )
                questions.append(
                    f"我们又拿来了{numbers[1]}个{strategy['metaphor']}"
                )
                questions.append(
                    f"如果把它们都放在一起，现在一共有几个{strategy['metaphor']}？"
                )

        elif problem_type == ProblemType.SUBTRACTION:
            if len(numbers) >= 2:
                questions.append(
                    f"想象一下，原来有{numbers[0]}个{strategy['metaphor']}"
                )
                questions.append(
                    f"然后吃掉（拿走）了{numbers[1]}个{strategy['metaphor']}"
                )
                questions.append(
                    f"现在还剩几个{strategy['metaphor']}？"
                )

        elif problem_type == ProblemType.COMPARISON:
            if len(numbers) >= 2:
                questions.append(
                    f"想象一下，有{numbers[0]}只小兔子参加赛跑"
                )
                questions.append(
                    f"还有{numbers[1]}只小兔子也参加赛跑"
                )
                questions.append(
                    f"谁跑得快一些？"
                )

        elif problem_type == ProblemType.WORD_PROBLEM:
            # 应用题需要更多步骤
            questions.append("我们先来理解题目在说什么，好吗？")
            if len(numbers) >= 2:
                questions.append(f"题目里一开始提到了{numbers[0]}个{strategy['metaphor']}")
                questions.append("后来发生了什么变化？")
                questions.append("最后要求我们算出什么？")

        # 如果生成的步骤太多，截断
        return questions[:max_steps]

    def _extract_numbers(self, text: str) -> List[int]:
        """
        从文本中提取数字

        Args:
            text: 文本内容

        Returns:
            数字列表
        """
        # 提取阿拉伯数字
        arabic_numbers = [int(n) for n in re.findall(r'\d+', text)]

        # 提取中文数字（简单情况）
        chinese_numbers_map = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '两': 2
        }

        chinese_numbers = []
        for char, value in chinese_numbers_map.items():
            if char in text:
                chinese_numbers.append(value)

        return arabic_numbers + chinese_numbers

    def generate_guided_prompt(
        self,
        problem: str,
        student_age: int = 6,
        problem_context: Optional[Dict] = None
    ) -> str:
        """
        生成引导式 Prompt

        Args:
            problem: 学生问题
            student_age: 学生年龄
            problem_context: 问题上下文（可选）

        Returns:
            引导式 Prompt
        """
        problem_type = self.recognize_problem_type(problem)
        strategy = self.select_strategy(problem_type)

        # 提取数字
        numbers = self._extract_numbers(problem)

        # 构建 Prompt
        if problem_type == ProblemType.ADDITION and len(numbers) >= 2:
            return f"""你是小芽老师，一位面向 {student_age} 岁学生的温柔家教。

学生问：{problem}

**教学策略**：
使用{strategy['metaphor']}比喻来讲解加法。

**引导步骤**：
1. "我们来玩个{strategy['action']}的游戏吧！"
2. "想象一下，小芽老师手里有{numbers[0]}个{strategy['metaphor']}"
3. "又拿来了{numbers[1]}个{strategy['metaphor']}"
4. "把它们都放在一起，现在一共有几个{strategy['metaphor']}？你来数数看！"

**重要提醒**：
- 绝对不要直接说"答案是{sum(numbers)}"
- 要用提问引导
- 语气温柔耐心
- 多用鼓励
"""

        elif problem_type == ProblemType.SUBTRACTION and len(numbers) >= 2:
            return f"""你是小芽老师，一位面向 {student_age} 岁学生的温柔家教。

学生问：{problem}

**教学策略**：
使用{strategy['metaphor']}比喻来讲解减法。

**引导步骤**：
1. "我们来分{strategy['metaphor']}吧！"
2. "想象一下，原来有{numbers[0]}个{strategy['metaphor']}"
3. "然后拿走（吃掉）了{numbers[1]}个{strategy['metaphor']}"
4. "现在还剩几个{strategy['metaphor']}？"

**重要提醒**：
- 绝对不要直接说"答案是{numbers[0]-numbers[1]}"
- 要用提问引导
- 语气温柔耐心
- 多用鼓励
"""

        else:
            # 通用引导 Prompt
            return f"""你是小芽老师，一位面向 {student_age} 岁学生的温柔家教。

学生问：{problem}

**教学策略**：
使用{strategy['metaphor']}方式来引导。

**引导步骤**：
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(self.generate_question_sequence(problem)[:3])])}

**重要提醒**：
- 绝对不要直接给答案
- 要用提问引导
- 语气温柔耐心
- 多用鼓励
- 使用具体比喻
"""
