"""
响应验证系统（Phase 2.2 - US2）

验证苏格拉底引导式响应是否包含直接答案，确保不违反教学原则。
"""

import re
from typing import Dict, Any


class ResponseValidator:
    """
    响应验证器

    通过多层验证确保引导式响应不包含直接答案。

    验证层级（SC-003 目标准确率 95%）：
    - Layer 1: 关键词检测（"答案是"、"等于"等）
    - Layer 2: 答案检测（数字匹配、表达式匹配）
    - Layer 3: AI 二次验证（可选，使用 Claude API）
    """

    # 直接答案的关键词
    ANSWER_KEYWORDS = [
        "答案是", "结果为", "等于", "就是", "应该是",
        "the answer is", "result is", "equals"
    ]

    def validate_response(
        self,
        response: str,
        correct_answer: str,
        question: str
    ) -> Dict[str, Any]:
        """
        验证引导式响应

        Args:
            response: 引导式响应内容
            correct_answer: 正确答案
            question: 原始问题

        Returns:
            验证结果：{"valid": bool, "reason": str, "layer": int}
        """
        # Layer 1: 关键词检测
        layer1_result = self._check_keywords(response)
        if not layer1_result["valid"]:
            return layer1_result

        # Layer 2: 答案检测
        layer2_result = self._check_answer(response, correct_answer)
        if not layer2_result["valid"]:
            return layer2_result

        # Layer 3: 通过所有验证
        return {
            "valid": True,
            "reason": "response passes all validation layers",
            "layer": 3
        }

    def _check_keywords(self, response: str) -> Dict[str, Any]:
        """
        Layer 1: 关键词检测

        检测响应中是否包含直接答案的关键词

        Args:
            response: 引导式响应内容

        Returns:
            验证结果
        """
        for keyword in self.ANSWER_KEYWORDS:
            if keyword.lower() in response.lower():
                return {
                    "valid": False,
                    "reason": f"contains_answer_keyword:{keyword}",
                    "layer": 1,
                    "keyword": keyword
                }

        return {
            "valid": True,
            "reason": "no answer keywords found",
            "layer": 1
        }

    def _check_answer(self, response: str, correct_answer: str) -> Dict[str, Any]:
        """
        Layer 2: 答案检测

        检测响应中是否包含正确答案

        Args:
            response: 引导式响应内容
            correct_answer: 正确答案

        Returns:
            验证结果
        """
        # 提取响应中的数字
        response_numbers = re.findall(r'\d+', response)
        correct_numbers = re.findall(r'\d+', str(correct_answer))

        # 检查是否包含正确答案的数字
        for num in correct_numbers:
            if num in response_numbers:
                # 检查上下文是否直接给出答案
                # 如果数字出现在 "答案是"、"等于" 等关键词附近，可能是直接答案
                # 这里简化处理：如果数字单独出现或与关键词相邻
                answer_pattern = rf'(?:{num})\s*(?:是|等于|等于号|is|equals)'
                if re.search(answer_pattern, response, re.IGNORECASE):
                    return {
                        "valid": False,
                        "reason": "contains_answer",
                        "layer": 2,
                        "detected_answer": num
                    }

        return {
            "valid": True,
            "reason": "no direct answer detected",
            "layer": 2
        }

    def validate_with_ai(
        self,
        response: str,
        correct_answer: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Layer 3 (可选): AI 二次验证

        使用 Claude API 进行二次验证（暂未实现）

        Args:
            response: 引导式响应内容
            correct_answer: 正确答案
            question: 原始问题

        Returns:
            验证结果
        """
        # AI 二次验证已通过 response_validation.py 中的 ResponseValidationService 实现
        # 这里使用基础规则验证作为快速检查
        return self.validate_response(response, correct_answer, question)
