"""
CrimeJournal Backend Application
AI-Powered Legal Case Research Platform
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import api_router
from app.middleware.usage import UsageLimitMiddleware
from app.middleware.audit import AuditMiddleware

logger = logging.getLogger(__name__)


# ==================== Lifespan Events ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")

    # 初始化审计日志数据库
    try:
        from app.middleware.audit import init_audit_db
        init_audit_db()
        logger.info("审计日志数据库初始化完成")
    except Exception as e:
        logger.warning(f"审计日志数据库初始化失败: {e}")

    # 预初始化缓存服务（确保 Redis 连接在关闭时能被正确清理）
    try:
        from app.services.cache import CacheService
        cache = CacheService()
        await cache._client.ping()   # 验证连接
        app.state._cache_service = cache
        logger.info("缓存服务初始化完成")
    except Exception as e:
        logger.warning(f"缓存服务初始化失败: {e}")
        app.state._cache_service = None

    # 初始化 AI 服务（MiniMax + DeepSeek）
    try:
        from app.services.ai import MiniMaxService, DeepSeekService, AIRouter
        minimax_service = MiniMaxService(
            api_key=settings.minimax_api_key,
            model=settings.minimax_model,
            base_url=settings.minimax_base_url
        )
        deepseek_service = DeepSeekService(
            api_key=settings.deepseek_api_key,
            model="deepseek-chat",
            base_url=settings.deepseek_base_url
        )
        ai_router = AIRouter(
            minimax_service=minimax_service,
            deepseek_service=deepseek_service
        )
        await ai_router.initialize_all()
        app.state._minimax_service = minimax_service
        app.state._deepseek_service = deepseek_service
        app.state._ai_router = ai_router
        logger.info("AI 路由服务初始化完成（MiniMax + DeepSeek）")
    except Exception as e:
        logger.warning(f"AI 服务初始化失败: {e}")
        app.state._minimax_service = None
        app.state._deepseek_service = None
        app.state._ai_router = None

    yield

    # 关闭时执行
    logger.info("应用关闭中...")

    # 清理所有已初始化的服务
    for attr in dir(app.state):
        if attr.startswith("_") and not attr.startswith("__"):
            obj = getattr(app.state, attr, None)
            if obj is not None and hasattr(obj, "close"):
                try:
                    close_method = obj.close
                    # 判断是 async def close() 还是 def close()
                    import inspect
                    if inspect.iscoroutinefunction(close_method):
                        await obj.close()
                    else:
                        obj.close()
                    logger.info(f"已关闭服务: {attr}")
                except Exception as e:
                    logger.warning(f"关闭服务 {attr} 时出错: {e}")


# ==================== Create FastAPI Application ====================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered legal case research platform with CourtListener integration",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用量限制中间件（记录搜索次数）
app.add_middleware(UsageLimitMiddleware)
# 审计日志中间件（记录所有 API 操作）
app.add_middleware(AuditMiddleware)


# ==================== Register API Routes ====================

# 注册 /api 前缀的路由
app.include_router(api_router, prefix="/api")


# ==================== Root Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
