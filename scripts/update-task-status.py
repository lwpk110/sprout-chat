#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新 Taskmaster 任务状态

根据代码完成情况更新任务状态
"""

import json
from pathlib import Path

# 配置
TASKMASTER_FILE = Path("/home/luwei/workspace/github/sprout-chat/.taskmaster/tasks/tasks.json")
TASKMASTER_TAG = "learning-management"

# 已完成的任务列表（基于代码分析）
COMPLETED_TASKS = [
    "LWP-2.2-T002",  # 安装 Python 依赖包
    "LWP-2.2-T004",  # 创建学习记录扩展模型
    "LWP-2.2-T005",  # 创建错题记录模型
    "LWP-2.2-T006",  # 创建知识点模型
    "LWP-2.2-T007",  # 创建知识点掌握模型
    "LWP-2.2-T008",  # 创建知识点依赖关系模型
    "LWP-2.2-T012",  # 扩展学习记录 API 端点
    "LWP-2.2-T013",  # 实现学习追踪服务
    "LWP-2.2-T014",  # 编写学习记录集成测试
    "LWP-2.2-T021",  # 编写苏格拉底教学服务测试
    "LWP-2.2-T022",  # 实现错误答案分类器
    "LWP-2.2-T023",  # 实现响应验证系统
    "LWP-2.2-T024",  # 集成 Claude API 生成引导式响应
    "LWP-2.2-T025",  # 实现引导教学 API 端点
    "LWP-2.2-T026",  # 编写引导教学集成测试
    "LWP-2.2-T031",  # 编写错题本 API 测试
    "LWP-2.2-T032",  # 实现练习推荐服务
    "LWP-2.2-T033",  # 实现错题本 API 端点
    "LWP-2.2-T041",  # 编写知识点图谱 API 测试
    "LWP-2.2-T042",  # 实现知识点追踪服务
    "LWP-2.2-T043",  # 实现知识点图谱 API 端点
]

def main():
    """批量更新任务状态"""
    print("=" * 70)
    print("Taskmaster 任务状态批量更新工具")
    print("=" * 70)
    print()

    # 1. 加载 Taskmaster 数据
    print(f"[INFO] 加载 Taskmaster 数据: {TASKMASTER_FILE}")
    with open(TASKMASTER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if TASKMASTER_TAG not in data:
        print(f"[ERROR] Tag '{TASKMASTER_TAG}' 不存在")
        return 1

    tasks = data[TASKMASTER_TAG]["tasks"]
    print(f"[INFO] 已加载 {len(tasks)} 个任务")
    print()

    # 2. 更新任务状态
    updated_count = 0
    for task in tasks:
        if task["id"] in COMPLETED_TASKS and task["status"] != "done":
            old_status = task["status"]
            task["status"] = "done"
            print(f"✅ {task['id']}: {old_status} → done")
            updated_count += 1

    print()
    print(f"[INFO] 已更新 {updated_count} 个任务状态")
    print()

    # 3. 保存更新
    print("[INFO] 保存更新...")
    with open(TASKMASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 已保存到 {TASKMASTER_FILE}")
    print()

    # 4. 统计信息
    done_count = sum(1 for t in tasks if t["status"] == "done")
    pending_count = sum(1 for t in tasks if t["status"] == "pending")
    progress = (done_count / len(tasks)) * 100 if tasks else 0

    print("=" * 70)
    print("更新后统计")
    print("=" * 70)
    print(f"总任务数: {len(tasks)}")
    print(f"✅ 已完成: {done_count} ({progress:.1f}%)")
    print(f"⭕ 待办: {pending_count} ({100-progress:.1f}%)")
    print("=" * 70)
    print()

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
