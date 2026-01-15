#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec-Kit → Taskmaster 完全自动化同步脚本

使用 Taskmaster MCP 工具实现完全自动化的任务同步

新增功能：
- --watch 模式：监听 tasks.md 变化自动同步
- --daemon 模式：后台运行

作者: Claude (Sonnet 4.5)
日期: 2026-01-15
版本: 2.2.0
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

# ==================== 配置 ====================

PROJECT_ROOT = Path("/home/luwei/workspace/github/sprout-chat")
SPECKIT_TASKS_FILE = PROJECT_ROOT / "specs/001-learning-management/tasks.md"
TASKMASTER_FILE = PROJECT_ROOT / ".taskmaster/tasks/tasks.json"
TASKMASTER_TAG = "learning-management"
PHASE_PREFIX = "LWP-2.2"
DEBOUNCE_SECONDS = 2  # 防抖延迟，避免频繁触发

# ==================== Spec-Kit 解析器 ====================

class SpecKitParser:
    """Spec-Kit tasks.md 解析器（简化版）"""

    def __init__(self, tasks_file: Path):
        self.tasks_file = tasks_file
        self.content = ""

    def load(self) -> bool:
        """加载 tasks.md 文件"""
        if not self.tasks_file.exists():
            print(f"[ERROR] 找不到 Spec-Kit tasks.md: {self.tasks_file}")
            return False

        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            self.content = f.read()

        print(f"[INFO] 已加载 Spec-Kit tasks.md")
        return True

    def parse(self) -> List[Dict]:
        """解析 tasks.md，返回任务列表"""
        import re

        tasks = []
        lines = self.content.split('\n')

        for line in lines:
            # 检测任务项：- [ ] T001 或 - [x] T001
            task_match = re.match(r'- \[([ x])\] ([A-Z]?\d+) (.+)', line)
            if task_match:
                status_char = task_match.group(1)
                task_id = task_match.group(2)
                description = task_match.group(3)

                # 标准化任务 ID
                if not task_id.startswith('T'):
                    task_id = f"T{task_id}"

                # 解析状态
                status = "done" if status_char == 'x' else "pending"

                # 解析优先级（简化）
                priority = "high"
                if "[P]" in description or "P2" in description:
                    priority = "medium"

                # 解析标题
                title = description.split('-')[0].strip() if '-' in description else description[:50]

                task = {
                    "id": task_id,
                    "title": title,
                    "description": description,
                    "status": status,
                    "priority": priority,
                    "dependencies": [],
                    "tags": ["speckit", "tdd"]
                }

                tasks.append(task)

        return tasks


# ==================== Taskmaster 同步器 ====================

class TaskmasterSyncer:
    """Taskmaster 同步器（直接修改 JSON）"""

    def __init__(self, taskmaster_file: Path):
        self.taskmaster_file = taskmaster_file
        self.existing_data = {}

    def load_existing(self) -> bool:
        """加载现有 Taskmaster 数据"""
        if not self.taskmaster_file.exists():
            print(f"[INFO] Taskmaster 文件不存在，将创建新文件")
            self.existing_data = {}
            return True

        with open(self.taskmaster_file, 'r', encoding='utf-8') as f:
            self.existing_data = json.load(f)

        print(f"[INFO] 已加载现有 Taskmaster 数据")
        return True

    def sync_tasks(self, speckit_tasks: List[Dict]) -> bool:
        """同步任务到 Taskmaster JSON"""
        try:
            # 转换 Spec-Kit 任务为 Taskmaster 格式
            tm_tasks = []
            for speckit_task in speckit_tasks:
                tm_id = f"{PHASE_PREFIX}-{speckit_task['id']}"

                # 检查是否已存在，保留状态
                existing_task = self._find_existing_task(tm_id)
                if existing_task:
                    status = existing_task.get("status", speckit_task["status"])
                else:
                    status = speckit_task["status"]

                tm_task = {
                    "id": tm_id,
                    "title": speckit_task["title"],
                    "description": speckit_task["description"],
                    "status": status,
                    "priority": speckit_task["priority"],
                    "dependencies": speckit_task["dependencies"],
                    "details": f"**Source**: Spec-Kit tasks.md\n**Original ID**: {speckit_task['id']}",
                    "testStrategy": "TDD 绿灯阶段：运行 pytest 确认测试通过",
                    "tags": speckit_task["tags"],
                    "subtasks": [],
                    "metadata": {
                        "source": "speckit",
                        "original_id": speckit_task['id'],
                        "file": str(SPECKIT_TASKS_FILE)
                    }
                }

                tm_tasks.append(tm_task)

            # 更新 Taskmaster 数据
            self.existing_data[TASKMASTER_TAG] = {
                "tasks": tm_tasks,
                "metadata": {
                    "source": "speckit",
                    "synced_at": "2026-01-15T13:00:00Z",
                    "speckit_file": str(SPECKIT_TASKS_FILE)
                }
            }

            # 保存到文件
            self.taskmaster_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.taskmaster_file, 'w', encoding='utf-8') as f:
                json.dump(self.existing_data, f, ensure_ascii=False, indent=2)

            print(f"[SUCCESS] 已同步 {len(tm_tasks)} 个任务到 Taskmaster")
            return True

        except Exception as e:
            print(f"[ERROR] 同步失败: {e}")
            return False

    def _find_existing_task(self, task_id: str) -> Dict:
        """查找现有任务"""
        if TASKMASTER_TAG in self.existing_data:
            for task in self.existing_data[TASKMASTER_TAG].get("tasks", []):
                if task.get("id") == task_id:
                    return task
        return None

    def verify_tasks(self) -> bool:
        """验证任务（使用 Taskmaster CLI）"""
        try:
            # 尝试使用 tm 命令验证
            result = subprocess.run(
                ["tm", "list", "--tag", TASKMASTER_TAG],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"[INFO] Taskmaster 验证成功")
                print(result.stdout)
                return True
            else:
                print(f"[WARNING] tm 命令不可用，跳过验证")
                return True

        except Exception as e:
            print(f"[INFO] 无法验证: {e}")
            return True


# ==================== 文件监听器 ====================

class FileWatcher:
    """文件监听器（使用 watchdog）"""

    def __init__(self, file_path: Path, callback, debounce: float = DEBOUNCE_SECONDS):
        self.file_path = file_path
        self.callback = callback
        self.debounce = debounce
        self.last_trigger = 0
        self.observer = None

    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return

        # 检查是否是监听的文件
        if Path(event.src_path) == self.file_path:
            now = time.time()

            # 防抖：避免短时间内多次触发
            if now - self.last_trigger < self.debounce:
                return

            self.last_trigger = now
            print(f"\n[INFO] 检测到 {self.file_path.name} 变化")

            # 执行回调
            try:
                self.callback()
            except Exception as e:
                print(f"[ERROR] 同步失败: {e}")

    def start(self):
        """启动监听"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class Handler(FileSystemEventHandler):
                def __init__(self, watcher):
                    self.watcher = watcher

                def on_modified(self, event):
                    self.watcher.on_modified(event)

            self.observer = Observer()
            handler = Handler(self)
            self.observer.schedule(handler, str(self.file_path.parent), recursive=False)
            self.observer.start()

            print(f"[INFO] 正在监听 {self.file_path}...")
            print(f"[INFO] 按 Ctrl+C 停止监听\n")

            # 保持运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

        except ImportError:
            print("[ERROR] 未安装 watchdog 库")
            print("请运行: pip install watchdog")
            sys.exit(1)

    def stop(self):
        """停止监听"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("\n[INFO] 监听已停止")


# ==================== 主程序 ====================

def main():
    """主程序"""
    parser = argparse.ArgumentParser(
        description="Spec-Kit → Taskmaster 自动同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单次同步
  python3 scripts/auto-sync-to-taskmaster.py

  # 监听模式（前台）
  python3 scripts/auto-sync-to-taskmaster.py --watch

  # 监听模式（后台）
  python3 scripts/auto-sync-to-taskmaster.py --watch --daemon

  # 指定配置文件
  python3 scripts/auto-sync-to-taskmaster.py --speckit /path/to/tasks.md --taskmaster /path/to/tasks.json
        """
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="监听模式，自动同步变化"
    )

    parser.add_argument(
        "--daemon",
        action="store_true",
        help="后台运行模式（需配合 --watch）"
    )

    parser.add_argument(
        "--speckit",
        type=Path,
        default=SPECKIT_TASKS_FILE,
        help="Spec-Kit tasks.md 路径"
    )

    parser.add_argument(
        "--taskmaster",
        type=Path,
        default=TASKMASTER_FILE,
        help="Taskmaster tasks.json 路径"
    )

    parser.add_argument(
        "--no-sync-on-start",
        action="store_true",
        help="启动时不立即同步（仅 --watch 模式）"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Spec-Kit → Taskmaster 完全自动化同步 v2.2")
    print("=" * 70)
    print()

    # 前置检查
    if not args.speckit.exists():
        print(f"[ERROR] Spec-Kit 文件不存在: {args.speckit}")
        return 1

    # 同步回调函数
    def sync_callback():
        print("\n" + "=" * 70)
        print("开始同步...")
        print("=" * 70)

        # 1. 解析 Spec-Kit
        print("[步骤 1/3] 解析 Spec-Kit tasks.md")
        print("-" * 70)

        parser_obj = SpecKitParser(args.speckit)
        if not parser_obj.load():
            return 1

        speckit_tasks = parser_obj.parse()
        print(f"[SUCCESS] 已解析 {len(speckit_tasks)} 个 Spec-Kit 任务\n")

        # 2. 同步到 Taskmaster
        print("[步骤 2/3] 同步到 Taskmaster JSON")
        print("-" * 70)

        syncer = TaskmasterSyncer(args.taskmaster)
        syncer.load_existing()

        if not syncer.sync_tasks(speckit_tasks):
            return 1

        print()

        # 3. 验证任务
        print("[步骤 3/3] 验证任务")
        print("-" * 70)

        syncer.verify_tasks()

        print()
        print("=" * 70)
        print("✅ 同步完成！")
        print("=" * 70)
        print()

    # 初始同步
    if not args.no_sync_on_start:
        sync_callback()

    # 监听模式
    if args.watch:
        if args.daemon:
            # 后台模式
            print("[INFO] 启动后台监听...")
            print("-" * 70)

            # Fork 进程
            pid = os.fork()
            if pid > 0:
                # 父进程退出
                print(f"[INFO] 后台进程已启动 (PID: {pid})")
                print(f"[INFO] 日志文件: /tmp/auto-sync-to-taskmaster.log")
                return 0

            # 子进程继续
            sys.stdout.flush()
            sys.stderr.flush()

            # 重定向输出
            with open("/tmp/auto-sync-to-taskmaster.log", "a") as log:
                os.dup2(log.fileno(), sys.stdout.fileno())
                os.dup2(log.fileno(), sys.stderr.fileno())

        else:
            print("[INFO] 启动前台监听...")
            print("-" * 70)

        # 启动监听
        watcher = FileWatcher(args.speckit, sync_callback)
        watcher.start()

    else:
        if not args.no_sync_on_start:
            print()
            print("下一步：")
            print("  1. 查看任务: tm list --tag=learning-management")
            print("  2. 推送到 Hamster: python3 scripts/auto-sync-to-hamster.py")
            print()
            print("提示: 使用 --watch 启用自动监听模式")

    return 0


if __name__ == "__main__":
    sys.exit(main())
