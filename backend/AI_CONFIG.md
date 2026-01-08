# 小芽家教 - AI 配置指南

## 支持的 AI 提供商

小芽家教后端现支持两种 AI 提供商：

### 1. **Anthropic Claude** (默认)
- 模型: Claude 3.5 Sonnet
- 适合: 教育场景优化

### 2. **智谱 GLM** (OpenAI 兼容)
- 模型: GLM-4.7, GLM-4-Plus, GLM-4-Air 等
- 适合: 国内部署、成本优化

## 配置步骤

### 方式一：使用智谱 GLM（推荐）

1. **编辑 `.env` 文件**:
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=你的智谱API密钥
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
AI_MODEL=glm-4.7
```

2. **可选的 GLM 模型**:
- `glm-4.7` - 最新版本（推荐）
- `glm-4-plus` - 增强版
- `glm-4-air` - 轻量版
- `glm-4-flash` - 快速版

### 方式二：使用 Anthropic Claude

1. **编辑 `.env` 文件**:
```bash
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=你的Claude_API密钥
AI_MODEL=claude-3-5-sonnet-20241022
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `AI_PROVIDER` | AI 提供商选择 | `anthropic` |
| `OPENAI_API_KEY` | 智谱 API 密钥 | - |
| `OPENAI_BASE_URL` | 智谱 API 端点 | `https://open.bigmodel.cn/api/paas/v4/` |
| `AI_MODEL` | 模型名称 | - |
| `AI_MAX_TOKENS` | 最大 token 数 | `1000` |
| `AI_TEMPERATURE` | 温度参数 | `0.7` |

## 获取 API 密钥

### 智谱 GLM
1. 访问: https://open.bigmodel.cn/
2. 注册/登录账号
3. 在控制台获取 API Key
4. 格式: `xxxxxx.Pk8x9c4nrtIitnWv`

### Anthropic Claude
1. 访问: https://console.anthropic.com/
2. 注册/登录账号
3. 在 API Keys 页面创建密钥
4. 格式: `sk-ant-api03-...`

## 验证配置

### 1. 测试基础连接
```bash
curl http://localhost:8000/health
```

### 2. 测试对话功能
```bash
# 创建会话
curl -X POST http://localhost:8000/api/v1/conversations/create \
  -H "Content-Type: application/json" \
  -d '{"student_id":"test","subject":"数学","student_age":6}'

# 发送消息
curl -X POST http://localhost:8000/api/v1/conversations/message \
  -H "Content-Type: application/json" \
  -d '{"session_id":"从上一步获取","content":"5 + 3 = ?"}'
```

### 3. 查看日志
```bash
# 查看服务器日志
tail -f /tmp/claude/-home-luwei-workspace-github-sprout-chat/tasks/*.output
```

## 切换提供商

### 从 Claude 切换到智谱 GLM
```bash
# .env 文件
AI_PROVIDER=openai
OPENAI_API_KEY=你的智谱密钥
AI_MODEL=glm-4.7
```

### 从智谱 GLM 切换到 Claude
```bash
# .env 文件
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=你的Claude密钥
AI_MODEL=claude-3-5-sonnet-20241022
```

## 故障排查

### 问题 1: API 密钥错误
```
错误: Authentication failed
解决: 检查 API_KEY 是否正确，确保没有多余空格
```

### 问题 2: 模型不存在
```
错误: Model not found
解决: 检查 AI_MODEL 拼写，参考上面的模型列表
```

### 问题 3: 连接超时
```
错误: Connection timeout
解决: 检查 OPENAI_BASE_URL 是否正确，确保网络可访问
```

## 成本对比

| 提供商 | 模型 | 输入成本 | 输出成本 |
|--------|------|----------|----------|
| 智谱 GLM | glm-4.7 | ¥0.5/百万tokens | ¥0.5/百万tokens |
| Claude | claude-3-5-sonnet | $3/百万tokens | $15/百万tokens |

*价格仅供参考，请以官方定价为准*

## 最佳实践

1. **开发阶段**: 使用 GLM-4-Flash（快速且便宜）
2. **测试阶段**: 使用 GLM-4-Air（性价比高）
3. **生产环境**: 使用 GLM-4.7 或 Claude 3.5 Sonnet（质量最佳）

## 技术实现

代码自动根据 `AI_PROVIDER` 环境变量选择相应的客户端：

```python
if settings.ai_provider == "openai":
    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url
    )
else:
    client = anthropic.Anthropic(
        api_key=settings.anthropic_api_key
    )
```

## 安全提示

⚠️ **重要**:
- 不要将 `.env` 文件提交到 Git 仓库
- 生产环境使用环境变量或密钥管理服务
- 定期轮换 API 密钥
- 监控 API 使用量和成本