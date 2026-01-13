#!/bin/bash

# 小芽家教前端 MVP - 功能测试脚本

echo "=========================================="
echo "小芽家教前端 MVP - 功能测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
PASSED=0
FAILED=0

# 测试函数
test_service() {
    local name=$1
    local url=$2
    local keyword=$3

    echo -n "测试 $name... "

    response=$(curl -s "$url" 2>&1)

    if echo "$response" | grep -q "$keyword"; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        ((FAILED++))
        return 1
    fi
}

# 1. 测试后端 API
echo "【1/4】测试后端 API"
test_service "后端服务" "http://localhost:8000/docs" "swagger-ui"
echo ""

# 2. 测试前端服务
echo "【2/4】测试前端服务"
test_service "前端页面" "http://localhost:3001" "html"
echo ""

# 3. 测试 API 端点
echo "【3/4】测试 API 端点"
test_service "会话创建 API" "http://localhost:8000/api/v1/conversations/create" "session_id"
echo ""

# 4. 检查必需的文件
echo "【4/4】检查必需文件"
files=(
    "frontend/src/App.tsx"
    "frontend/src/pages/StudentHome.tsx"
    "frontend/src/components/VoiceInteraction.tsx"
    "frontend/src/components/PhotoInteraction.tsx"
    "frontend/src/components/GuidedResponse.tsx"
    "frontend/src/store/sessionStore.ts"
    "frontend/src/services/api.ts"
)

for file in "${files[@]}"; do
    echo -n "检查 $file... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ 存在${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ 缺失${NC}"
        ((FAILED++))
    fi
done

echo ""
echo "=========================================="
echo "测试结果"
echo "=========================================="
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    echo ""
    echo "立即访问前端 MVP："
    echo -e "${YELLOW}http://localhost:3001${NC}"
    echo ""
    echo "后端 API 文档："
    echo -e "${YELLOW}http://localhost:8000/docs${NC}"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败，请检查${NC}"
    exit 1
fi
