#!/bin/bash

# 小芽家教前端开发启动脚本

echo "🌱 小芽家教 - 前端开发环境"
echo "================================"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: Node.js 未安装"
    echo "请访问 https://nodejs.org/ 安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo "✅ npm 版本: $(npm --version)"
echo ""

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
    echo ""
fi

# 检查后端是否运行
echo "🔍 检查后端服务..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ 后端服务运行中 (http://localhost:8000)"
else
    echo "⚠️  警告: 后端服务未运行"
    echo "请先启动后端服务:"
    echo "  cd ../backend"
    echo "  uvicorn app.main:app --reload"
    echo ""
    read -p "是否继续启动前端? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🚀 启动前端开发服务器..."
echo "================================"
npm run dev
