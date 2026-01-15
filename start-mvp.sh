#!/bin/bash

###############################################################################
# 小芽家教 MVP 快速启动脚本
#
# 用途：一键启动前端和后端开发服务器
# 使用：./start-mvp.sh
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🌱 小芽家教 MVP - 快速启动${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 启动后端
cd backend
echo -e "${BLUE}启动后端服务 (http://localhost:8000)...${NC}"
nohup python -m uvicorn app.main:app --reload --port 8000 > /tmp/sprout-backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/sprout-backend.pid
echo -e "${GREEN}✓ 后端 PID: $BACKEND_PID${NC}"

sleep 3

# 启动前端
cd ../frontend
echo -e "${BLUE}启动前端服务 (http://localhost:3000)...${NC}"
nohup npm run dev > /tmp/sprout-frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/sprout-frontend.pid
echo -e "${GREEN}✓ 前端 PID: $FRONTEND_PID${NC}"

sleep 3

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 所有服务启动成功！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}🌱 小芽家教 MVP 已启动：${NC}"
echo -e "  📱 前端: ${GREEN}http://localhost:3000${NC}"
echo -e "  🔧 后端: ${GREEN}http://localhost:8000${NC}"
echo -e "  📚 API 文档: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}🛑 停止服务：${NC}"
echo -e "  运行: ${GREEN}./stop-mvp.sh${NC}"
echo -e "  或手动: kill $BACKEND_PID $FRONTEND_PID"
echo ""
