"""
知识点追踪服务（Phase 2.2 - US4）

实现知识点图谱的建立、掌握度追踪和学习路径推荐功能。
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import (
    KnowledgePoint, KnowledgePointMastery, LearningRecord
)


class KnowledgeTrackerService:
    """
    知识点追踪服务

    追踪学生对各个知识点的掌握程度，生成学习路径推荐。
    """

    def __init__(self):
        """初始化知识点追踪服务"""
        pass

    def get_knowledge_points(
        self,
        db: Session,
        subject: Optional[str] = None,
        difficulty_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取知识点列表

        Args:
            db: 数据库会话
            subject: 科目筛选（可选）
            difficulty_level: 难度筛选（可选）

        Returns:
            知识点列表
        """
        query = db.query(KnowledgePoint)

        if subject:
            query = query.filter(KnowledgePoint.subject == subject)
        if difficulty_level:
            query = query.filter(KnowledgePoint.difficulty_level == difficulty_level)

        knowledge_points = query.order_by(
            KnowledgePoint.difficulty_level,
            KnowledgePoint.name
        ).all()

        # 转换为字典
        kp_data = []
        for kp in knowledge_points:
            kp_data.append({
                "id": kp.id,
                "name": kp.name,
                "subject": kp.subject,
                "difficulty_level": kp.difficulty_level,
                "description": kp.description,
                "parent_id": kp.parent_id
            })

        return {
            "total": len(kp_data),
            "knowledge_points": kp_data
        }

    def get_knowledge_point_detail(
        self,
        db: Session,
        knowledge_point_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取知识点详情

        Args:
            db: 数据库会话
            knowledge_point_id: 知识点 ID

        Returns:
            知识点详情，如果不存在则返回 None
        """
        kp = db.query(KnowledgePoint).filter(
            KnowledgePoint.id == knowledge_point_id
        ).first()

        if not kp:
            return None

        # 获取前置知识点
        prerequisites = []
        if kp.prerequisites:
            for prereq in kp.prerequisites:
                prerequisites.append({
                    "id": prereq.id,
                    "name": prereq.name
                })

        # 获取子知识点
        children = db.query(KnowledgePoint).filter(
            KnowledgePoint.parent_id == knowledge_point_id
        ).all()

        children_data = []
        for child in children:
            children_data.append({
                "id": child.id,
                "name": child.name
            })

        return {
            "id": kp.id,
            "name": kp.name,
            "subject": kp.subject,
            "difficulty_level": kp.difficulty_level,
            "description": kp.description,
            "parent_id": kp.parent_id,
            "prerequisites": prerequisites,
            "children": children_data
        }

    def get_knowledge_graph(
        self,
        db: Session,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取知识点图谱（DAG 结构）

        Args:
            db: 数据库会话
            subject: 科目筛选（可选）

        Returns:
            知识点图谱（节点和边）
        """
        query = db.query(KnowledgePoint)
        if subject:
            query = query.filter(KnowledgePoint.subject == subject)

        knowledge_points = query.all()

        # 构建节点
        nodes = []
        for kp in knowledge_points:
            nodes.append({
                "id": kp.id,
                "name": kp.name,
                "subject": kp.subject,
                "difficulty_level": kp.difficulty_level
            })

        # 构建边（前置知识点的依赖关系）
        edges = []
        for kp in knowledge_points:
            if kp.prerequisites:
                for prereq in kp.prerequisites:
                    edges.append({
                        "from": prereq.id,  # 从对象中提取 ID
                        "to": kp.id,
                        "type": "prerequisite"
                    })

            # 如果有父知识点，添加关系边
            if kp.parent_id:
                edges.append({
                    "from": kp.parent_id,
                    "to": kp.id,
                    "type": "parent_child"
                })

        return {
            "nodes": nodes,
            "edges": edges
        }

    def get_student_mastery(
        self,
        db: Session,
        student_id: int,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取学生的知识点掌握情况

        Args:
            db: 数据库会话
            student_id: 学生 ID
            subject: 科目筛选（可选）

        Returns:
            知识点掌握情况
        """
        # 获取该学生的所有掌握记录
        query = db.query(KnowledgePointMastery).filter(
            KnowledgePointMastery.student_id == student_id
        )

        # 如果指定科目，需要关联知识点表
        if subject:
            query = query.join(KnowledgePoint).filter(
                KnowledgePoint.subject == subject
            )

        mastery_records = query.all()

        # 统计各状态数量
        mastered_count = sum(1 for m in mastery_records if m.mastery_percentage >= 80)
        in_progress_count = sum(1 for m in mastery_records if 40 <= m.mastery_percentage < 80)
        not_started_count = sum(1 for m in mastery_records if m.mastery_percentage < 40)

        # 转换为字典
        mastery_data = []
        for m in mastery_records:
            kp = db.query(KnowledgePoint).filter(
                KnowledgePoint.id == m.knowledge_point_id
            ).first()

            # 确定状态
            if m.mastery_percentage >= 80:
                status = "mastered"
            elif m.mastery_percentage >= 40:
                status = "in_progress"
            else:
                status = "not_started"

            mastery_data.append({
                "id": m.id,
                "knowledge_point_id": m.knowledge_point_id,
                "knowledge_point_name": kp.name if kp else "未知",
                "mastery_percentage": m.mastery_percentage,
                "status": status,
                "last_updated": m.updated_at.isoformat() if m.updated_at else None
            })

        return {
            "student_id": student_id,
            "total_points": len(mastery_records),
            "mastered_count": mastered_count,
            "in_progress_count": in_progress_count,
            "not_started_count": not_started_count,
            "mastery_records": mastery_data
        }

    def update_mastery(
        self,
        db: Session,
        student_id: int,
        knowledge_point_id: int,
        mastery_percentage: float
    ) -> Dict[str, Any]:
        """
        更新知识点掌握度

        Args:
            db: 数据库会话
            student_id: 学生 ID
            knowledge_point_id: 知识点 ID
            mastery_percentage: 掌握度百分比（0-100）

        Returns:
            更新后的掌握记录
        """
        # 查找现有记录
        mastery = db.query(KnowledgePointMastery).filter(
            KnowledgePointMastery.student_id == student_id,
            KnowledgePointMastery.knowledge_point_id == knowledge_point_id
        ).first()

        # 确定状态
        if mastery_percentage >= 80:
            status = "mastered"
        elif mastery_percentage >= 40:
            status = "in_progress"
        else:
            status = "not_started"

        if mastery:
            # 更新现有记录
            mastery.mastery_percentage = mastery_percentage
            mastery.status = status
            mastery.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            mastery = KnowledgePointMastery(
                student_id=student_id,
                knowledge_point_id=knowledge_point_id,
                mastery_percentage=mastery_percentage,
                status=status,
                updated_at=datetime.utcnow()
            )
            db.add(mastery)

        db.commit()
        db.refresh(mastery)

        return {
            "id": mastery.id,
            "student_id": mastery.student_id,
            "knowledge_point_id": mastery.knowledge_point_id,
            "mastery_percentage": mastery.mastery_percentage,
            "status": mastery.status
        }

    def generate_learning_path(
        self,
        db: Session,
        student_id: int,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成学习路径推荐

        Args:
            db: 数据库会话
            student_id: 学生 ID
            subject: 科目筛选（可选）

        Returns:
            推荐的学习路径
        """
        # 获取所有知识点
        query = db.query(KnowledgePoint)
        if subject:
            query = query.filter(KnowledgePoint.subject == subject)
        knowledge_points = query.all()

        # 获取学生的掌握情况
        student_mastery = db.query(KnowledgePointMastery).filter(
            KnowledgePointMastery.student_id == student_id
        ).all()

        # 构建掌握度映射
        mastery_map = {}
        for m in student_mastery:
            mastery_map[m.knowledge_point_id] = m.mastery_percentage

        # 为每个知识点生成推荐
        recommendations = []
        for kp in knowledge_points:
            # 检查前置知识点是否已掌握
            prerequisites_met = self.check_prerequisites_met(
                kp, mastery_map
            )

            # 确定推荐理由
            if prerequisites_met:
                reason = "前置知识点已掌握，可以开始学习"
            elif kp.prerequisites:
                reason = f"需要先掌握 {len(kp.prerequisites)} 个前置知识点"
            else:
                reason = "基础知识点，可以直接开始学习"

            recommendations.append({
                "order": kp.difficulty_level,  # 按难度排序
                "knowledge_point": {
                    "id": kp.id,
                    "name": kp.name,
                    "difficulty_level": kp.difficulty_level
                },
                "prerequisites_met": prerequisites_met,
                "reason": reason
            })

        # 按难度和前置知识点是否满足排序
        recommendations.sort(key=lambda x: (
            0 if x["prerequisites_met"] else 1,  # 前置满足的在前
            x["order"]  # 难度低的在前
        ))

        return {
            "student_id": student_id,
            "recommended_path": recommendations
        }

    def calculate_mastery_percentage(
        self,
        db: Session,
        student_id: int,
        knowledge_point_id: int
    ) -> float:
        """
        计算知识点掌握度

        掌握度计算公式：
        - 最近表现 40%
        - 历史表现 40%
        - 连续答对 20%

        Args:
            db: 数据库会话
            student_id: 学生 ID
            knowledge_point_id: 知识点 ID

        Returns:
            掌握度百分比（0-100）
        """
        # 获取该知识点的所有学习记录
        learning_records = db.query(LearningRecord).filter(
            LearningRecord.student_id == student_id,
            LearningRecord.knowledge_point_id == knowledge_point_id
        ).order_by(LearningRecord.created_at.desc()).all()

        if not learning_records:
            return 0.0

        total_records = len(learning_records)

        # 最近表现（最近 10 次）
        recent_records = learning_records[:min(10, total_records)]
        if recent_records:
            recent_correct = sum(1 for r in recent_records if r.is_correct)
            recent_score = (recent_correct / len(recent_records)) * 100
        else:
            recent_score = 0.0

        # 历史表现（总正确率）
        total_correct = sum(1 for r in learning_records if r.is_correct)
        historical_score = (total_correct / total_records) * 100

        # 连续答对（从最新记录开始计数）
        streak = 0
        for record in learning_records:
            if record.is_correct:
                streak += 1
            else:
                break

        streak_score = min(streak * 10, 100)  # 最多 100 分

        # 加权计算
        mastery_percentage = (
            recent_score * 0.4 +
            historical_score * 0.4 +
            streak_score * 0.2
        )

        return round(mastery_percentage, 2)

    def check_prerequisites_met(
        self,
        knowledge_point: KnowledgePoint,
        mastery_map: Dict[int, float]
    ) -> bool:
        """
        检查前置知识点是否已掌握

        Args:
            knowledge_point: 知识点对象
            mastery_map: 知识点掌握度映射

        Returns:
            前置知识点是否已掌握
        """
        if not knowledge_point.prerequisites:
            return True

        # 检查所有前置知识点掌握度 >= 80%
        for prereq in knowledge_point.prerequisites:
            prereq_id = prereq.id  # 从对象中提取 ID
            mastery = mastery_map.get(prereq_id, 0)
            if mastery < 80:
                return False

        return True
