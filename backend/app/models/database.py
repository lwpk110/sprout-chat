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
    """学习记录表"""
    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(100), unique=True, index=True)
    session_id = Column(String(100), index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    # 问题信息
    subject = Column(String(50), nullable=False)
    problem_type = Column(String(50), nullable=False)
    problem_text = Column(Text, nullable=False)
    problem_image_url = Column(String(500))

    # 学生回答
    student_answer = Column(Text, nullable=False)
    answer_result = Column(String(20), nullable=False)  # correct, incorrect, partial
    attempts = Column(Integer, default=1)
    hints_used = Column(Integer, default=0)

    # 时间信息
    question_time = Column(DateTime, default=datetime.utcnow)
    answer_time = Column(DateTime)
    response_duration = Column(Float)  # 秒

    # 教学信息
    strategy_used = Column(String(100))
    metaphor_used = Column(String(50))

    # 元数据
    json_metadata = Column(JSON)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    student = relationship("Student", back_populates="learning_records")


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
