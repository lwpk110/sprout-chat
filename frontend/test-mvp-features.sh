#!/bin/bash

# 小芽家教 MVP 功能测试脚本
# 用于快速验证前后端功能

set -e

echo "========================================="
echo "🌱 小芽家教 MVP 功能测试"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果
PASS=0
FAIL=0

# 测试函数
test_api() {
    local name=$1
    local url=$2
    local method=$3
    local data=$4

    echo -n "测试: $name ... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -X GET "$url" -H "Content-Type: application/json")
    else
        response=$(curl -s -X "$method" "$url" -H "Content-Type: application/json" -d "$data")
    fi

    if echo "$response" | grep -q "error\|Error\|错误"; then
        echo -e "${RED}失败${NC}"
        echo "  响应: $response"
        FAIL=$((FAIL + 1))
    else
        echo -e "${GREEN}通过${NC}"
        echo "  响应: $response"
        PASS=$((PASS + 1))
    fi
    echo ""
}

# 1. 测试后端服务
echo "========================================="
echo "📡 测试后端服务"
echo "========================================="
echo ""

test_api \
    "创建会话" \
    "http://localhost:8000/api/v1/conversations/create" \
    "POST" \
    '{"student_id":"test_mvp","subject":"数学","student_age":6,"topic":"MVP测试"}'

# 保存 session_id 用于后续测试
SESSION_ID=$(curl -s http://localhost:8000/api/v1/conversations/create \
    -H "Content-Type: application/json" \
    -d '{"student_id":"test_mvp_voice","subject":"数学","student_age":6}' \
    | grep -o '"session_id":"[^"]*"' \
    | cut -d'"' -f4)

echo "会话 ID: $SESSION_ID"
echo ""

test_api \
    "语音输入" \
    "http://localhost:8000/api/v1/conversations/voice" \
    "POST" \
    "{\"session_id\":\"$SESSION_ID\",\"transcript\":\"我想学加法\"}"

test_api \
    "文字输入" \
    "http://localhost:8000/api/v1/conversations/message" \
    "POST" \
    "{\"session_id\":\"$SESSION_ID\",\"content\":\"小芽老师好\"}"

test_api \
    "获取历史" \
    "http://localhost:8000/api/v1/conversations/$SESSION_ID/history" \
    "GET"

test_api \
    "会话统计" \
    "http://localhost:8000/api/v1/conversations/$SESSION_ID/stats" \
    "GET"

# 2. 测试前端服务
echo "========================================="
echo "🌐 测试前端服务"
echo "========================================="
echo ""

echo -n "测试: 前端页面可访问 ... "
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}通过${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}失败${NC}"
    FAIL=$((FAIL + 1))
fi
echo ""

echo -n "测试: 前端包含小芽主题 ... "
if curl -s http://localhost:3000 | grep -q "sprout"; then
    echo -e "${GREEN}通过${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}失败${NC}"
    FAIL=$((FAIL + 1))
fi
echo ""

# 3. 测试文件结构
echo "========================================="
echo "📁 测试文件结构"
echo "========================================="
echo ""

check_file() {
    local file=$1
    echo -n "检查: $file ... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}存在${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}缺失${NC}"
        FAIL=$((FAIL + 1))
    fi
}

check_file "frontend/src/App.tsx"
check_file "frontend/src/pages/StudentHome.tsx"
check_file "frontend/src/components/VoiceInteraction.tsx"
check_file "frontend/src/components/PhotoInteraction.tsx"
check_file "frontend/src/components/GuidedResponse.tsx"
check_file "frontend/src/services/api.ts"
check_file "frontend/src/store/sessionStore.ts"
check_file "frontend/src/types/index.ts"
echo ""

# 4. 总结
echo "========================================="
echo "📊 测试总结"
echo "========================================="
echo ""
echo -e "${GREEN}通过: $PASS${NC}"
echo -e "${RED}失败: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！MVP 已就绪！${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  有 $FAIL 个测试失败，请检查${NC}"
    exit 1
fi
