# 小芽家教后端服务

面向一年级学生的 AI-First 个性化家教助手 - 后端服务

## 技术栈

- **框架**: FastAPI
- **AI**: Claude API (Anthropic)
- **Python**: 3.9+
- **数据库**: SQLite (可扩展到 PostgreSQL)

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加 API keys
# ANTHROPIC_API_KEY=your_key_here
```

### 3. 运行服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload

# 或者直接运行
python -m app.main
```

服务将在 `http://localhost:8000` 启动

### 4. 访问 API 文档

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API 端点

### 对话管理

- `POST /api/v1/conversations/create` - 创建新会话
- `POST /api/v1/conversations/voice` - 语音输入
- `POST /api/v1/conversations/message` - 文字输入
- `GET /api/v1/conversations/{session_id}/history` - 获取历史
- `GET /api/v1/conversations/{session_id}/stats` - 会话统计
- `DELETE /api/v1/conversations/{session_id}` - 删除会话

### 系统

- `GET /` - 根路径
- `GET /health` - 健康检查

## 核心功能

### 1. 小芽对话引擎

实现了符合"小芽"人格的对话管理：
- 温柔耐心、具象比喻的教学风格
- 苏格拉底式提问，不给答案
- 会话状态管理
- 对话历史追踪

### 2. AI 集成

- Claude API 集成
- 教育场景优化的 Prompt 模板
- 引导式教学逻辑

### 3. 会话管理

- 会话创建与验证
- 超时自动清理（30分钟）
- 对话历史记录（最多10条）

## 测试

```bash
# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_engine.py

# 详细输出
pytest -v
```

## 项目结构

```
backend/
├── app/
│   ├── api/               # API 路由
│   │   └── conversations.py
│   ├── core/              # 核心配置
│   │   └── config.py
│   ├── models/            # 数据模型
│   │   └── schemas.py
│   ├── services/          # 业务逻辑
│   │   ├── engine.py      # 对话引擎
│   │   └── sprout_persona.py  # 小芽人格
│   ├── utils/             # 工具函数
│   └── main.py            # 主应用
├── tests/                 # 测试
│   └── test_engine.py
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量模板
└── README.md             # 本文件
```

## 开发指南

### 代码风格

```bash
# 格式化代码
black .
isort .

# 检查代码质量
flake8
mypy app/
```

### 添加新功能

1. 在 `app/services/` 添加业务逻辑
2. 在 `app/models/schemas.py` 定义数据模型
3. 在 `app/api/` 创建 API 路由
4. 在 `tests/` 添加测试

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ANTHROPIC_API_KEY` | Claude API 密钥 | 必填 |
| `DEBUG` | 调试模式 | `True` |
| `HOST` | 服务器地址 | `0.0.0.0` |
| `PORT` | 服务器端口 | `8000` |
| `AI_MODEL` | AI 模型 | `claude-3-5-sonnet-20241022` |
| `SESSION_TIMEOUT_MINUTES` | 会话超时时间 | `30` |

## 注意事项

1. **API 密钥安全**: 不要将 `.env` 文件提交到版本控制
2. **儿童数据**: 遵守儿童隐私保护法规（COPPA）
3. **响应时间**: 目标是 <3 秒响应时间
4. **教学原则**: 始终使用引导式教学，不给答案

## 许可证

Copyright © 2024 小芽家教项目