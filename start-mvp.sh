#!/bin/bash

# 小芽家教 MVP 快速启动脚本
# 一键启动前后端服务

set -e

echo "========================================="
echo "🌱 小芽家教 MVP - 快速启动"
echo "========================================="
echo ""

# 检查依赖
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 错误: $1 未安装"
        exit 1
    fi
}

echo "🔍 检查依赖..."
check_command python3
check_command npm
echo "✅ 依赖检查完成"
echo ""

# 启动后端
echo "========================================="
echo "🚀 启动后端服务 (FastAPI)"
echo "========================================="
echo ""

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
if [ ! -f "venv/.installed" ]; then
    echo "安装 Python 依赖..."
    pip install -q -r requirements.txt
    touch venv/.installed
fi

# 启动后端（后台运行）
echo "启动后端服务器 (端口 8000)..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 等待后端启动
echo "等待后端启动..."
sleep 5

# 测试后端
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ 后端启动成功"
else
    echo "❌ 后端启动失败"
    cat ../backend.log
    exit 1
fi

cd ..
echo ""

# 启动前端
echo "========================================="
echo "🚀 启动前端服务 (React + Vite)"
echo "========================================="
echo ""

cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装 NPM 依赖..."
    npm install --silent
fi

# 启动前端（后台运行）
echo "启动前端服务器 (端口 3000)..."
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"

# 等待前端启动
echo "等待前端启动..."
sleep 5

# 测试前端
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 前端启动成功"
else
    echo "⏳ 前端正在启动中..."
fi

cd ..
echo ""

# 保存 PID 到文件
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

# 完成
echo "========================================="
echo "✅ MVP 启动完成！"
echo "========================================="
echo ""
echo "📱 前端地址: http://localhost:3000"
echo "📡 后端文档: http://localhost:8000/docs"
echo ""
echo "📝 日志文件:"
echo "  - 后端: backend.log"
echo "  - 前端: frontend.log"
echo ""
echo "🛑 停止服务:"
echo "  - 运行: ./stop-mvp.sh"
echo "  - 或: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "🌱 开始使用小芽家教吧！"
echo "========================================="
