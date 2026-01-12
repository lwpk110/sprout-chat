"""
SQLAlchemy 数据库模型

定义所有数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表（家长）"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))

    # 状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # 关系
    students = relationship("Student", back_populates="parent")


class Student(Base):
    """学生表（儿童）"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 基本信息
    name = Column(String(50), nullable=False)
    nickname = Column(String(50))
    age = Column(Integer, nullable=False)
    grade = Column(String(20))  # 年级
    avatar_url = Column(String(500))

    # 状态
    is_active = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    parent = relationship("User", back_populates="students")
    sessions = relationship("ConversationSession", back_populates="student")
    learning_records = relationship("LearningRecord", back_populates="student")
    progress = relationship("StudentProgress", back_populates="student")
    parental_controls = relationship("ParentalControl", back_populates="student")


class ConversationSession(Base):
    """对话会话表"""
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    # 会话信息
    subject = Column(String(50), default="数学")
    topic = Column(String(100))
    is_active = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)

    # 关系
    student = relationship("Student", back_populates="sessions")
    messages = relationship("ConversationMessage", back_populates="session")


class ConversationMessage(Base):
    """对话消息表"""
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False)

    # 消息内容
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # 元数据
    json_metadata = Column(JSON)  # 存储额外的对话信息

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("ConversationSession", back_populates="messages")


class LearningRecord(Base):
    """学习记录表（Phase 2.2 扩展）"""
    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(100), unique=True, index=True)
    session_id = Column(String(100), index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    # 问题信息
    question_content = Column(String(1000), nullable=False)  # 问题内容
    question_type = Column(String(50), nullable=False)  # 题目类型（addition, subtraction等）
    subject = Column(String(50), nullable=False, default="math")  # 科目
    difficulty_level = Column(Integer, default=1)  # 难度等级（1-5）
    problem_text = Column(Text)  # 保留兼容性
    problem_image_url = Column(String(500))
    problem_type = Column(String(50))  # 保留兼容性

    # 答案信息（Phase 2.2 新增）
    correct_answer = Column(String(500), nullable=False)  # 正确答案
    is_correct = Column(Boolean, nullable=False, index=True)  # 是否正确

    # 学生回答（加密存储）
    student_answer = Column(Text, nullable=False)  # TODO: 应用加密
    answer_result = Column(String(20), nullable=False)  # 保留兼容性（correct, incorrect, partial）
    attempts = Column(Integer, default=1)
    hints_used = Column(Integer, default=0)

    # 时间信息（Phase 2.2 优化）
    question_time = Column(DateTime, default=datetime.utcnow)
    answer_time = Column(DateTime)
    response_duration = Column(Float)  # 保留兼容性（秒）
    time_spent_seconds = Column(Integer, nullable=False)  # 答题耗时（秒）Phase 2.2

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 教学信息
    strategy_used = Column(String(100))
    metaphor_used = Column(String(50))

    # 元数据
    json_metadata = Column(JSON)

    # 关系
    student = relationship("Student", back_populates="learning_records")
    wrong_answer_record = relationship("WrongAnswerRecord", back_populates="learning_record", uselist=False)

    # 复合索引
    __table_args__ = (
        # TODO: Add composite index for (student_id, created_at) in Alembic migration
        # Index('idx_student_created', 'student_id', 'created_at'),
    )


class StudentProgress(Base):
    """学生进度表"""
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String(50), nullable=False)

    # 总体统计
    total_questions = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    total_incorrect = Column(Integer, default=0)
    total_partial = Column(Integer, default=0)

    # 按题型统计
    by_problem_type = Column(JSON)

    # 学习时长
    total_learning_time = Column(Float, default=0)  # 秒
    average_response_time = Column(Float, default=0)

    # 连续统计
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)

    # 掌握程度
    mastery_level = Column(JSON)

    # 时间范围
    first_activity = Column(DateTime)
    last_activity = Column(DateTime)

    # 时间戳
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    student = relationship("Student", back_populates="progress")


class ParentalControl(Base):
    """家长控制表"""
    __tablename__ = "parental_controls"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    # 时间限制
    time_restriction_type = Column(String(20))  # daily, weekly, per_session
    max_minutes = Column(Integer)
    allowed_start_time = Column(String(10))  # HH:MM
    allowed_end_time = Column(String(10))  # HH:MM
    allowed_days = Column(JSON)  # [0, 1, 2, 3, 4, 5, 6]

    # 难度设置
    difficulty_level = Column(String(20))  # easy, medium, hard, adaptive
    adaptive_enabled = Column(Boolean, default=True)

    # 内容过滤
    content_filters = Column(JSON)  # {"blocked": [], "limited": []}

    # 提醒设置
    reminder_before_end = Column(Integer, default=5)  # 分钟
    break_reminder = Column(Integer, default=20)  # 分钟
    break_duration = Column(Integer, default=10)  # 分钟

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    student = relationship("Student", back_populates="parental_controls")


class Problem(Base):
    """题目表"""
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(String(100), unique=True, index=True)

    # 科目和题型
    subject = Column(String(50), nullable=False)
    problem_type = Column(String(50), nullable=False)

    # 题目内容
    content = Column(Text, nullable=False)
    options = Column(JSON)  # 选择题选项
    correct_answer = Column(String(200), nullable=False)
    explanation = Column(Text)  # 解析

    # 难度和标签
    difficulty = Column(String(20), default="简单")  # 简单、中等、困难
    grade = Column(String(20))  # 适合年级

    # 知识点
    knowledge_points = Column(JSON)
    tags = Column(JSON)

    # 多媒体
    image_url = Column(String(500))
    audio_url = Column(String(500))

    # 状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 创建者
    created_by = Column(String(50))

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =============================================================================
# Phase 2.2: Learning Management Models
# =============================================================================

class WrongAnswerRecord(Base):
    """错题记录表（Phase 2.2）"""
    __tablename__ = "wrong_answer_records"

    id = Column(Integer, primary_key=True, index=True)
    learning_record_id = Column(Integer, ForeignKey("learning_records.id"), unique=True, nullable=False, index=True)

    # 错误分类
    error_type = Column(String(50), nullable=False, index=True)  # calculation, concept, understanding, careless

    # 引导式反馈
    guidance_type = Column(String(50), nullable=False)  # clarify, hint, break_down, visualize, check_work, alternative_method, encourage
    guidance_content = Column(Text, nullable=False)  # 引导式反馈内容

    # 解决状态
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    learning_record = relationship("LearningRecord", back_populates="wrong_answer_record")


class KnowledgePoint(Base):
    """知识点表（Phase 2.2）"""
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)

    # 分类
    subject = Column(String(50), nullable=False, index=True)  # math, chinese, english
    difficulty_level = Column(Integer, nullable=False)  # 1-5

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系（自引用多对多：前置知识点）
    prerequisites = relationship(
        "KnowledgePoint",
        secondary="knowledge_point_dependencies",
        primaryjoin="KnowledgePoint.id == KnowledgePointDependency.knowledge_point_id",
        secondaryjoin="KnowledgePoint.id == KnowledgePointDependency.prerequisite_id",
        backref="dependents"
    )


class KnowledgeMastery(Base):
    """知识点掌握表（Phase 2.2）"""
    __tablename__ = "knowledge_mastery"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False, index=True)

    # 掌握度
    mastery_percentage = Column(Integer, nullable=False)  # 0-100
    questions_practiced = Column(Integer, default=0, nullable=False)
    questions_correct = Column(Integer, default=0, nullable=False)
    recent_performance = Column(Integer)  # 最近表现（最近10题的正确率，0-100）

    # 掌握状态
    mastery_status = Column(String(50), default="not_started", nullable=False, index=True)  # not_started, learning, mastered

    # 时间信息
    last_practiced_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 复合索引
    __table_args__ = (
        # TODO: Add unique constraint for (student_id, knowledge_point_id) in Alembic migration
        # UniqueConstraint('student_id', 'knowledge_point_id', name='uq_student_knowledge'),
    )


class KnowledgePointDependency(Base):
    """知识点依赖关系表（Phase 2.2）"""
    __tablename__ = "knowledge_point_dependencies"

    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey("knowledge_points.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# 数据库会话管理
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 使用 SQLite 开发，生产环境应使用 PostgreSQL
engine = create_engine(
    "sqlite:///./sprout_chat.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
