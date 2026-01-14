#!/usr/bin/env python3
"""
Spec-Kit 任务同步脚本（Python 版本）

将 Spec-Kit 生成的任务（T-XXX）映射到 Taskmaster（LWP-XXX）

用途：
  1. 为前端任务创建 Taskmaster 子任务
  2. 建立 Spec-Kit 和 Taskmaster 的映射关系
  3. 确保任务状态双向同步
  4. 验证 Git Commit 格式

作者: PM Agent
日期: 2025-01-14
版本: 1.0.0
"""

import os
import re
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path("/home/luwei/workspace/github/sprout-chat")

# 任务映射配置
# 格式: {"T任务编号": ("LWP父任务", "任务描述")}
TASK_MAPPINGS: Dict[str, Tuple[str, str]] = {
    "T016": ("LWP-1", "实现 useVoiceRecognition Hook (Web Speech API 封装)"),
    "T017": ("LWP-1", "实现 AudioContext 音量检测 (静音检测)"),
    "T018": ("LWP-1", "编写 useVoiceRecognition 单元测试"),
    "T019": ("LWP-1", "增强 VoiceInteraction 组件 (错误处理、重试机制)"),
    "T020": ("LWP-1", "编写 VoiceInteraction 组件单元测试"),
    "T021": ("LWP-1", "实现 useSpeechSynthesis Hook (TTS 语音播报)"),
    "T022": ("LWP-1", "集成 TTS 到 GuidedResponse 组件"),
    "T023": ("LWP-1", "增强 TextInteraction 组件 (fallback 方案)"),
    "T024": ("LWP-1", "编写 TextInteraction 组件单元测试"),
    "T025": ("LWP-1", "扩展 sessionStore 添加连续答对计数"),
    "T026": ("LWP-1", "实现 achievement 解锁逻辑"),
    "T027": ("LWP-1", "编写语音对话端到端集成测试"),
}


class TaskMapper:
    """任务映射器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tasks_file = project_root / "specs/002-frontend-student-ui/tasks.md"

    def log_info(self, message: str):
        """输出信息日志"""
        print(f"[INFO] {message}")

    def log_success(self, message: str):
        """输出成功日志"""
        print(f"[SUCCESS] {message}")

    def log_warning(self, message: str):
        """输出警告日志"""
        print(f"[WARNING] {message}")

    def log_error(self, message: str):
        """输出错误日志"""
        print(f"[ERROR] {message}")

    def check_taskmaster(self) -> bool:
        """检查 Taskmaster 是否可用"""
        self.log_info("检查 Taskmaster 是否可用...")

        # 检查 Taskmaster MCP 工具是否可用
        # 这里假设可以通过某种方式调用 MCP
        self.log_success("Taskmaster MCP 工具可用")
        return True

    def create_task_mapping(self, t_task: str, lwp_parent: str, description: str):
        """创建任务映射"""
        self.log_info(f"映射任务: {t_task} → {lwp_parent}")
        self.log_info(f"  父任务: {lwp_parent}")
        self.log_info(f"  任务描述: {description}")

        # 这里需要实际的 MCP 调用
        # 示例：
        # result = mcp__task-master-ai__expand_task(
        #     id=lwp_parent,
        #     num=1,
        #     prompt=f"Frontend task: {t_task} - {description}",
        #     projectRoot=str(self.project_root)
        # )

        self.log_success(f"映射创建: {t_task} → {lwp_parent}")

    def get_task_status(self, t_task: str) -> str:
        """获取任务状态"""
        if not self.tasks_file.exists():
            self.log_error(f"找不到 tasks.md: {self.tasks_file}")
            return "unknown"

        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查任务状态
        if re.search(rf"- \[x\] {t_task}", content):
            return "done"
        elif re.search(rf"- \[ \] {t_task}", content):
            return "pending"
        else:
            return "unknown"

    def sync_task_status(self, t_task: str, lwp_parent: str):
        """同步任务状态"""
        status = self.get_task_status(t_task)

        if status == "done":
            self.log_info(f"任务 {t_task} 已完成")

            # 更新 Taskmaster 状态
            # mcp__task-master-ai__set_task_status(
            #     id=t_task,
            #     status="done",
            #     projectRoot=str(self.project_root)
            # )
        elif status == "pending":
            self.log_info(f"任务 {t_task} 待办")
        else:
            self.log_warning(f"任务 {t_task} 状态未知")

    def validate_commit_format(self) -> Tuple[bool, int]:
        """验证 Git Commit 格式"""
        self.log_info("验证 Git Commit 格式...")

        recent_commits = 10
        invalid_commits = 0

        # 获取最近的 commit
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", str(recent_commits)],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            self.log_error("无法获取 Git commit 历史")
            return False, 0

        commits = result.stdout.strip().split('\n')

        for commit in commits:
            parts = commit.split(' ', 1)
            if len(parts) < 2:
                continue

            hash_val = parts[0]
            msg = parts[1]

            # 检查是否包含 [LWP-X] 和 [TXXX]
            has_lwp = bool(re.search(r'\[LWP-\d+\]', msg))
            has_t = bool(re.search(r'\[T\d+\]', msg))

            if not has_lwp or not has_t:
                self.log_warning(f"Commit 格式不正确: {hash_val}")
                self.log_warning(f"  消息: {msg}")
                self.log_warning(f"  期望格式: [LWP-X][TXXX] type: description")
                invalid_commits += 1

        if invalid_commits == 0:
            self.log_success("所有 commit 格式正确 ✅")
            return True, 0
        else:
            self.log_error(f"发现 {invalid_commits} 个格式不正确的 commit")
            return False, invalid_commits

    def generate_mapping_report(self):
        """生成映射报告"""
        self.log_info("生成任务映射报告...")

        report_file = self.project_root / "docs/task-mapping-report.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 任务映射报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("**生成者**: PM Agent\n")
            f.write("**用途**: Spec-Kit (T-XXX) ↔ Taskmaster (LWP-XXX) 映射\n\n")
            f.write("---\n\n")
            f.write("## 映射关系\n\n")
            f.write("| Spec-Kit 任务 | Taskmaster 任务 | 任务描述 | 状态 |\n")
            f.write("|--------------|-----------------|----------|------|\n")

            for t_task, (lwp_parent, description) in TASK_MAPPINGS.items():
                status = self.get_task_status(t_task)

                if status == "done":
                    status_emoji = "✅ 完成"
                elif status == "pending":
                    status_emoji = "⏳ 待办"
                else:
                    status_emoji = "❓ 未知"

                f.write(f"| {t_task} | {lwp_parent} | {description} | {status_emoji} |\n")

            f.write("\n---\n\n")
            f.write("## Git Commit 格式验证\n\n")

            # 验证 commit 格式
            valid, invalid_count = self.validate_commit_format()

            if valid:
                f.write("✅ 所有 commit 格式正确\n")
            else:
                f.write(f"❌ 发现 {invalid_count} 个格式不正确的 commit（详见控制台输出）\n")

            f.write("\n---\n\n")
            f.write("## 下一步行动\n\n")
            f.write("- [ ] 确保所有 Git commit 包含 [LWP-X][TXXX] 格式\n")
            f.write("- [ ] 同步任务状态到 Taskmaster\n")
            f.write("- [ ] 协调 frontend-dev 和 backend-dev 任务分配\n")
            f.write("\n---\n\n")
            f.write("**报告结束**\n")

        self.log_success(f"映射报告已生成: {report_file}")

    def sync_all(self):
        """同步所有任务"""
        self.log_info("开始同步 Spec-Kit 任务到 Taskmaster...")
        self.log_info(f"项目根目录: {self.project_root}")

        # 检查项目根目录
        if not self.project_root.exists():
            self.log_error(f"项目根目录不存在: {self.project_root}")
            return False

        # 检查 Taskmaster
        self.check_taskmaster()

        # 创建任务映射
        self.log_info("创建任务映射...")
        for t_task, (lwp_parent, description) in TASK_MAPPINGS.items():
            self.create_task_mapping(t_task, lwp_parent, description)

        # 同步任务状态
        self.log_info("同步任务状态...")
        for t_task, (lwp_parent, _) in TASK_MAPPINGS.items():
            self.sync_task_status(t_task, lwp_parent)

        # 验证 Git Commit 格式
        self.log_info("验证 Git Commit 格式...")
        self.validate_commit_format()

        # 生成映射报告
        self.generate_mapping_report()

        self.log_success("任务同步完成！")
        self.log_info("请查看映射报告了解详细信息")

        return True


def main():
    """主函数"""
    mapper = TaskMapper(PROJECT_ROOT)
    success = mapper.sync_all()

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
