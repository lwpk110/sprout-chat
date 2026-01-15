#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taskmaster → Hamster 自动同步脚本

监听 tasks.json 变化，自动推送到 Hamster

前提条件：
1. 已安装 task-master CLI
2. 已登录: task-master auth login
3. 本地 tasks.json 已生成

依赖：
- pip install watchdog

作者: Claude (Sonnet 4.5)
日期: 2026-01-15
版本: 1.0.0
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict

# ==================== 配置 ====================

PROJECT_ROOT = Path("/home/luwei/workspace/github/sprout-chat")
TASKMASTER_FILE = PROJECT_ROOT / ".taskmaster/tasks/tasks.json"
TASKMASTER_TAG = "learning-management"
DEBOUNCE_SECONDS = 2  # 防抖延迟，避免频繁触发

# ==================== Taskmaster 推送器（复用） ====================

class TaskmasterPusher:
    """Taskmaster 推送器（复用 push-to-hamster.py 的逻辑）"""

    def __init__(self, taskmaster_file: Path):
        self.taskmaster_file = taskmaster_file
        self.tasks = []
        self.last_sync_hash = None

    def load_tasks(self) -> bool:
        """加载 Taskmaster 任务"""
        try:
            with open(self.taskmaster_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取指定 tag 的任务
            if TASKMASTER_TAG in data:
                self.tasks = data[TASKMASTER_TAG]["tasks"]
            else:
                print(f"[ERROR] Tag '{TASKMASTER_TAG}' 不存在于 {self.taskmaster_file}")
                return False

            print(f"[INFO] 已加载 {len(self.tasks)} 个任务")
            return True

        except Exception as e:
            print(f"[ERROR] 加载任务失败: {e}")
            return False

    def check_login(self) -> bool:
        """检查是否已登录 Hamster"""
        try:
            result = subprocess.run(
                ["task-master", "list"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True
            else:
                print(f"[ERROR] 未登录或登录失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"[ERROR] 检查登录失败: {e}")
            return False

    def add_task(self, task: Dict) -> bool:
        """添加单个任务到 Hamster"""
        try:
            # 构建任务描述
            prompt = self._build_task_prompt(task)

            # 构建命令
            cmd = [
                "task-master",
                "add-task",
                "--prompt", prompt
            ]

            # 添加依赖关系
            if task.get("dependencies"):
                deps = ",".join(task["dependencies"])
                cmd.extend(["--dependencies", deps])

            # 添加优先级
            if task.get("priority"):
                cmd.extend(["--priority", task["priority"]])

            # 执行命令
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"  ✅ {task['id']}: {task['title'][:30]}")
                return True
            else:
                # 任务可能已存在，视为成功
                if "already exists" in result.stderr.lower():
                    print(f"  ⏭️  {task['id']}: 已存在")
                    return True
                print(f"  ❌ {task['id']}: {result.stderr[:50]}")
                return False

        except Exception as e:
            print(f"  ❌ {task['id']}: {e}")
            return False

    def _build_task_prompt(self, task: Dict) -> str:
        """构建任务描述"""
        lines = [
            f"任务 ID: {task['id']}",
            f"标题: {task['title']}",
            f"描述: {task['description']}",
        ]

        # 添加详情
        if task.get("details"):
            lines.append(f"详情: {task['details']}")

        # 添加测试策略
        if task.get("testStrategy"):
            lines.append(f"测试策略: {task['testStrategy']}")

        # 添加标签
        if task.get("tags"):
            tags_str = ", ".join(task["tags"])
            lines.append(f"标签: {tags_str}")

        # 添加 Spec-Kit 元信息
        if "metadata" in task:
            metadata = task["metadata"]
            if metadata.get("original_id"):
                lines.append(f"原始 ID: {metadata['original_id']}")
            if metadata.get("phase"):
                lines.append(f"Phase: {metadata['phase']}")

        return "\n".join(lines)

    def sync_to_hamster(self) -> bool:
        """同步所有任务到 Hamster"""
        total = len(self.tasks)
        success_count = 0

        print(f"[INFO] 开始同步 {total} 个任务到 Hamster...")

        for i, task in enumerate(self.tasks, 1):
            if self.add_task(task):
                success_count += 1

        print(f"[INFO] 同步完成: {success_count}/{total} 成功")
        return success_count == total

    def has_changed(self) -> bool:
        """检查 tasks.json 是否变化"""
        try:
            with open(self.taskmaster_file, 'r', encoding='utf-8') as f:
                content = f.read()
                current_hash = hash(content)

                if self.last_sync_hash is None:
                    self.last_sync_hash = current_hash
                    return True

                if current_hash != self.last_sync_hash:
                    self.last_sync_hash = current_hash
                    return True

                return False

        except Exception as e:
            print(f"[ERROR] 检查文件变化失败: {e}")
            return False


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
        description="Taskmaster → Hamster 自动同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单次同步
  python3 scripts/auto-sync-to-hamster.py

  # 监听模式（前台）
  python3 scripts/auto-sync-to-hamster.py --watch

  # 监听模式（后台）
  python3 scripts/auto-sync-to-hamster.py --watch --daemon

  # 指定配置文件
  python3 scripts/auto-sync-to-hamster.py --config /path/to/tasks.json
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
        "--config",
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
    print("Taskmaster → Hamster 自动同步工具 v1.0")
    print("=" * 70)
    print()

    # 前置检查
    if not args.config.exists():
        print(f"[ERROR] 配置文件不存在: {args.config}")
        return 1

    # 创建推送器
    pusher = TaskmasterPusher(args.config)

    # 检查登录
    print("[INFO] 检查 Hamster 登录状态...")
    if not pusher.check_login():
        print()
        print("请先登录 Hamster:")
        print("  task-master auth login")
        return 1

    print("[SUCCESS] 已登录 Hamster")
    print()

    # 同步回调函数
    def sync_callback():
        if pusher.load_tasks():
            pusher.sync_to_hamster()

    # 初始同步
    if not args.no_sync_on_start:
        print("[步骤 1/2] 初始同步")
        print("-" * 70)
        sync_callback()
        print()

    # 监听模式
    if args.watch:
        if args.daemon:
            # 后台模式
            print("[步骤 2/2] 启动后台监听...")
            print("-" * 70)

            # Fork 进程
            pid = os.fork()
            if pid > 0:
                # 父进程退出
                print(f"[INFO] 后台进程已启动 (PID: {pid})")
                print(f"[INFO] 日志文件: /tmp/auto-sync-to-hamster.log")
                return 0

            # 子进程继续
            sys.stdout.flush()
            sys.stderr.flush()

            # 重定向输出
            with open("/tmp/auto-sync-to-hamster.log", "a") as log:
                os.dup2(log.fileno(), sys.stdout.fileno())
                os.dup2(log.fileno(), sys.stderr.fileno())

        else:
            print("[步骤 2/2] 启动前台监听...")
            print("-" * 70)

        # 启动监听
        watcher = FileWatcher(args.config, sync_callback)
        watcher.start()

    else:
        print("[INFO] 单次同步完成")
        print()
        print("提示: 使用 --watch 启用自动监听模式")

    return 0


if __name__ == "__main__":
    sys.exit(main())
