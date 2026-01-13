#!/bin/bash
# 小芽家教 MVP 一键启动脚本

set -e

echo "🌱 小芽家教 - MVP 启动脚本"
echo "================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查后端是否运行
echo -e "${BLUE}检查后端服务...${NC}"
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务已运行 (http://localhost:8000)${NC}"
else
    echo -e "${YELLOW}⚠ 后端服务未运行，正在启动...${NC}"
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    cd ..
    sleep 2
fi

# 检查前端是否运行
echo -e "${BLUE}检查前端服务...${NC}"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端服务已运行 (http://localhost:3000)${NC}"
else
    echo -e "${YELLOW}⚠ 前端服务未运行，正在启动...${NC}"
    cd frontend

    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}首次运行，正在安装依赖...${NC}"
        npm install
    fi

    npm run dev &
    FRONTEND_PID=$!
    echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
    cd ..
    sleep 2
fi

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}🎉 MVP 服务已全部启动！${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "📍 访问地址："
echo -e "   • 前端界面: ${BLUE}http://localhost:3000${NC}"
echo -e "   • 后端 API: ${BLUE}http://localhost:8000${NC}"
echo -e "   • API 文档: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "💡 使用提示："
echo -e "   • 按 Ctrl+C 停止所有服务"
echo -e "   • 查看完整文档: cat FRONTEND_MVP.md"
echo ""

# 保持脚本运行
trap "echo ''; echo '正在停止所有服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
