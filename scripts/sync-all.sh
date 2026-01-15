#!/bin/bash
# 一键同步脚本：Spec-Kit → Taskmaster → Hamster

set -e

PROJECT_ROOT="/home/luwei/workspace/github/sprout-chat"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "🚀 一键同步：Spec-Kit → Taskmaster → Hamster"
echo "======================================================================"
echo ""

# 步骤 1: Spec-Kit → Taskmaster
echo "[步骤 1/2] 同步 Spec-Kit → Taskmaster"
echo "----------------------------------------------------------------------"
python3 scripts/speckit-to-taskmaster.py
echo ""

# 步骤 2: Taskmaster → Hamster
echo "[步骤 2/2] 同步 Taskmaster → Hamster"
echo "----------------------------------------------------------------------"
python3 scripts/taskmaster-to-hamster.py
echo ""

# 完成
echo "======================================================================"
echo "✅ 同步完成！"
echo "======================================================================"
echo ""
echo "下一步："
echo "  1. 查看同步报告: cat .taskmaster/docs/speckit-sync-report.md"
echo "  2. 查看哈姆斯特 Markdown: cat .taskmaster/docs/hamster-sync.md"
echo "  3. 复制到 Hamster: cat .taskmaster/docs/hamster-sync.md | xclip -selection clipboard"
echo "  4. 打开 Hamster 粘贴: https://tryhamster.com/home/lwpk110s-team/briefs/226273bf-3756-4262-b47b-d8d0c51e9348/plan"
echo ""
