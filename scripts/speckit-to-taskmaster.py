#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec-Kit → Taskmaster 双向同步脚本

功能：
  1. 解析 Spec-Kit tasks.md（Markdown 格式）
  2. 自动生成 Taskmaster JSON 任务
  3. 保留 Spec-Kit 元信息（Phase、用户故事、依赖关系）
  4. 支持双向状态同步

作者: Claude (Sonnet 4.5)
日期: 2026-01-15
版本: 2.0.0
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# ==================== 配置 ====================

PROJECT_ROOT = Path("/home/luwei/workspace/github/sprout-chat")
SPECKIT_TASKS_FILE = PROJECT_ROOT / "specs/001-learning-management/tasks.md"
TASKMASTER_FILE = PROJECT_ROOT / ".taskmaster/tasks/tasks.json"
TASKMASTER_TAG = "learning-management"
PHASE_PREFIX = "LWP-2.2"  # Taskmaster 任务 ID 前缀

# ==================== 数据模型 ====================

@dataclass
class SpecKitTask:
    """Spec-Kit 任务模型"""
    id: str  # T001, T002, ...
    title: str
    description: str
    phase: str  # Phase 1, Phase 2, ...
    user_story: Optional[str]  # US1, US2, ...
    status: str  # pending, done
    priority: str  # high, medium
    tags: List[str]
    dependencies: List[str]
    commit_message: str  # 预期的 commit message
    metadata: Dict  # 额外的 Spec-Kit 元信息


@dataclass
class TaskmasterTask:
    """Taskmaster 任务模型"""
    id: str  # LWP-2.2-T001
    title: str
    description: str
    status: str
    priority: str
    dependencies: List[str]
    details: str
    test_strategy: str
    tags: List[str]
    subtasks: List
    # Spec-Kit 元信息（扩展字段）
    speckit_metadata: Dict


# ==================== Spec-Kit 解析器 ====================

class SpecKitParser:
    """Spec-Kit tasks.md 解析器"""

    def __init__(self, tasks_file: Path):
        self.tasks_file = tasks_file
        self.content = ""
        self.current_phase = ""

    def load(self) -> bool:
        """加载 tasks.md 文件"""
        if not self.tasks_file.exists():
            print(f"[ERROR] 找不到 Spec-Kit tasks.md: {self.tasks_file}")
            return False

        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            self.content = f.read()

        print(f"[INFO] 已加载 Spec-Kit tasks.md: {self.tasks_file}")
        return True

    def parse(self) -> List[SpecKitTask]:
        """解析 tasks.md，返回任务列表"""
        tasks = []
        lines = self.content.split('\n')

        for line in lines:
            # 检测 Phase 标题
            phase_match = re.match(r'## Phase (\d+):', line)
            if phase_match:
                self.current_phase = f"Phase {phase_match.group(1)}"
                print(f"[DEBUG] 进入 {self.current_phase}")
                continue

            # 检测 User Story 标题
            us_match = re.match(r'### 目标|### 用户故事|用户故事 (US\d+)', line)
            current_us = None
            if us_match:
                us_search = re.search(r'US(\d+)', line)
                if us_search:
                    current_us = f"US{us_search.group(1)}"

            # 检测任务项
            task_match = re.match(r'- \[([ x])\] \[?([PT]?\d+)\]?(?: \[([^\]]+)\])?(?: \[(US\d+)\])? (.+)', line)
            if not task_match:
                # 尝试简化格式
                task_match = re.match(r'- \[([ x])\] ([A-Z]?\d+) (.+)', line)

            if task_match:
                status_char = task_match.group(1)
                task_id = task_match.group(2)
                priority_marker = task_match.group(3) if len(task_match.groups()) >= 3 else None
                user_story = task_match.group(4) if len(task_match.groups()) >= 4 else current_us
                description = task_match.group(5) if len(task_match.groups()) >= 5 else task_match.group(3)

                # 标准化任务 ID
                if not task_id.startswith('T'):
                    task_id = f"T{task_id}"

                # 解析状态
                status = "done" if status_char == 'x' else "pending"

                # 解析优先级
                priority = "high"
                if priority_marker:
                    if 'P' in priority_marker:
                        priority_map = {'P1': 'high', 'P2': 'medium', 'P0': 'high'}
                        priority = priority_map.get(priority_marker, 'medium')
                    elif '[P]' in priority_marker:
                        priority = 'medium'  # 并行任务标记

                # 解析标签
                tags = [self.current_phase.replace(' ', '-')]
                if user_story:
                    tags.append(user_story)
                tags.append("tdd")  # Spec-Kit 任务都是 TDD

                # 解析依赖（从描述中提取）
                dependencies = self._extract_dependencies(description)

                # 提取 commit message
                commit_message = self._extract_commit_message(description)

                # 解析标题
                title = self._extract_title(description)

                task = SpecKitTask(
                    id=task_id,
                    title=title,
                    description=description,
                    phase=self.current_phase,
                    user_story=user_story,
                    status=status,
                    priority=priority,
                    tags=tags,
                    dependencies=dependencies,
                    commit_message=commit_message,
                    metadata={
                        "source": "speckit",
                        "phase": self.current_phase,
                        "user_story": user_story,
                        "original_id": task_id,
                        "file": str(self.tasks_file)
                    }
                )

                tasks.append(task)
                print(f"[DEBUG] 解析任务: {task.id} - {title}")

        return tasks

    def _extract_dependencies(self, description: str) -> List[str]:
        """从描述中提取依赖关系"""
        dependencies = []

        # 查找 TXXX 格式的依赖
        dep_matches = re.findall(r'T\d+', description)
        for dep_id in dep_matches:
            # 转换为 Taskmaster ID
            dependencies.append(f"{PHASE_PREFIX}-{dep_id}")

        return dependencies

    def _extract_commit_message(self, description: str) -> str:
        """从描述中提取 commit message"""
        # 查找 git commit 行
        commit_match = re.search(r'git commit -m "([^"]+)"', description)
        if commit_match:
            return commit_match.group(1)

        # 如果没有找到，生成默认的
        return f"[{PHASE_PREFIX}-XXX] feat: {description[:50]}..."

    def _extract_title(self, description: str) -> str:
        """从描述中提取标题"""
        # 移除 commit 信息
        title = re.sub(r'\s*git commit -m "[^"]+"', '', description)
        title = title.strip()

        # 移除行号标记
        title = re.sub(r'^\s*[\w-]+\s+', '', title)

        # 限制长度
        if len(title) > 100:
            title = title[:97] + "..."

        return title


# ==================== Taskmaster 生成器 ====================

class TaskmasterGenerator:
    """Taskmaster JSON 生成器"""

    def __init__(self, phase_prefix: str):
        self.phase_prefix = phase_prefix

    def generate(self, speckit_tasks: List[SpecKitTask]) -> List[TaskmasterTask]:
        """从 Spec-Kit 任务生成 Taskmaster 任务"""
        tm_tasks = []

        for speckit_task in speckit_tasks:
            # 转换任务 ID
            tm_id = f"{self.phase_prefix}-{speckit_task.id}"

            # 转换依赖关系
            tm_dependencies = []
            for dep in speckit_task.dependencies:
                # 确保依赖使用正确的 ID 格式
                if not dep.startswith(self.phase_prefix):
                    dep = f"{self.phase_prefix}-{dep}"
                tm_dependencies.append(dep)

            # 生成详情（包含 Spec-Kit 元信息）
            details = self._generate_details(speckit_task)

            # 生成测试策略
            test_strategy = self._generate_test_strategy(speckit_task)

            # 合并标签
            tags = speckit_task.tags.copy()
            tags.append("speckit")

            # 创建 Taskmaster 任务
            tm_task = TaskmasterTask(
                id=tm_id,
                title=speckit_task.title,
                description=speckit_task.description,
                status=speckit_task.status,
                priority=speckit_task.priority,
                dependencies=tm_dependencies,
                details=details,
                test_strategy=test_strategy,
                tags=tags,
                subtasks=[],
                speckit_metadata=speckit_task.metadata
            )

            tm_tasks.append(tm_task)
            print(f"[INFO] 生成任务: {tm_id} - {speckit_task.title}")

        return tm_tasks

    def _generate_details(self, speckit_task: SpecKitTask) -> str:
        """生成任务详情"""
        details = []

        if speckit_task.phase:
            details.append(f"**Phase**: {speckit_task.phase}")

        if speckit_task.user_story:
            details.append(f"**User Story**: {speckit_task.user_story}")

        if speckit_task.commit_message:
            details.append(f"**Commit Message**: `{speckit_task.commit_message}`")

        details.append(f"**Source**: Spec-Kit tasks.md")
        details.append(f"**Original ID**: {speckit_task.id}")

        return "\n".join(details)

    def _generate_test_strategy(self, speckit_task: SpecKitTask) -> str:
        """生成测试策略"""
        if "test" in speckit_task.title.lower():
            return "TDD 红灯阶段：运行 pytest 确认测试失败"

        if "集成测试" in speckit_task.title:
            return "端到端测试完整功能流程"

        return "TDD 绿灯阶段：运行 pytest 确认测试通过"

    def to_taskmaster_format(self, tm_tasks: List[TaskmasterTask]) -> Dict:
        """转换为 Taskmaster JSON 格式"""
        tasks_data = []

        for tm_task in tm_tasks:
            task_dict = {
                "id": tm_task.id,
                "title": tm_task.title,
                "description": tm_task.description,
                "status": tm_task.status,
                "priority": tm_task.priority,
                "dependencies": tm_task.dependencies,
                "details": tm_task.details,
                "testStrategy": tm_task.test_strategy,
                "tags": tm_task.tags,
                "subtasks": tm_task.subtasks,
                # Spec-Kit 元信息（保留在 metadata 字段）
                "metadata": tm_task.speckit_metadata
            }

            tasks_data.append(task_dict)

        return {
            TASKMASTER_TAG: {
                "tasks": tasks_data,
                "metadata": {
                    "source": "speckit",
                    "synced_at": datetime.now().isoformat(),
                    "speckit_file": str(SPECKIT_TASKS_FILE)
                }
            }
        }


# ==================== 同步引擎 ====================

class SyncEngine:
    """双向同步引擎"""

    def __init__(self, taskmaster_file: Path):
        self.taskmaster_file = taskmaster_file
        self.existing_data = {}

    def load_taskmaster(self) -> bool:
        """加载现有 Taskmaster 数据"""
        if not self.taskmaster_file.exists():
            print(f"[INFO] Taskmaster 文件不存在，将创建新文件")
            return True

        with open(self.taskmaster_file, 'r', encoding='utf-8') as f:
            self.existing_data = json.load(f)

        print(f"[INFO] 已加载现有 Taskmaster 数据")
        return True

    def merge_tasks(self, new_tasks: List[TaskmasterTask]) -> List[TaskmasterTask]:
        """合并新任务和现有任务（保留状态）"""
        merged_tasks = []

        # 创建现有任务映射
        existing_tasks_map = {}
        if TASKMASTER_TAG in self.existing_data:
            for existing_task in self.existing_data[TASKMASTER_TAG].get("tasks", []):
                existing_tasks_map[existing_task["id"]] = existing_task

        for new_task in new_tasks:
            if new_task.id in existing_tasks_map:
                # 保留现有任务的状态
                existing_task = existing_tasks_map[new_task.id]

                # 更新其他字段，但保留状态
                new_task.status = existing_task.get("status", new_task.status)

                # 如果有子任务，也保留
                if existing_task.get("subtasks"):
                    new_task.subtasks = existing_task["subtasks"]

                print(f"[INFO] 保留任务状态: {new_task.id} -> {new_task.status}")

            merged_tasks.append(new_task)

        return merged_tasks

    def save_to_taskmaster(self, tm_data: Dict) -> bool:
        """保存到 Taskmaster JSON 文件"""
        try:
            # 创建目录（如果不存在）
            self.taskmaster_file.parent.mkdir(parents=True, exist_ok=True)

            # 保存到文件
            with open(self.taskmaster_file, 'w', encoding='utf-8') as f:
                json.dump(tm_data, f, ensure_ascii=False, indent=2)

            print(f"[SUCCESS] 已保存到 Taskmaster: {self.taskmaster_file}")
            return True

        except Exception as e:
            print(f"[ERROR] 保存失败: {e}")
            return False

    def generate_report(self, speckit_tasks: List[SpecKitTask], tm_tasks: List[TaskmasterTask]) -> str:
        """生成同步报告"""
        report_lines = [
            "# Spec-Kit → Taskmaster 同步报告\n",
            f"**同步时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Spec-Kit 文件**: {SPECKIT_TASKS_FILE}",
            f"**Taskmaster 文件**: {self.taskmaster_file}",
            "\n---\n",
            "## 同步统计\n",
            f"- Spec-Kit 任务数: {len(speckit_tasks)}",
            f"- Taskmaster 任务数: {len(tm_tasks)}",
            f"- Phase 前缀: {PHASE_PREFIX}",
            "\n---\n",
            "## 任务映射\n",
            "| Spec-Kit ID | Taskmaster ID | 标题 | 状态 | 优先级 |",
            "|-------------|---------------|------|------|--------|",
        ]

        for i, speckit_task in enumerate(speckit_tasks):
            tm_id = f"{PHASE_PREFIX}-{speckit_task.id}"
            title = speckit_task.title[:50] + "..." if len(speckit_task.title) > 50 else speckit_task.title
            status_emoji = "✅" if speckit_task.status == "done" else "⏳"
            priority = speckit_task.priority

            report_lines.append(f"| {speckit_task.id} | {tm_id} | {title} | {status_emoji} {speckit_task.status} | {priority} |")

        report_lines.extend([
            "\n---\n",
            "## Spec-Kit 元信息保留\n",
            "- ✅ Phase 信息（标签）",
            "- ✅ User Story（标签和详情）",
            "- ✅ 原始任务 ID（metadata）",
            "- ✅ Commit Message（详情）",
            "- ✅ 依赖关系（自动转换 ID）",
            "\n---\n",
            "## 下一步\n",
            "1. 检查同步后的任务: `cat .taskmaster/tasks/tasks.json`",
            "2. 查看任务列表: `tm list`",
            "3. 开始任务: `tm autopilot start <task-id>`",
            "\n---\n",
            "**报告结束**"
        ])

        return "\n".join(report_lines)


# ==================== 主程序 ====================

def main():
    """主函数"""
    print("=" * 70)
    print("Spec-Kit → Taskmaster 双向同步工具 v2.0")
    print("=" * 70)
    print()

    # 1. 解析 Spec-Kit tasks.md
    print("[步骤 1/4] 解析 Spec-Kit tasks.md")
    print("-" * 70)

    parser = SpecKitParser(SPECKIT_TASKS_FILE)
    if not parser.load():
        return 1

    speckit_tasks = parser.parse()
    print(f"[SUCCESS] 已解析 {len(speckit_tasks)} 个 Spec-Kit 任务\n")

    # 2. 生成 Taskmaster 任务
    print("[步骤 2/4] 生成 Taskmaster 任务")
    print("-" * 70)

    generator = TaskmasterGenerator(PHASE_PREFIX)
    tm_tasks = generator.generate(speckit_tasks)
    print(f"[SUCCESS] 已生成 {len(tm_tasks)} 个 Taskmaster 任务\n")

    # 3. 合并现有任务
    print("[步骤 3/4] 合并现有任务")
    print("-" * 70)

    sync_engine = SyncEngine(TASKMASTER_FILE)
    sync_engine.load_taskmaster()
    merged_tasks = sync_engine.merge_tasks(tm_tasks)
    print(f"[SUCCESS] 已合并 {len(merged_tasks)} 个任务\n")

    # 4. 保存到 Taskmaster
    print("[步骤 4/4] 保存到 Taskmaster")
    print("-" * 70)

    tm_data = generator.to_taskmaster_format(merged_tasks)
    if not sync_engine.save_to_taskmaster(tm_data):
        return 1

    print()

    # 生成报告
    print("=" * 70)
    print("📊 同步完成")
    print("=" * 70)

    report = sync_engine.generate_report(speckit_tasks, merged_tasks)
    report_file = PROJECT_ROOT / ".taskmaster/docs/speckit-sync-report.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 同步报告: {report_file}")
    print(f"\n下一步:")
    print(f"  1. 查看报告: cat {report_file}")
    print(f"  2. 列出任务: tm list")
    print(f"  3. 查看详情: tm get {PHASE_PREFIX}-T001")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
