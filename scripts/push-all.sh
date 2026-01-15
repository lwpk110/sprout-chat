#!/bin/bash
# 一键推送到 GitHub 和 Gitee

set -e

BRANCH=${1:-main}

echo "🚀 开始推送到所有仓库..."
echo "📌 当前分支: $BRANCH"
echo ""

# 推送到 GitHub
echo "📦 推送到 GitHub..."
git push origin $BRANCH
echo "✅ GitHub 推送完成"
echo ""

# 推送到 Gitee
echo "📦 推送到 Gitee..."
git push gitee $BRANCH
echo "✅ Gitee 推送完成"
echo ""

echo "🎉 所有仓库推送完成！"
