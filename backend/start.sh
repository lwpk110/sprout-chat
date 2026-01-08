#!/bin/bash

# 小芽家教后端启动脚本

echo "🌱 小芽家教后端服务启动中..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -q -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在，从 .env.example 复制..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件添加 API keys"
fi

# 运行服务
echo "启动服务..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000