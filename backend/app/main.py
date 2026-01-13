"""
小芽家教 - FastAPI 主应用

面向一年级学生的 AI-First 个性化家教助手
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.conversations import router as conversations_router
from app.api.images import router as images_router
from app.api.learning import router as learning_router
from app.api.parental import router as parental_router
from app.api.auth import router as auth_router
from app.api.teaching import router as teaching_router
from app.api.wrong_answers import router as wrong_answers_router
from app.api.knowledge import router as knowledge_router
from app.api.knowledge import mastery_router as knowledge_mastery_router
from app.api.socratic import router as socratic_router
from app.api.scaffolding import router as scaffolding_router
from app.api.validation import router as validation_router
from app.api.parent_reports import router as parent_reports_router
from app.api.parental_settings import router as parental_settings_router
from app.api.multi_subject import router as multi_subject_router
from app.services.engine import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🌱 {settings.app_name} v{settings.app_version} 启动中...")
    print(f"📝 当前模式: {'开发' if settings.debug else '生产'}")
    yield
    # 关闭时
    print(f"🌙 {settings.app_name} 正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description="""
## 小芽家教 (SproutChat) API

面向一年级学生的 AI-First 个性化家教助手。

### 核心功能

- **学习记录追踪**: 记录学生的学习活动，追踪学习进度
- **苏格拉底式教学**: 通过引导式提问帮助学生思考，而非直接给答案
- **错题本管理**: 智能分类错误类型，提供针对性练习推荐
- **知识点图谱**: 追踪知识点掌握程度，生成个性化学习路径

### 技术栈

- **后端**: Python FastAPI
- **AI 服务**: Claude API / 智谱 GLM
- **数据库**: SQLite (开发) / PostgreSQL (生产)

### 认证

大部分 API 端点需要 Bearer Token 认证。请在请求头中包含：
```
Authorization: Bearer <your_token>
```

### 错误处理

API 使用标准 HTTP 状态码：
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `404`: 资源不存在
- `500`: 服务器错误

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```
""",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "学习记录",
            "description": "学习活动记录和进度追踪"
        },
        {
            "name": "苏格拉底教学",
            "description": "引导式教学和反馈生成"
        },
        {
            "name": "错题本",
            "description": "错题管理和练习推荐"
        },
        {
            "name": "知识点图谱",
            "description": "知识点追踪和掌握度分析"
        },
        {
            "name": "认证",
            "description": "用户注册和登录"
        },
        {
            "name": "对话",
            "description": "师生对话交互"
        },
        {
            "name": "图像识别",
            "description": "题目图片识别"
        },
        {
            "name": "家长监控",
            "description": "学习数据查看和统计"
        }
    ]
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(conversations_router)
app.include_router(images_router)
app.include_router(learning_router)
app.include_router(parental_router)
app.include_router(auth_router)
app.include_router(teaching_router)
app.include_router(wrong_answers_router)
app.include_router(knowledge_router)
app.include_router(knowledge_mastery_router)
app.include_router(socratic_router)
app.include_router(scaffolding_router)
app.include_router(validation_router)
app.include_router(parent_reports_router)
app.include_router(parental_settings_router)
app.include_router(multi_subject_router)


@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "message": "欢迎来到小芽家教！🌱"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """健康检查"""
    # 清理过期会话
    expired_count = engine.cleanup_expired_sessions()

    return {
        "status": "healthy",
        "active_sessions": len(engine.conversations),
        "expired_sessions_cleaned": expired_count
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )