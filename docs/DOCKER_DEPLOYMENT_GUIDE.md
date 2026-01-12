# Docker 部署指南

## 概述

本指南提供使用 Docker 和 Docker Compose 部署小芽家教 API 的说明。

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- (可选) Docker Swarm 用于集群部署

## 1. 快速开始

### 1.1 开发环境

```bash
# 构建并启动开发环境
docker-compose -f docker-compose.dev.yml up --build

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f api

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

访问：
- API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 1.2 生产环境

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api

# 停止所有服务
docker-compose down

# 停止并删除卷
docker-compose down -v
```

## 2. 环境变量配置

### 2.1 创建 .env 文件

```bash
cp .env.example .env
```

### 2.2 修改关键配置

```bash
# 生成安全的 SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# 配置 AI API 密钥
OPENAI_API_KEY=your_actual_api_key

# 配置数据库密码
POSTGRES_PASSWORD=your_secure_password
```

### 2.3 使用环境变量文件

```bash
# 从文件加载环境变量
docker-compose --env-file .env up -d
```

## 3. 服务管理

### 3.1 查看服务状态

```bash
# 查看所有服务
docker-compose ps

# 查看资源使用
docker stats

# 查看服务健康状态
docker inspect sprout-chat-api | grep -A 10 Health
```

### 3.2 日志管理

```bash
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs api

# 实时跟踪日志
docker-compose logs -f api

# 查看最近 100 行
docker-compose logs --tail=100 api
```

### 3.3 进入容器

```bash
# 进入 API 容器
docker-compose exec api bash

# 进入数据库容器
docker-compose exec postgres psql -U sprout_user -d sprout_chat

# 进入 Redis 容器
docker-compose exec redis redis-cli
```

### 3.4 重启服务

```bash
# 重启特定服务
docker-compose restart api

# 重启所有服务
docker-compose restart
```

## 4. 数据管理

### 4.1 数据库备份

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U sprout_user sprout_chat > backup_$(date +%Y%m%d).sql

# 从备份恢复
docker-compose exec -T postgres psql -U sprout_user sprout_chat < backup_20250112.sql
```

### 4.2 数据卷管理

```bash
# 查看卷
docker volume ls

# 备份卷
docker run --rm -v sprout-chat_postgres_data:/data -v $(pwd):/backup ubuntu \
  tar czf /backup/postgres_backup.tar.gz /data

# 恢复卷
docker run --rm -v sprout-chat_postgres_data:/data -v $(pwd):/backup ubuntu \
  tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 5. 生产环境优化

### 5.1 资源限制

在 `docker-compose.yml` 中添加：

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 5.2 健康检查优化

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 5.3 日志轮转

```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 6. 监控集成

### 6.1 Prometheus 监控（可选）

添加到 `docker-compose.yml`：

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: sprout-chat-prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - sprout-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: sprout-chat-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    networks:
      - sprout-network
    restart: unless-stopped
```

## 7. 更新部署

### 7.1 滚动更新（零停机）

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build api

# 滚动更新（保持服务运行）
docker-compose up -d --no-deps --build api
```

### 7.2 蓝绿部署（可选）

```bash
# 启动新版本
docker-compose -f docker-compose.yml -p sprout-new up -d

# 切换流量
# (通过负载均衡器或 DNS)

# 停止旧版本
docker-compose -f docker-compose.yml -p sprout-old down
```

## 8. 故障排查

### 8.1 常见问题

**问题 1: 容器无法启动**

```bash
# 查看容器日志
docker-compose logs api

# 检查容器状态
docker-compose ps -a

# 进入容器检查
docker-compose exec api bash
```

**问题 2: 数据库连接失败**

```bash
# 检查数据库是否健康
docker-compose ps postgres

# 测试数据库连接
docker-compose exec postgres pg_isready -U sprout_user

# 查看数据库日志
docker-compose logs postgres
```

**问题 3: 权限错误**

```bash
# 检查文件权限
docker-compose exec api ls -la

# 修复权限
docker-compose exec api chown -R sprout:sprout /home/sprout
```

### 8.2 性能问题

```bash
# 查看容器资源使用
docker stats

# 检查网络延迟
docker-compose exec api ping postgres

# 查看数据库连接数
docker-compose exec postgres psql -U sprout_user -d sprout_chat \
  -c "SELECT count(*) FROM pg_stat_activity;"
```

## 9. 安全最佳实践

### 9.1 镜像安全

```bash
# 使用特定版本标签，避免使用 latest
FROM python:3.12-slim

# 定期更新基础镜像
docker pull python:3.12-slim

# 扫描漏洞
docker scan sprout-chat-api:latest
```

### 9.2 容器安全

```bash
# 以非 root 用户运行
USER sprout

# 只读文件系统
RUN chmod -R 555 /home/sprout

# 限制容器能力
docker-compose run --rm --cap-drop=ALL --cap-add=NET_BIND_SERVICE api
```

### 9.3 网络安全

```yaml
# 使用自定义网络
networks:
  sprout-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 10. CI/CD 集成

### 10.1 GitHub Actions 示例

```yaml
name: Docker Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t sprout-chat-api .

      - name: Log in to Docker Hub
        run: docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }}

      - name: Push to Docker Hub
        run: docker push sprout-chat-api:latest
```

## 11. 生产检查清单

部署前检查：

- [ ] 修改默认 SECRET_KEY
- [ ] 配置强数据库密码
- [ ] 配置 SSL 证书
- [ ] 设置防火墙规则
- [ ] 配置日志监控
- [ ] 设置备份策略
- [ ] 测试健康检查
- [ ] 配置资源限制
- [ ] 测试灾难恢复
- [ ] 配置告警通知

## 支持

- Docker 文档: https://docs.docker.com/
- Docker Compose 文档: https://docs.docker.com/compose/
- 项目文档: `docs/`
