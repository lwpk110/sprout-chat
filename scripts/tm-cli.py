#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taskmaster CLI 增强工具

提供 visualize 和 stats 命令，增强 Taskmaster 的功能

命令：
- tm-cli visualize: 显示任务树形图
- tm-cli stats: 显示任务进度统计

作者: Claude (Sonnet 4.5)
日期: 2026-01-15
版本: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter

# ==================== 配置 ====================

PROJECT_ROOT = Path("/home/luwei/workspace/github/sprout-chat")
TASKMASTER_FILE = PROJECT_ROOT / ".taskmaster/tasks/tasks.json"
TASKMASTER_TAG = "learning-management"

# ==================== Taskmaster 数据加载器 ====================

class TaskmasterLoader:
    """Taskmaster 数据加载器"""

    def __init__(self, taskmaster_file: Path, tag: str = TASKMASTER_TAG):
        self.taskmaster_file = taskmaster_file
        self.tag = tag
        self.tasks = []

    def load(self) -> bool:
        """加载任务"""
        if not self.taskmaster_file.exists():
            print(f"[ERROR] Taskmaster 文件不存在: {self.taskmaster_file}")
            return False

        try:
            with open(self.taskmaster_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if self.tag in data:
                self.tasks = data[self.tag]["tasks"]
                print(f"[INFO] 已加载 {len(self.tasks)} 个任务（Tag: {self.tag}）")
                return True
            else:
                print(f"[ERROR] Tag '{self.tag}' 不存在")
                print(f"[INFO] 可用 tags: {', '.join(data.keys())}")
                return False

        except Exception as e:
            print(f"[ERROR] 加载失败: {e}")
            return False


# ==================== Visualize 命令 ====================

class TaskVisualizer:
    """任务可视化器"""

    def __init__(self, tasks: List[Dict]):
        self.tasks = tasks
        self.task_map = {task["id"]: task for task in tasks}

    def build_tree(self) -> List[Dict]:
        """构建任务树"""
        # 按依赖关系排序
        visited = set()
        tree = []

        def visit(task_id: str, depth: int = 0):
            if task_id in visited:
                return

            visited.add(task_id)

            if task_id in self.task_map:
                task = self.task_map[task_id]
                tree.append({
                    "task": task,
                    "depth": depth,
                    "has_children": len(task.get("dependencies", [])) > 0
                })

                # 递归访问依赖任务
                for dep_id in task.get("dependencies", []):
                    visit(dep_id, depth + 1)

        # 从所有任务开始构建
        for task in self.tasks:
            visit(task["id"])

        return tree

    def render_tree(self, tree: List[Dict]) -> str:
        """渲染树形图"""
        lines = []

        for i, item in enumerate(tree):
            task = item["task"]
            depth = item["depth"]

            # 构建前缀
            if depth == 0:
                prefix = "└─ " if i > 0 else "└─ "
            else:
                prefix = "  " * (depth - 1) + "└─ "

            # 构建状态图标
            status = task.get("status", "pending")
            status_icons = {
                "pending": "⭕",
                "in-progress": "🔄",
                "done": "✅",
                "blocked": "🚫",
                "cancelled": "❌",
                "deferred": "⏸️",
                "review": "👀"
            }
            icon = status_icons.get(status, "❓")

            # 构建行
            line = f"{prefix}{icon} {task['id']}: {task['title']}"

            # 添加优先级
            if task.get("priority"):
                priority = task["priority"]
                if priority == "high":
                    line += " 🔥"
                elif priority == "medium":
                    line += " 🟡"
                elif priority == "low":
                    line += " 🟢"

            lines.append(line)

        return "\n".join(lines)

    def visualize(self) -> str:
        """生成可视化输出"""
        tree = self.build_tree()
        return self.render_tree(tree)


# ==================== Stats 命令 ====================

class TaskStats:
    """任务统计器"""

    def __init__(self, tasks: List[Dict]):
        self.tasks = tasks

    def calculate_stats(self) -> Dict:
        """计算统计数据"""
        total = len(self.tasks)

        # 按状态统计
        status_counter = Counter(task.get("status", "pending") for task in self.tasks)

        # 按优先级统计
        priority_counter = Counter(task.get("priority", "medium") for task in self.tasks)

        # 计算进度
        done = status_counter.get("done", 0)
        in_progress = status_counter.get("in-progress", 0)
        progress = (done + in_progress * 0.5) / total * 100 if total > 0 else 0

        # Spec-Kit 元信息统计
        phases = Counter()
        user_stories = Counter()

        for task in self.tasks:
            metadata = task.get("metadata", {})
            if metadata.get("phase"):
                phases[metadata["phase"]] += 1
            if metadata.get("user_story"):
                user_stories[metadata["user_story"]] += 1

        return {
            "total": total,
            "status": dict(status_counter),
            "priority": dict(priority_counter),
            "progress": round(progress, 2),
            "phases": dict(phases),
            "user_stories": dict(user_stories)
        }

    def render_stats(self, stats: Dict, output_format: str = "text") -> str:
        """渲染统计信息"""
        if output_format == "json":
            return json.dumps(stats, ensure_ascii=False, indent=2)

        # 文本格式
        lines = []
        lines.append("=" * 70)
        lines.append("Taskmaster 任务统计")
        lines.append("=" * 70)
        lines.append("")

        # 总览
        lines.append("📊 总览")
        lines.append("-" * 70)
        lines.append(f"总任务数: {stats['total']}")
        lines.append(f"进度: {stats['progress']:.1f}%")
        lines.append("")

        # 状态分布
        lines.append("📋 状态分布")
        lines.append("-" * 70)

        status_icons = {
            "pending": ("⭕", "待办"),
            "in-progress": ("🔄", "进行中"),
            "done": ("✅", "已完成"),
            "blocked": ("🚫", "阻塞"),
            "cancelled": ("❌", "已取消"),
            "deferred": ("⏸️", "延期"),
            "review": ("👀", "审查中")
        }

        for status, count in stats["status"].items():
            icon, label = status_icons.get(status, ("❓", status))
            percentage = count / stats["total"] * 100
            bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            lines.append(f"  {icon} {label:12} {count:3} ({percentage:5.1f}%) [{bar}]")

        lines.append("")

        # 优先级分布
        lines.append("🎯 优先级分布")
        lines.append("-" * 70)

        priority_icons = {
            "high": ("🔥", "高"),
            "medium": ("🟡", "中"),
            "low": ("🟢", "低")
        }

        for priority, count in stats["priority"].items():
            icon, label = priority_icons.get(priority, ("❓", priority))
            percentage = count / stats["total"] * 100
            lines.append(f"  {icon} {label:4} {count:3} ({percentage:5.1f}%)")

        lines.append("")

        # Spec-Kit 元信息
        if stats["phases"]:
            lines.append("📚 Phase 分布")
            lines.append("-" * 70)
            for phase, count in sorted(stats["phases"].items()):
                lines.append(f"  {phase}: {count}")
            lines.append("")

        if stats["user_stories"]:
            lines.append("👤 User Story 分布")
            lines.append("-" * 70)
            for us, count in sorted(stats["user_stories"].items()):
                lines.append(f"  {us}: {count}")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)


# ==================== 主程序 ====================

def main():
    """主程序"""
    parser = argparse.ArgumentParser(
        description="Taskmaster CLI 增强工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 显示任务树形图
  python3 scripts/tm-cli.py visualize

  # 显示任务统计
  python3 scripts/tm-cli.py stats

  # 输出 JSON 格式
  python3 scripts/tm-cli.py stats --format json

  # 指定配置文件
  python3 scripts/tm-cli.py visualize --config /path/to/tasks.json

  # 指定 Tag
  python3 scripts/tm-cli.py stats --tag my-feature
        """
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=TASKMASTER_FILE,
        help="Taskmaster tasks.json 路径"
    )

    parser.add_argument(
        "--tag",
        type=str,
        default=TASKMASTER_TAG,
        help="Taskmaster Tag"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # visualize 命令
    visualize_parser = subparsers.add_parser("visualize", help="显示任务树形图")

    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="显示任务统计")
    stats_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="输出格式"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 加载任务
    loader = TaskmasterLoader(args.config, args.tag)
    if not loader.load():
        return 1

    # 执行命令
    if args.command == "visualize":
        visualizer = TaskVisualizer(loader.tasks)
        output = visualizer.visualize()
        print(output)

    elif args.command == "stats":
        stats = TaskStats(loader.tasks)
        data = stats.calculate_stats()
        output = stats.render_stats(data, args.format)
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
