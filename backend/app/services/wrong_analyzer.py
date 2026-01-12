"""
错误答案分类器（Phase 2.2 - US2）

判断学生答错的根本原因，为后续引导教学提供依据。

支持的错误类型：
- calculation: 计算错误（加减乘除计算错误）
- concept: 概念错误（混淆运算方法、概念理解偏差）
- understanding: 理解错误（题意理解偏差、答非所问）
- careless: 粗心错误（笔误、抄错数字）
"""

import re
from typing import Optional


class WrongAnswerClassifier:
    """
    错误答案分类器

    通过分析问题内容、学生答案、正确答案和答题历史，
    判断学生答错的根本原因。

    分类策略：
    1. 计算错误：运算步骤正确，但计算结果错误
    2. 概念错误：混淆不同运算方法（如加减混淆）
    3. 理解错误：对题意理解有偏差
    4. 粗心错误：答案与正确答案非常接近
    """

    # 一年级数学常见运算关键词
    ADDITION_KEYWORDS = ["加", "和", "一共", "增加", "添上", "plus", "add"]
    SUBTRACTION_KEYWORDS = ["减", "剩", "差", "减少", "去掉", "minus", "subtract"]

    def classify(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        attempts: int = 1
    ) -> str:
        """
        分类错误答案

        Args:
            question: 问题内容
            student_answer: 学生答案
            correct_answer: 正确答案
            attempts: 尝试次数（默认 1）

        Returns:
            错误类型：calculation, concept, understanding, 或 careless
        """
        # 提取数字
        student_num = self._extract_number(student_answer)
        correct_num = self._extract_number(correct_answer)

        if student_num is None or correct_num is None:
            # 无法提取数字，默认为理解错误
            return "understanding"

        # 检查是否为概念错误（混淆运算）- 优先检查
        if self._is_concept_error(question, student_num, correct_num):
            return "concept"

        # 检查是否为理解错误（答非所问）
        if self._is_understanding_error(question, student_answer, correct_answer):
            return "understanding"

        # 检查是否为粗心错误（答案非常接近）
        # 只有在尝试次数较少时才认为是粗心
        if attempts < 3 and self._is_careless_error(student_num, correct_num):
            return "careless"

        # 多次尝试后，倾向于认为是概念或理解问题
        if attempts >= 3:
            # 根据答案差异判断
            if abs(student_num - correct_num) > 10:
                return "concept"
            else:
                return "understanding"

        # 默认为计算错误
        return "calculation"

    def _extract_number(self, text: str) -> Optional[int]:
        """
        从文本中提取数字

        Args:
            text: 文本内容

        Returns:
            提取的数字，如果无法提取则返回 None
        """
        # 尝试直接转换
        try:
            return int(text.strip())
        except (ValueError, TypeError):
            pass

        # 使用正则表达式提取数字
        numbers = re.findall(r'\d+', text)
        if numbers:
            try:
                return int(numbers[0])
            except (ValueError, IndexError):
                pass

        return None

    def _is_careless_error(self, student_num: int, correct_num: int, context: dict = None) -> bool:
        """
        判断是否为粗心错误

        粗心错误特征：
        - 答案与正确答案非常接近（相差 1）
        - 且不是简单的单位数计算错误

        Args:
            student_num: 学生答案（数字）
            correct_num: 正确答案（数字）
            context: 额外上下文（可选）

        Returns:
            是否为粗心错误
        """
        difference = abs(student_num - correct_num)

        # 相差 1 才是粗心错误
        if difference != 1:
            return False

        # 如果正确答案较小（< 10），可能是计算错误而非粗心
        # 例如："3 + 5 = 7" 差 1，但这是计算错误不是粗心
        if correct_num < 10:
            return False

        # 正确答案较大时，差 1 更可能是粗心错误
        return True

    def _is_calculation_error(
        self,
        question: str,
        student_num: int,
        correct_num: int
    ) -> bool:
        """
        判断是否为计算错误

        计算错误特征：
        - 运算方向正确（加法做加法，减法做减法）
        - 但结果不正确
        - 且差异不是简单的粗心（相差 > 2）

        Args:
            question: 问题内容
            student_num: 学生答案（数字）
            correct_num: 正确答案（数字）

        Returns:
            是否为计算错误
        """
        # 提取问题中的数字
        numbers = re.findall(r'\d+', question)
        if len(numbers) < 2:
            return False

        # 检查是否为加法问题
        is_addition = any(kw in question for kw in self.ADDITION_KEYWORDS)

        # 检查是否为减法问题
        is_subtraction = any(kw in question for kw in self.SUBTRACTION_KEYWORDS)

        # 判断运算方向是否正确
        if is_addition and not is_subtraction:
            # 加法问题：学生答案应该大于操作数
            n1, n2 = int(numbers[0]), int(numbers[1])
            expected_range = n1 + n2
            # 如果学生答案在合理范围内但不是正确答案
            if student_num > max(n1, n2) and student_num != expected_range:
                return True

        elif is_subtraction and not is_addition:
            # 减法问题：学生答案应该小于被减数
            n1, n2 = int(numbers[0]), int(numbers[1])
            expected_range = n1 - n2
            # 如果学生答案在合理范围内但不是正确答案
            if 0 <= student_num < n1 and student_num != expected_range:
                return True

        return False

    def _is_concept_error(
        self,
        question: str,
        student_num: int,
        correct_num: int
    ) -> bool:
        """
        判断是否为概念错误

        概念错误特征：
        - 混淆运算方法（如加法做成减法，减法做成加法）
        - 但不包括对"一共"、"总数"等关键词的理解偏差

        Args:
            question: 问题内容
            student_num: 学生答案（数字）
            correct_num: 正确答案（数字）

        Returns:
            是否为概念错误
        """
        # 提取问题中的数字
        numbers = re.findall(r'\d+', question)
        if len(numbers) < 2:
            return False

        n1, n2 = int(numbers[0]), int(numbers[1])

        # 检查是否为加法问题
        is_addition = any(kw in question for kw in self.ADDITION_KEYWORDS)

        # 检查是否为减法问题
        is_subtraction = any(kw in question for kw in self.SUBTRACTION_KEYWORDS)

        # 检查是否有"一共/总数"关键词（这些情况属于理解错误，不是概念错误）
        has_total_keywords = any(kw in question for kw in ["一共", "总数", "总共", "合计", "total"])

        # 加法问题，但答案是减法结果
        # 但如果是"一共"问题，优先归类为理解错误
        if is_addition and not has_total_keywords and student_num == abs(n1 - n2):
            return True

        # 减法问题，但答案是加法结果
        if is_subtraction and student_num == (n1 + n2):
            return True

        return False

    def _is_understanding_error(
        self,
        question: str,
        student_answer: str,
        correct_answer: str
    ) -> bool:
        """
        判断是否为理解错误

        理解错误特征：
        - 问题要求"一共"、"总数"但学生用减法
        - 答案与问题无关
        - 答案格式不符合预期

        Args:
            question: 问题内容
            student_answer: 学生答案
            correct_answer: 正确答案

        Returns:
            是否为理解错误
        """
        # 提取数字
        student_num = self._extract_number(student_answer)
        correct_num = self._extract_number(correct_answer)

        if student_num is None:
            return True

        # 检查是否为"一共/总数"型问题但学生用减法
        if any(kw in question for kw in ["一共", "总数", "总共", "合计", "total"]):
            numbers = re.findall(r'\d+', question)
            if len(numbers) >= 2:
                n1, n2 = int(numbers[0]), int(numbers[1])
                # 如果学生答案是减法结果（且正确答案是加法结果）
                if student_num == abs(n1 - n2) and correct_num == (n1 + n2):
                    return True

        # 检查是否为"剩余/差值"型问题但学生用加法
        # 注意：这可能是概念错误（混淆运算），不一定是理解错误
        # 所以这里不检查，留给 _is_concept_error 处理

        # 如果答案中有多个数字，可能是理解错误
        numbers_in_answer = re.findall(r'\d+', student_answer)
        if len(numbers_in_answer) > 1:
            return True

        # 如果答案包含文字而非数字，可能是理解错误
        if student_answer and not student_answer.strip().isdigit():
            # 检查是否主要是文字
            alphanumeric_ratio = sum(c.isalnum() for c in student_answer) / len(student_answer)
            if alphanumeric_ratio < 0.5:
                return True

        return False
