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
    description="面向一年级学生的 AI-First 个性化家教助手",
    version=settings.app_version,
    lifespan=lifespan
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