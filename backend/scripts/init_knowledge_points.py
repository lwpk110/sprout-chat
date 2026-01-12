"""
Phase 2.2 知识点初始化脚本

生成一年级数学的核心知识点（至少 20 个）
建立知识点之间的依赖关系（DAG）
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.database import SessionLocal, KnowledgePoint, KnowledgePointDependency


# 一年级数学知识点定义
KNOWLEDGE_POINTS = [
    # 基础知识（难度 1）
    {"name": "10以内数的认识", "subject": "math", "difficulty_level": 1, "description": "认识0-10的数字，理解数的含义"},
    {"name": "10以内数的比较", "subject": "math", "difficulty_level": 1, "description": "会比较10以内数的大小"},
    {"name": "10以内数的组成", "subject": "math", "difficulty_level": 1, "description": "理解10以内数的分解和组成"},

    # 10以内加减法（难度 2）
    {"name": "10以内加法", "subject": "math", "difficulty_level": 2, "description": "掌握10以内数的加法运算"},
    {"name": "10以内减法", "subject": "math", "difficulty_level": 2, "description": "掌握10以内数的减法运算"},
    {"name": "10以内加减法混合运算", "subject": "math", "difficulty_level": 2, "description": "10以内加减法综合练习"},

    # 20以内数（难度 2）
    {"name": "20以内数的认识", "subject": "math", "difficulty_level": 2, "description": "认识11-20的数字"},
    {"name": "20以内数的比较", "subject": "math", "difficulty_level": 2, "description": "会比较20以内数的大小"},

    # 20以内加减法（难度 3）
    {"name": "20以内进位加法", "subject": "math", "difficulty_level": 3, "description": "掌握20以内的进位加法"},
    {"name": "20以内退位减法", "subject": "math", "difficulty_level": 3, "description": "掌握20以内的退位减法"},
    {"name": "20以内加减法混合运算", "subject": "math", "difficulty_level": 3, "description": "20以内加减法综合练习"},

    # 100以内数（难度 3）
    {"name": "100以内数的认识", "subject": "math", "difficulty_level": 3, "description": "认识100以内的数字"},
    {"name": "100以内数的比较", "subject": "math", "difficulty_level": 3, "description": "会比较100以内数的大小"},

    # 100以内加减法（难度 4）
    {"name": "100以内不进位加法", "subject": "math", "difficulty_level": 4, "description": "掌握100以内不进位加法"},
    {"name": "100以内不退位减法", "subject": "math", "difficulty_level": 4, "description": "掌握100以内不退位减法"},
    {"name": "100以内进位加法", "subject": "math", "difficulty_level": 4, "description": "掌握100以内的进位加法"},
    {"name": "100以内退位减法", "subject": "math", "difficulty_level": 4, "description": "掌握100以内的退位减法"},

    # 乘法基础（难度 4-5）
    {"name": "乘法的意义", "subject": "math", "difficulty_level": 4, "description": "理解乘法是相同数连加的简便运算"},
    {"name": "2-5的乘法口诀", "subject": "math", "difficulty_level": 4, "description": "掌握2-5的乘法口诀"},
    {"name": "6-9的乘法口诀", "subject": "math", "difficulty_level": 5, "description": "掌握6-9的乘法口诀"},
    {"name": "表内乘法", "subject": "math", "difficulty_level": 5, "description": "掌握乘法表内的乘法运算"},
]

# 知识点依赖关系（前置知识点）
# 格式：(知识点名称, [前置知识点列表])
KNOWLEDGE_DEPENDENCIES = [
    # 10以内加减法依赖：10以内数的认识、组成
    ("10以内数的比较", ["10以内数的认识"]),
    ("10以内数的组成", ["10以内数的认识"]),
    ("10以内加法", ["10以内数的认识", "10以内数的组成"]),
    ("10以内减法", ["10以内数的认识", "10以内数的组成"]),
    ("10以内加减法混合运算", ["10以内加法", "10以内减法"]),

    # 20以内数依赖：10以内数的基础
    ("20以内数的认识", ["10以内数的认识"]),
    ("20以内数的比较", ["10以内数的比较", "20以内数的认识"]),

    # 20以内加减法依赖：10以内加减法、20以内数的认识
    ("20以内进位加法", ["10以内加法", "20以内数的认识"]),
    ("20以内退位减法", ["10以内减法", "20以内数的认识"]),
    ("20以内加减法混合运算", ["20以内进位加法", "20以内退位减法"]),

    # 100以内数依赖：20以内数的基础
    ("100以内数的认识", ["20以内数的认识"]),
    ("100以内数的比较", ["20以内数的比较", "100以内数的认识"]),

    # 100以内加减法依赖：20以内加减法、100以内数的认识
    ("100以内不进位加法", ["10以内加法", "100以内数的认识"]),
    ("100以内不退位减法", ["10以内减法", "100以内数的认识"]),
    ("100以内进位加法", ["20以内进位加法", "100以内数的认识"]),
    ("100以内退位减法", ["20以内退位减法", "100以内数的认识"]),

    # 乘法依赖：加法基础
    ("乘法的意义", ["10以内加法"]),
    ("2-5的乘法口诀", ["乘法的意义", "10以内加法"]),
    ("6-9的乘法口诀", ["2-5的乘法口诀"]),
    ("表内乘法", ["2-5的乘法口诀", "6-9的乘法口诀"]),
]


def create_knowledge_points():
    """创建知识点"""
    print(f"Creating {len(KNOWLEDGE_POINTS)} knowledge points...")

    db = SessionLocal()
    try:
        # 创建知识点
        for kp_data in KNOWLEDGE_POINTS:
            # 检查是否已存在
            existing = db.query(KnowledgePoint).filter(KnowledgePoint.name == kp_data["name"]).first()
            if existing:
                print(f"  ⏭️  Skipping existing: {kp_data['name']}")
                continue

            knowledge_point = KnowledgePoint(**kp_data)
            db.add(knowledge_point)
            print(f"  ✅ Created: {kp_data['name']}")

        db.commit()
        print(f"\n✅ Knowledge points created successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating knowledge points: {e}")
        raise
    finally:
        db.close()


def create_knowledge_dependencies():
    """创建知识点依赖关系"""
    print(f"\nCreating knowledge point dependencies...")

    db = SessionLocal()
    try:
        for kp_name, prerequisite_names in KNOWLEDGE_DEPENDENCIES:
            # 查找知识点
            knowledge_point = db.query(KnowledgePoint).filter(KnowledgePoint.name == kp_name).first()
            if not knowledge_point:
                print(f"  ⚠️  Knowledge point not found: {kp_name}")
                continue

            # 创建依赖关系
            for prereq_name in prerequisite_names:
                prerequisite = db.query(KnowledgePoint).filter(KnowledgePoint.name == prereq_name).first()
                if not prerequisite:
                    print(f"  ⚠️  Prerequisite not found: {prereq_name}")
                    continue

                # 检查是否已存在
                existing = db.query(KnowledgePointDependency).filter(
                    KnowledgePointDependency.knowledge_point_id == knowledge_point.id,
                    KnowledgePointDependency.prerequisite_id == prerequisite.id
                ).first()

                if existing:
                    continue

                dependency = KnowledgePointDependency(
                    knowledge_point_id=knowledge_point.id,
                    prerequisite_id=prerequisite.id
                )
                db.add(dependency)
                print(f"  ✅ {kp_name} ← {prereq_name}")

        db.commit()
        print(f"\n✅ Knowledge dependencies created successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating dependencies: {e}")
        raise
    finally:
        db.close()


def verify_knowledge_points():
    """验证知识点数据"""
    print("\nVerifying knowledge points...")

    db = SessionLocal()
    try:
        # 统计知识点
        count = db.query(KnowledgePoint).count()
        print(f"\n  Total knowledge points: {count}")

        # 按科目统计
        math_count = db.query(KnowledgePoint).filter(KnowledgePoint.subject == "math").count()
        print(f"  Math knowledge points: {math_count}")

        # 按难度统计
        for level in range(1, 6):
            level_count = db.query(KnowledgePoint).filter(
                KnowledgePoint.subject == "math",
                KnowledgePoint.difficulty_level == level
            ).count()
            print(f"  Difficulty {level}: {level_count} points")

        # 统计依赖关系
        dep_count = db.query(KnowledgePointDependency).count()
        print(f"  Total dependencies: {dep_count}")

        # 验证成功
        if count >= 20 and math_count >= 20:
            print("\n  ✅ Knowledge points verification passed!")
            return True
        else:
            print(f"\n  ⚠️  Expected at least 20 knowledge points, got {count}")
            return False

    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 60)
    print("Phase 2.2 Knowledge Points Initialization")
    print("=" * 60)

    # 创建知识点
    create_knowledge_points()

    # 创建依赖关系
    create_knowledge_dependencies()

    # 验证知识点
    success = verify_knowledge_points()

    if success:
        print("\n" + "=" * 60)
        print("✅ Knowledge points initialization completed successfully!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Knowledge points initialization failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
