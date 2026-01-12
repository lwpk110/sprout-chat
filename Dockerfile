# 多阶段构建 Dockerfile
# Stage 1: 构建阶段
FROM python:3.12-slim as builder

# 设置工作目录
WORKDIR /build

# 安装系统依赖和构建工具
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements 文件
COPY backend/requirements.txt .

# 安装 Python 依赖到临时目录
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: 运行阶段
FROM python:3.12-slim

# 创建非 root 用户
RUN useradd -m -u 1000 sprout && mkdir -p /home/sprout/app

# 设置工作目录
WORKDIR /home/sprout/app

# 从 builder 阶段复制已安装的包
COPY --from=builder /root/.local /root/.local

# 确保脚本在 PATH 中可用
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY backend/ .

# 创建必要的目录
RUN mkdir -p logs && \
    chown -R sprout:sprout /home/sprout

# 切换到非 root 用户
USER sprout

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
