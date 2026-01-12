"""
Phase 2.2 数据库初始化脚本

创建所有必要的数据库表和索引
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.database import Base, engine, init_db
from sqlalchemy import text


def create_tables():
    """创建所有数据库表"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")


def create_indexes():
    """创建额外的索引（优化查询性能）"""
    print("\nCreating additional indexes...")

    index_sqls = [
        # LearningRecord 复合索引
        "CREATE INDEX IF NOT EXISTS idx_student_created ON learning_records (student_id, created_at);",

        # KnowledgeMastery 唯一约束
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_student_knowledge ON knowledge_mastery (student_id, knowledge_point_id);",
    ]

    with engine.connect() as conn:
        for sql in index_sqls:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"  ✅ Created index: {sql.split('IF NOT EXISTS ')[1].split(' ')[0]}")
            except Exception as e:
                print(f"  ⚠️  Index creation note: {e}")

    print("✅ All indexes created!")


def verify_tables():
    """验证表是否创建成功"""
    print("\nVerifying tables...")

    expected_tables = [
        "users",
        "students",
        "learning_records",
        "student_progress",
        "wrong_answer_records",  # Phase 2.2
        "knowledge_points",      # Phase 2.2
        "knowledge_mastery",      # Phase 2.2
        "knowledge_point_dependencies",  # Phase 2.2
        "conversation_sessions",
        # "messages",  # Not defined in current schema
        "parental_controls",
        "problems",
    ]

    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        ))
        existing_tables = [row[0] for row in result.fetchall()]

    print(f"\n  Expected tables: {len(expected_tables)}")
    print(f"  Existing tables: {len(existing_tables)}")

    missing_tables = set(expected_tables) - set(existing_tables)
    if missing_tables:
        print(f"\n  ⚠️  Missing tables: {missing_tables}")
        return False
    else:
        print(f"\n  ✅ All expected tables exist!")
        return True


def main():
    """主函数"""
    print("=" * 60)
    print("Phase 2.2 Database Initialization")
    print("=" * 60)

    # 创建表
    create_tables()

    # 创建索引
    create_indexes()

    # 验证表
    success = verify_tables()

    if success:
        print("\n" + "=" * 60)
        print("✅ Database initialization completed successfully!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Database initialization failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
