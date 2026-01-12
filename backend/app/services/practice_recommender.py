"""
练习推荐服务（Phase 2.2 - US3）

基于学生的错题记录，生成针对性的练习推荐。
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.database import WrongAnswerRecord, LearningRecord


class PracticeRecommenderService:
    """
    练习推荐服务

    根据学生的错题记录，智能推荐相似题目进行针对性练习。
    """

    def __init__(self):
        """初始化练习推荐服务"""
        pass

    def get_wrong_answers(
        self,
        db: Session,
        student_id: int,
        error_type: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取错题列表

        Args:
            db: 数据库会话
            student_id: 学生 ID
            error_type: 错误类型筛选（可选）
            is_resolved: 解决状态筛选（可选）
            page: 页码（从 1 开始）
            page_size: 每页数量

        Returns:
            分页的错题列表
        """
        query = db.query(WrongAnswerRecord).filter(
            WrongAnswerRecord.student_id == student_id
        )

        # 应用筛选条件
        if error_type:
            query = query.filter(WrongAnswerRecord.error_type == error_type)
        if is_resolved is not None:
            query = query.filter(WrongAnswerRecord.is_resolved == is_resolved)

        # 计算总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        wrong_answers = query.order_by(
            WrongAnswerRecord.created_at.desc()
        ).offset(offset).limit(page_size).all()

        # 转换为字典
        wrong_answers_data = []
        for wa in wrong_answers:
            wrong_answers_data.append({
                "id": wa.id,
                "student_id": wa.student_id,
                "question_content": wa.question_content,
                "student_answer": wa.student_answer,
                "correct_answer": wa.correct_answer,
                "error_type": wa.error_type,
                "is_resolved": wa.is_resolved,
                "attempts_count": wa.attempts_count,
                "created_at": wa.created_at.isoformat() if wa.created_at else None
            })

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "wrong_answers": wrong_answers_data
        }

    def get_wrong_answer_detail(
        self,
        db: Session,
        wrong_answer_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取错题详情

        Args:
            db: 数据库会话
            wrong_answer_id: 错题记录 ID

        Returns:
            错题详情，如果不存在则返回 None
        """
        wrong_answer = db.query(WrongAnswerRecord).filter(
            WrongAnswerRecord.id == wrong_answer_id
        ).first()

        if not wrong_answer:
            return None

        # 获取关联的学习记录
        learning_record = db.query(LearningRecord).filter(
            LearningRecord.id == wrong_answer.learning_record_id
        ).first()

        return {
            "id": wrong_answer.id,
            "student_id": wrong_answer.student_id,
            "question_content": wrong_answer.question_content,
            "student_answer": wrong_answer.student_answer,
            "correct_answer": wrong_answer.correct_answer,
            "error_type": wrong_answer.error_type,
            "guidance_type": wrong_answer.guidance_type,
            "guidance_content": wrong_answer.guidance_content,
            "is_resolved": wrong_answer.is_resolved,
            "attempts_count": wrong_answer.attempts_count,
            "last_attempt_at": wrong_answer.last_attempt_at.isoformat() if wrong_answer.last_attempt_at else None,
            "created_at": wrong_answer.created_at.isoformat() if wrong_answer.created_at else None
        }

    def update_wrong_answer_status(
        self,
        db: Session,
        wrong_answer_id: int,
        is_resolved: bool
    ) -> Dict[str, Any]:
        """
        更新错题状态

        Args:
            db: 数据库会话
            wrong_answer_id: 错题记录 ID
            is_resolved: 是否已解决

        Returns:
            更新后的错题信息
        """
        wrong_answer = db.query(WrongAnswerRecord).filter(
            WrongAnswerRecord.id == wrong_answer_id
        ).first()

        if not wrong_answer:
            return None

        wrong_answer.is_resolved = is_resolved
        if is_resolved:
            from datetime import datetime
            wrong_answer.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(wrong_answer)

        return {
            "id": wrong_answer.id,
            "is_resolved": wrong_answer.is_resolved,
            "resolved_at": wrong_answer.resolved_at.isoformat() if wrong_answer.resolved_at else None
        }

    def get_statistics(
        self,
        db: Session,
        student_id: int
    ) -> Dict[str, Any]:
        """
        获取错题统计

        Args:
            db: 数据库会话
            student_id: 学生 ID

        Returns:
            错题统计数据
        """
        # 获取所有错题
        wrong_answers = db.query(WrongAnswerRecord).filter(
            WrongAnswerRecord.student_id == student_id
        ).all()

        total = len(wrong_answers)
        resolved = sum(1 for wa in wrong_answers if wa.is_resolved)
        unresolved = total - resolved

        # 按错误类型分组
        by_error_type = {
            "calculation": 0,
            "concept": 0,
            "understanding": 0,
            "careless": 0
        }

        for wa in wrong_answers:
            if wa.error_type in by_error_type:
                by_error_type[wa.error_type] += 1

        # 找出最常见的错误类型
        most_common = sorted(
            by_error_type.items(),
            key=lambda x: x[1],
            reverse=True
        )
        most_common_errors = [k for k, v in most_common if v > 0]

        return {
            "student_id": student_id,
            "total_wrong_answers": total,
            "resolved_count": resolved,
            "unresolved_count": unresolved,
            "by_error_type": by_error_type,
            "most_common_errors": most_common_errors
        }

    def generate_recommendations(
        self,
        db: Session,
        student_id: int,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        生成练习推荐

        Args:
            db: 数据库会话
            student_id: 学生 ID
            limit: 推荐数量限制

        Returns:
            练习推荐列表
        """
        # 获取未解决的错题
        wrong_answers = db.query(WrongAnswerRecord).filter(
            WrongAnswerRecord.student_id == student_id,
            WrongAnswerRecord.is_resolved == False
        ).order_by(
            WrongAnswerRecord.attempts_count.desc(),
            WrongAnswerRecord.created_at.desc()
        ).limit(limit).all()

        if not wrong_answers:
            return {
                "student_id": student_id,
                "recommendations": [],
                "total_count": 0
            }

        # 按错误类型分组
        wrong_answers_by_type = self._get_wrong_answers_by_type(wrong_answers)

        # 生成推荐
        recommendations = []
        for error_type, answers in wrong_answers_by_type.items():
            # 生成相似题目
            similar_questions = []
            for wa in answers[:2]:  # 每种类型最多取 2 个
                similar = self._generate_similar_question(wa)
                if similar:
                    similar_questions.append(similar)

            # 确定优先级
            priority = self._determine_priority(error_type, len(answers))

            # 生成推荐理由
            reason = self._generate_reason(error_type, len(answers))

            recommendations.append({
                "priority": priority,
                "error_type": error_type,
                "similar_questions": similar_questions,
                "reason": reason
            })

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return {
            "student_id": student_id,
            "recommendations": recommendations[:limit],
            "total_count": len(recommendations)
        }

    def _get_wrong_answers_by_type(
        self,
        wrong_answers: List[WrongAnswerRecord]
    ) -> Dict[str, List[WrongAnswerRecord]]:
        """按错误类型分组错题"""
        grouped = {}
        for wa in wrong_answers:
            if wa.error_type not in grouped:
                grouped[wa.error_type] = []
            grouped[wa.error_type].append(wa)
        return grouped

    def _generate_similar_question(
        self,
        wrong_answer: WrongAnswerRecord
    ) -> Optional[Dict[str, Any]]:
        """
        生成相似题目

        基于原题目生成数字不同但类型相同的题目
        """
        import re

        question = wrong_answer.question_content

        # 提取题目中的数字
        numbers = re.findall(r'\d+', question)
        if len(numbers) < 2:
            return None

        # 生成新的数字（保持难度相似）
        n1, n2 = int(numbers[0]), int(numbers[1])

        # 简单的数字变换逻辑
        if wrong_answer.question_type == "addition":
            new_n1, new_n2 = max(1, n1 - 1), min(10, n2 + 1)
        elif wrong_answer.question_type == "subtraction":
            new_n1, new_n2 = max(5, n1 + 1), min(5, n2 - 1)
        else:
            new_n1, new_n2 = n1, n2

        # 替换数字生成新题目
        new_question = question
        new_question = new_question.replace(str(n1), str(new_n1), 1)
        new_question = new_question.replace(str(n2), str(new_n2), 1)

        return {
            "id": wrong_answer.id * 1000 + 1,  # 模拟 ID
            "question_content": new_question,
            "difficulty_level": wrong_answer.difficulty_level,
            "question_type": wrong_answer.question_type
        }

    def _determine_priority(self, error_type: str, count: int) -> str:
        """
        确定推荐优先级

        Args:
            error_type: 错误类型
            count: 该类型错题数量

        Returns:
            优先级：high/medium/low
        """
        if count >= 3:
            return "high"
        elif count >= 2:
            return "medium"
        else:
            return "low"

    def _generate_reason(self, error_type: str, count: int) -> str:
        """
        生成推荐理由

        Args:
            error_type: 错误类型
            count: 该类型错题数量

        Returns:
            推荐理由文本
        """
        reasons = {
            "calculation": f"该学生在计算中多次出错（{count}题），建议加强基础计算练习",
            "concept": f"该学生对概念理解有偏差（{count}题），建议巩固基础知识",
            "understanding": f"该学生对题意理解有误（{count}题），建议培养读题能力",
            "careless": f"该学生存在粗心问题（{count}题），建议养成检查习惯"
        }

        return reasons.get(error_type, f"该类型错误出现 {count} 次，建议针对性练习")
