# 小芽家教 - 后端部署指南

本文档提供小芽家教后端服务的完整部署指南。

## 📋 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [开发环境设置](#开发环境设置)
- [生产环境部署](#生产环境部署)
- [数据库配置](#数据库配置)
- [环境变量](#环境变量)
- [性能优化](#性能优化)
- [安全配置](#安全配置)
- [监控和日志](#监控和日志)
- [故障排查](#故障排查)

---

## 环境要求

### 系统要求

- **操作系统**: Linux (Ubuntu 20.04+ 推荐) / macOS / Windows
- **Python**: 3.11+
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 10GB 可用空间

### 依赖服务

- **数据库**: SQLite (开发) / PostgreSQL 14+ (生产)
- **AI 服务**: Claude API 或智谱 GLM
- **缓存**: Redis (可选，推荐生产环境)

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/lwpk110/sprout-chat.git
cd sprout-chat/backend
```

### 2. 创建虚拟环境

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量：

```bash
# AI Provider
AI_PROVIDER=openai  # 或 zhipu
AI_MODEL=glm-4.7
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# 加密密钥（可选，用于数据加密）
ENCRYPTION_KEY=your-secret-key-min-32-chars

# 调试模式
DEBUG=False
```

### 5. 初始化数据库

```bash
# 使用 SQLite（开发环境）
python -c "from app.models.database import Base; from app.core.config import engine; Base.metadata.create_all(bind=engine)"

# 或使用 PostgreSQL（生产环境）
alembic upgrade head
```

### 6. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 7. 验证部署

访问以下 URL 验证服务运行正常：

- **健康检查**: http://localhost:8000/health
- **API 文档**: http://localhost:8000/docs
- **根路径**: http://localhost:8000/

---

## 开发环境设置

### 安装开发依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果存在
```

### 代码格式化

```bash
# Black
black app/

# isort
isort app/

# Flake8
flake8 app/
```

### 运行测试

```bash
# 所有测试
pytest

# 单个测试文件
pytest tests/test_learning_tracker.py

# 带覆盖率报告
pytest --cov=app --cov-report=html
```

### 开发工具推荐

- **IDE**: VS Code / PyCharm
- **API 测试**: Postman / Insomnia
- **数据库管理**: DBeaver / pgAdmin

---

## 生产环境部署

### 方案 1: 使用 Docker（推荐）

#### 1. 构建 Docker 镜像

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. 构建并运行

```bash
# 构建镜像
docker build -t sprout-chat-backend .

# 运行容器
docker run -d \
  --name sprout-chat \
  -p 8000:8000 \
  --env-file .env \
  sprout-chat-backend
```

### 方案 2: 使用 Systemd（Linux）

#### 1. 创建服务文件

```ini
# /etc/systemd/system/sprout-chat.service
[Unit]
Description=Sprout Chat Backend
After=network.target

[Service]
Type=simple
User=sprout
WorkingDirectory=/opt/sprout-chat/backend
Environment="PATH=/opt/sprout-chat/backend/venv/bin"
ExecStart=/opt/sprout-chat/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 2. 启用服务

```bash
sudo systemctl enable sprout-chat
sudo systemctl start sprout-chat
sudo systemctl status sprout-chat
```

### 方案 3: 使用 Gunicorn + Nginx

#### 1. 安装 Gunicorn

```bash
pip install gunicorn
```

#### 2. 启动 Gunicorn

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### 3. 配置 Nginx 反向代理

```nginx
# /etc/nginx/sites-available/sprout-chat
server {
    listen 80;
    server_name api.sprout-chat.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 数据库配置

### PostgreSQL（生产环境）

#### 1. 安装 PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@14
```

#### 2. 创建数据库和用户

```bash
sudo -u postgres psql

CREATE DATABASE sprout_chat;
CREATE USER sprout_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sprout_chat TO sprout_user;
\q
```

#### 3. 配置连接字符串

在 `.env` 文件中：

```bash
DATABASE_URL=postgresql://sprout_user:your_password@localhost:5432/sprout_chat
```

#### 4. 运行迁移

```bash
alembic upgrade head
```

#### 5. 创建数据库索引

```bash
python -c "
from app.models.database import Base
from app.core.config import engine
Base.metadata.create_all(bind=engine)
print('✅ 数据库表和索引创建成功')
"
```

---

## 环境变量

### 必需变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `AI_PROVIDER` | AI 服务提供商 | `openai` / `zhipu` |
| `AI_MODEL` | AI 模型名称 | `glm-4.7` / `gpt-4` |
| `OPENAI_API_KEY` | API 密钥 | `sk-...` |
| `OPENAI_BASE_URL` | API 基础 URL | `https://api.openai.com/v1/` |

### 可选变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ENCRYPTION_KEY` | 数据加密密钥 | 自动生成 |
| `DEBUG` | 调试模式 | `False` |
| `DATABASE_URL` | 数据库连接 | SQLite |
| `REDIS_URL` | Redis 连接 | 无 |
| `LOG_LEVEL` | 日志级别 | `INFO` |

---

## 性能优化

### 1. 数据库优化

已实现的优化：
- ✅ 9 个索引
- ✅ 3 个唯一约束
- ✅ 复合索引优化查询

额外优化建议：
- 使用连接池（SQLAlchemy 默认）
- 启用查询缓存
- 定期 VACUUM（PostgreSQL）

### 2. 应用优化

```bash
# 使用多 Worker
uvicorn app.main:app --workers 4

# 调整 Worker 类型
uvicorn app.main:app --worker-class uvicorn.workers.UvicornWorker
```

### 3. 缓存策略

```python
# 可选：集成 Redis
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param):
    # ...
    pass
```

---

## 安全配置

### 1. 数据加密

启用学生答案加密：

```python
# app/models/database.py
from app.utils.encryption import EncryptedString

class LearningRecord(Base):
    # ...
    student_answer = Column(EncryptedString(1000))
```

### 2. CORS 配置

```python
# app/core/config.py
cors_origins_list = [
    "https://sprout-chat.com",
    "https://api.sprout-chat.com"
]
```

### 3. API 认证

```python
# 添加 JWT 认证
# app/api/auth.py
```

---

## 监控和日志

### 1. 日志配置

```python
# .env
LOG_LEVEL=INFO
LOG_FILE=/var/log/sprout-chat/app.log
```

### 2. 健康检查

```bash
curl http://localhost:8000/health
```

预期响应：

```json
{
  "status": "healthy",
  "active_sessions": 10,
  "expired_sessions_cleaned": 5
}
```

### 3. 性能监控

建议工具：
- **Sentry**: 错误追踪
- **Prometheus**: 指标收集
- **Grafana**: 可视化仪表板

---

## 故障排查

### 常见问题

#### 1. 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
sudo systemctl status postgresql

# 检查连接
psql -U sprout_user -d sprout_chat
```

#### 3. AI API 调用失败

```bash
# 检查 API 密钥
echo $OPENAI_API_KEY

# 测试 API 连接
python -c "
from app.core.config import settings
print(f'Provider: {settings.ai_provider}')
print(f'Model: {settings.ai_model}')
"
```

#### 4. 内存不足

```bash
# 检查内存使用
free -h

# 减少 Worker 数量
uvicorn app.main:app --workers 2
```

---

## 部署检查清单

部署前检查：

- [ ] 环境变量已配置
- [ ] 数据库已初始化
- [ ] 索引已创建
- [ ] API 密钥有效
- [ ] 防火墙规则已配置
- [ ] 日志目录已创建
- [ ] 备份策略已设置
- [ ] 监控已配置

部署后验证：

- [ ] 服务启动成功
- [ ] 健康检查通过
- [ ] API 文档可访问
- [ ] 数据库连接正常
- [ ] AI API 调用成功
- [ ] 日志正常输出

---

## 维护

### 定期任务

**每日**:
- 检查错误日志
- 验证服务运行状态
- 检查磁盘空间

**每周**:
- 数据库备份
- 清理旧日志
- 性能指标审查

**每月**:
- 安全更新
- 依赖升级
- 容量规划

---

## 支持

如遇问题，请查看：
- **项目文档**: [README.md](README.md)
- **开发指南**: [docs/development-guide.md](docs/development-guide.md)
- **问题反馈**: [GitHub Issues](https://github.com/lwpk110/sprout-chat/issues)

---

**最后更新**: 2026-01-13
