#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步任务脚本：将中文任务同步到 Task-Master 和导出到 Hamster 格式
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class TaskSyncer:
    """任务同步器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tm_tasks_path = project_root / ".taskmaster" / "tasks" / "tasks.json"
        self.cn_tasks_path = project_root / ".taskmaster" / "tasks" / "tasks-cn.json"

    def load_chinese_tasks(self) -> Dict:
        """加载中文任务"""
        with open(self.cn_tasks_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def sync_to_taskmaster(self) -> bool:
        """同步中文任务到 Task-Master"""
        try:
            # 加载中文任务
            cn_tasks = self.load_chinese_tasks()

            # 读取当前 Task-Master 任务
            if self.tm_tasks_path.exists():
                with open(self.tm_tasks_path, "r", encoding="utf-8") as f:
                    tm_data = json.load(f)
            else:
                tm_data = {}

            # 更新或创建 learning-management tag
            tm_data["learning-management"] = cn_tasks["learning-management"]

            # 保存到 Task-Master
            with open(self.tm_tasks_path, "w", encoding="utf-8") as f:
                json.dump(tm_data, f, ensure_ascii=False, indent=2)

            print(f"✅ 成功同步 {len(cn_tasks['learning-management']['tasks'])} 个中文任务到 Task-Master")
            return True

        except Exception as e:
            print(f"❌ 同步失败: {e}")
            return False

    def export_to_hamster_markdown(self) -> bool:
        """导出任务为 Hamster Markdown 格式"""
        try:
            cn_tasks = self.load_chinese_tasks()
            tasks = cn_tasks["learning-management"]["tasks"]

            # 生成 Markdown
            md_content = "# Phase 2.2 学习管理系统任务清单\n\n"
            md_content += "**同步时间**: 2025-01-15\n"
            md_content += "**任务数量**: {} 个\n\n".format(len(tasks))
            md_content += "---\n\n"

            # 按优先级分组
            high_priority = [t for t in tasks if t["priority"] == "high"]
            medium_priority = [t for t in tasks if t["priority"] == "medium"]

            md_content += "## 🔴 高优先级任务 (P0-P1)\n\n"
            for task in high_priority:
                md_content += f"### {task['id']}: {task['title']}\n\n"
                md_content += f"**描述**: {task['description']}\n\n"
                md_content += f"**状态**: {task['status']}\n\n"
                if task.get("details"):
                    md_content += f"**详情**: {task['details']}\n\n"
                if task.get("dependencies"):
                    md_content += f"**依赖**: {', '.join(task['dependencies'])}\n\n"
                md_content += "---\n\n"

            md_content += "## 🟡 中优先级任务 (P2)\n\n"
            for task in medium_priority:
                md_content += f"### {task['id']}: {task['title']}\n\n"
                md_content += f"**描述**: {task['description']}\n\n"
                md_content += f"**状态**: {task['status']}\n\n"
                if task.get("details"):
                    md_content += f"**详情**: {task['details']}\n\n"
                md_content += "---\n\n"

            # 保存到文件
            output_path = self.project_root / ".taskmaster" / "docs" / "hamster-sync.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            print(f"✅ 已导出 Hamster Markdown 格式到: {output_path}")
            print(f"   请手动复制到 Hamster: https://tryhamster.com/home/lwpk110s-team/briefs/226273bf-3756-4262-b47b-d8d0c51e9348/plan")
            return True

        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False

    def export_to_github_issues(self) -> bool:
        """导出任务为 GitHub Issues CSV 格式"""
        try:
            cn_tasks = self.load_chinese_tasks()
            tasks = cn_tasks["learning-management"]["tasks"]

            # 生成 CSV
            csv_content = "title,body,labels\n"
            for task in tasks:
                title = f"{task['id']}: {task['title']}"
                body = f"**描述**: {task['description']}\n\n"
                if task.get("details"):
                    body += f"**详情**: {task['details']}\n\n"
                if task.get("testStrategy"):
                    body += f"**测试策略**: {task['testStrategy']}\n\n"
                body += f"**优先级**: {task['priority']}\n"
                body += f"**状态**: {task['status']}"

                labels = f"learning-management,{task['priority']}"
                if "setup" in task.get("tags", []):
                    labels += ",setup"
                if "ai" in task.get("tags", []):
                    labels += ",ai"

                # 转义 CSV
                title = title.replace('"', '""')
                body = body.replace('"', '""')
                labels = labels.replace('"', '""')

                csv_content += f'"{title}","{body}","{labels}"\n'

            # 保存到文件
            output_path = self.project_root / ".taskmaster" / "docs" / "github-issues.csv"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(csv_content)

            print(f"✅ 已导出 GitHub Issues CSV 格式到: {output_path}")
            print(f"   导入命令: gh issue import - {output_path}")
            return True

        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False

    def show_summary(self):
        """显示任务摘要"""
        cn_tasks = self.load_chinese_tasks()
        tasks = cn_tasks["learning-management"]["tasks"]

        pending = len([t for t in tasks if t["status"] == "pending"])
        high_priority = len([t for t in tasks if t["priority"] == "high"])
        medium_priority = len([t for t in tasks if t["priority"] == "medium"])

        print("\n" + "="*60)
        print("📊 任务统计")
        print("="*60)
        print(f"总任务数: {len(tasks)}")
        print(f"待处理: {pending}")
        print(f"高优先级: {high_priority}")
        print(f"中优先级: {medium_priority}")
        print("="*60 + "\n")


def main():
    """主函数"""
    print("🚀 Task-Master 任务同步工具\n")

    syncer = TaskSyncer(PROJECT_ROOT)

    # 显示摘要
    syncer.show_summary()

    # 1. 同步到 Task-Master
    print("步骤 1: 同步中文任务到 Task-Master")
    if syncer.sync_to_taskmaster():
        print("   ✅ 完成\n")
    else:
        print("   ❌ 失败\n")
        return 1

    # 2. 导出到 Hamster Markdown
    print("步骤 2: 导出 Hamster Markdown 格式")
    if syncer.export_to_hamster_markdown():
        print("   ✅ 完成\n")
    else:
        print("   ❌ 失败\n")
        return 1

    # 3. 导出到 GitHub Issues CSV
    print("步骤 3: 导出 GitHub Issues CSV 格式")
    if syncer.export_to_github_issues():
        print("   ✅ 完成\n")
    else:
        print("   ❌ 失败\n")
        return 1

    print("\n" + "="*60)
    print("🎉 同步完成！")
    print("="*60)
    print("\n下一步:")
    print("1. 查看中文任务: cat .taskmaster/tasks/tasks.json")
    print("2. 复制到 Hamster: cat .taskmaster/docs/hamster-sync.md")
    print("3. 导入到 GitHub: gh issue import - .taskmaster/docs/github-issues.csv")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
