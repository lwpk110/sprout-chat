#!/bin/bash

# 小芽家教 - 完整开发环境启动脚本

echo "🌱 小芽家教 - 启动完整开发环境"
echo "================================"
echo ""

# 检查依赖
echo "🔍 检查系统依赖..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ 错误: Node.js 未安装"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ 错误: npm 未安装"
    exit 1
fi

echo "✅ Python: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo ""

# 启动后端
echo "🚀 启动后端服务..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（如果需要）
if [ ! -f ".deps_installed" ]; then
    echo "📦 安装 Python 依赖..."
    pip install -q -r requirements.txt
    touch .deps_installed
fi

# 启动后端（在后台）
echo "✅ 后端服务启动中 (http://localhost:8000)"
uvicorn app.main:app --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"
cd ..

# 等待后端启动
echo "⏳ 等待后端服务就绪..."
sleep 3

# 检查后端是否成功启动
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ 后端服务已就绪"
else
    echo "❌ 后端启动失败，请查看 backend.log"
    exit 1
fi

echo ""

# 启动前端
echo "🚀 启动前端服务..."
cd frontend

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装 Node 依赖..."
    npm install
fi

echo "✅ 前端服务启动中 (http://localhost:3000)"
echo ""
echo "================================"
echo "🎉 开发环境已就绪！"
echo "================================"
echo ""
echo "📍 前端地址: http://localhost:3000"
echo "📍 后端 API: http://localhost:8000"
echo "📍 API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 启动前端（前台）
npm run dev

# 清理：当用户按 Ctrl+C 时
echo ""
echo "🛑 停止服务..."
kill $BACKEND_PID 2>/dev/null
echo "✅ 后端服务已停止"
