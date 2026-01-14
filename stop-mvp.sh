#!/bin/bash

# 小芽家教 MVP 停止脚本
# 停止所有前后端服务

echo "========================================="
echo "🛑 停止小芽家教 MVP"
echo "========================================="
echo ""

# 从文件读取 PID
if [ -f ".backend_pid" ]; then
    BACKEND_PID=$(cat .backend_pid)
    echo "停止后端 (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null && echo "✅ 后端已停止" || echo "⚠️  后端未运行"
    rm .backend_pid
fi

if [ -f ".frontend_pid" ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    echo "停止前端 (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null && echo "✅ 前端已停止" || echo "⚠️  前端未运行"
    rm .frontend_pid
fi

# 或者查找并杀死所有相关进程
echo ""
echo "检查残留进程..."

# 杀死 uvicorn 进程
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "✅ 后端进程已清理" || echo "ℹ️  无后端进程"

# 杀死 npm run dev 进程
pkill -f "npm run dev" 2>/dev/null && echo "✅ 前端进程已清理" || echo "ℹ️  无前端进程"

echo ""
echo "========================================="
echo "✅ 所有服务已停止"
echo "========================================="
