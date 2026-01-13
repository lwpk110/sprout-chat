#!/bin/bash
# 快速启动前端 MVP

echo "🌱 启动小芽家教前端 MVP..."
echo ""

cd "$(dirname "$0")"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，安装依赖中..."
    npm install
fi

echo "🚀 启动开发服务器..."
echo ""
echo "✨ 服务将在 http://localhost:3000 启动"
echo "📱 使用浏览器打开即可访问"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev
