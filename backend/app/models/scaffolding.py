"""
脚手架层级持久化数据模型 (LWP-15)

定义脚手架层级和表现指标的数据库表结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.database import Base
from app.models.socratic import ScaffoldingLevel


class ScaffoldingLevelRecord(Base):
    """学生脚手架层级记录表"""
    __tablename__ = "scaffolding_levels"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    problem_domain = Column(String(50), nullable=False, index=True, default="general")  # math, reading, general
    level = Column(SQLEnum(ScaffoldingLevel), nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    student = relationship("Student", foreign_keys=[student_id])

    # 复合索引
    __table_args__ = (
        Index('idx_student_domain_updated', 'student_id', 'problem_domain', 'updated_at'),
    )

    def __repr__(self):
        return f"<ScaffoldingLevelRecord(student_id={self.student_id}, domain={self.problem_domain}, level={self.level.value})>"


class PerformanceMetric(Base):
    """学生表现指标表"""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    conversation_id = Column(String(100), ForeignKey("conversation_sessions.session_id"), index=True)
    problem_domain = Column(String(50), nullable=False, index=True, default="general")  # math, reading, general

    # 表现指标
    is_correct = Column(Boolean, nullable=False, index=True)
    hints_needed = Column(Integer, default=0)
    response_time_seconds = Column(Float)
    self_corrected = Column(Boolean, default=False)

    # 上下文信息
    scaffolding_level_at_time = Column(SQLEnum(ScaffoldingLevel), nullable=False)
    question_type = Column(String(50))  # addition, subtraction, reading_comprehension, etc.

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    student = relationship("Student", foreign_keys=[student_id])

    # 复合索引
    __table_args__ = (
        Index('idx_student_domain_created', 'student_id', 'problem_domain', 'created_at'),
    )

    def __repr__(self):
        return f"<PerformanceMetric(student_id={self.student_id}, correct={self.is_correct}, hints={self.hints_needed})>"
