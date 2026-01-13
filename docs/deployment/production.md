# 生产环境部署指南

## 概述

本指南提供小芽家教 (SproutChat) 后端 API 的生产环境部署说明。

## 前置要求

- Python 3.12+
- PostgreSQL 14+ (生产环境)
- Redis 6+ (可选，用于缓存)
- Nginx (反向代理，推荐)
- SSL 证书 (HTTPS，生产环境必须)

## 1. 环境变量配置

### 1.1 创建 .env 文件

```bash
cp .env.example .env
```

### 1.2 修改关键配置

```bash
# 生产环境必须修改的配置
ENVIRONMENT=production
DEBUG=false

# 数据库配置（PostgreSQL）
DATABASE_URL=postgresql://user:password@localhost:5432/sprout_chat
DB_HOST=your-db-host.example.com
DB_PORT=5432
DB_USER=sprout_user
DB_PASSWORD=your_secure_password_here
DB_NAME=sprout_chat

# 安全密钥（使用 openssl 生成）
SECRET_KEY=$(openssl rand -hex 32)

# CORS 配置
FRONTEND_URL=https://your-frontend-domain.com

# AI API 密钥
OPENAI_API_KEY=your_actual_api_key
```

### 1.3 生成安全密钥

```bash
# 生成 JWT 密钥
openssl rand -hex 32

# 或使用 Python
python -c "import secrets; print(secrets.token_hex(32))"
```

## 2. 数据库设置

### 2.1 创建 PostgreSQL 数据库

```sql
-- 连接到 PostgreSQL
psql -U postgres

-- 创建数据库和用户
CREATE DATABASE sprout_chat;
CREATE USER sprout_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE sprout_chat TO sprout_user;

-- 退出
\q
```

### 2.2 运行数据库迁移

```bash
# 激活虚拟环境
source venv/bin/activate

# 创建数据库表
python -c "from app.models.database import engine; from app.models.database import Base; Base.metadata.create_all(engine)"
```

## 3. 应用部署

### 3.1 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 或使用 poetry
poetry install
```

### 3.2 生产依赖

确保 `requirements.txt` 包含：

```txt
fastapi==0.128.0
uvicorn[standard]
psycopg2-binary
python-multipart
python-jose[cryptography]
passlib[bcrypt]
pydantic
pydantic-settings
sqlalchemy
```

### 3.3 使用 systemd 服务（推荐）

创建 `/etc/systemd/system/sprout-chat.service`:

```ini
[Unit]
Description=SproutChat API
After=network.target postgresql.service

[Service]
Type=notify
User=sprout
Group=sprout
WorkingDirectory=/var/www/sprout-chat/backend
Environment="PATH=/var/www/sprout-chat/venv/bin"
ExecStart=/var/www/sprout-chat/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start sprout-chat

# 设置开机自启
sudo systemctl enable sprout-chat

# 查看状态
sudo systemctl status sprout-chat

# 查看日志
sudo journalctl -u sprout-chat -f
```

### 3.4 使用 Gunicorn（生产级 WSGI）

安装 Gunicorn：

```bash
pip install gunicorn
```

启动命令：

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info
```

## 4. Nginx 反向代理

### 4.1 配置 Nginx

创建 `/etc/nginx/sites-available/sprout-chat`:

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 日志
    access_log /var/log/nginx/sprout-chat-access.log;
    error_log /var/log/nginx/sprout-chat-error.log;

    # 反向代理到 FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API 文档（可选：限制访问）
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        # 允许特定 IP 访问
        # allow 1.2.3.4;
        # deny all;
    }
}
```

启用配置：

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/sprout-chat /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

## 5. SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.example.com

# 自动续期
sudo certbot renew --dry-run
```

## 6. 监控和日志

### 6.1 日志配置

确保 `.env` 中配置：

```bash
LOG_LEVEL=INFO
LOG_FILE=logs/sprout_chat.log
LOG_ROTATION=true
```

### 6.2 Sentry 错误追踪（可选）

```bash
# 安装 Sentry SDK
pip install sentry-sdk

# 配置 .env
SENTRY_DSN=your-sentry-dsn-here
```

在 `app/main.py` 中初始化：

```python
import sentry_sdk

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    traces_sample_rate=1.0,
)
```

## 7. 安全检查清单

- [ ] 修改默认 SECRET_KEY
- [ ] 配置强密码（数据库、API 密钥）
- [ ] 启用 HTTPS
- [ ] 配置 CORS 白名单
- [ ] 关闭 DEBUG 模式
- [ ] 设置 ALLOWED_HOSTS
- [ ] 启用速率限制
- [ ] 配置防火墙
- [ ] 定期备份数据库
- [ ] 配置日志监控

## 8. 性能优化

### 8.1 使用缓存（可选）

```bash
# 安装 Redis
sudo apt-get install redis-server

# 配置 .env
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

### 8.2 数据库连接池

在 `app/models/database.py` 中配置：

```python
engine = create_engine(
    settings.database_url_resolved,
    pool_size=20,  # 连接池大小
    max_overflow=40,  # 最大溢出连接
    pool_pre_ping=True,  # 连接健康检查
)
```

### 8.3 Gunicorn Workers 配置

```bash
# 推荐：(2 x $num_cores) + 1
gunicorn app.main:app --workers 9 --worker-class uvicorn.workers.UvicornWorker
```

## 9. 备份策略

### 9.1 数据库备份

```bash
# 创建备份脚本
cat > backup.sh << 'SCRIPT'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U sprout_user sprout_chat > backups/sprout_chat_$DATE.sql
# 保留最近 7 天的备份
find backups/ -name "sprout_chat_*.sql" -mtime +7 -delete
SCRIPT

chmod +x backup.sh

# 添加到 crontab（每天凌晨 2 点）
crontab -e
# 0 2 * * * /path/to/backup.sh
```

### 9.2 应用代码备份

```bash
# 使用 Git 备份
git push origin main
```

## 10. 故障排查

### 10.1 查看应用日志

```bash
# Systemd 服务
sudo journalctl -u sprout-chat -n 100

# 应用日志
tail -f logs/sprout_chat.log

# Nginx 日志
tail -f /var/log/nginx/sprout-chat-error.log
```

### 10.2 常见问题

**问题 1: 数据库连接失败**
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 测试连接
psql -U sprout_user -h localhost -d sprout_chat
```

**问题 2: 端口已被占用**
```bash
# 查看端口占用
sudo lsof -i :8000

# 杀死进程
sudo kill -9 <PID>
```

**问题 3: 权限错误**
```bash
# 确保文件权限正确
sudo chown -R sprout:sprout /var/www/sprout-chat
```

## 11. 更新部署

```bash
# 拉取最新代码
cd /var/www/sprout-chat
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart sprout-chat

# 检查状态
sudo systemctl status sprout-chat
```

## 12. 健康检查

配置健康检查端点：

```bash
# 检查应用健康
curl https://api.example.com/health

# 预期响应
{
  "status": "healthy",
  "service": "小芽家教 API",
  "version": "0.1.0"
}
```

## 支持

如有问题，请查看：
- 项目文档: `docs/`
- API 文档: https://api.example.com/docs
- GitHub Issues: https://github.com/lwpk110/sprout-chat/issues
