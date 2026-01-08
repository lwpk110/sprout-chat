# 小芽家教后端 - 部署验证指南

## 验证步骤

### 1. 环境准备

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，添加 ANTHROPIC_API_KEY
# ANTHROPIC_API_KEY=your_key_here
```

### 3. 运行测试

```bash
# 运行单元测试
pytest tests/ -v

# 预期结果：大部分测试应该通过（除了需要真实 API key 的测试）
```

### 4. 启动服务

```bash
# 方式1：使用启动脚本
./start.sh

# 方式2：直接运行
uvicorn app.main:app --reload
```

### 5. 验证 API

#### 健康检查
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "active_sessions": 0,
  "expired_sessions_cleaned": 0
}
```

#### 创建会话
```bash
curl -X POST http://localhost:8000/api/v1/conversations/create \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test_001",
    "subject": "数学",
    "student_age": 6
  }'
```

#### 文字对话（需要 API key）
```bash
curl -X POST http://localhost:8000/api/v1/conversations/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "从创建会话获取",
    "content": "5 + 3 = ?"
  }'
```

### 6. 访问 API 文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心功能验证清单

- [x] 后端项目结构创建
- [x] FastAPI 应用框架搭建
- [x] Claude API 集成服务实现
- [x] 小芽对话引擎 (engine.py) 实现
- [x] 小芽人格 Prompt 模板定义
- [x] 会话管理系统实现
- [x] 对话 API 接口创建
- [x] 基础测试用例编写
- [x] 项目文档完善

## 下一步建议

1. **设置真实的 ANTHROPIC_API_KEY** 以启用 AI 功能
2. **运行完整测试套件** 验证所有功能
3. **开始前端开发** 搭建 React + Tailwind 界面
4. **集成语音识别** 实现前端 Web Speech API
5. **编写更多测试** 提高代码覆盖率

## 项目进度

- Task ID 1 (LWP-1): ✅ **已完成**
  - 语音对话功能后端实现 100%
  - 前端集成待开发

总体项目进度: **~16%** (1/6 任务完成)