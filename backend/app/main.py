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

logger = logging.getLogger(__name__)


# ==================== Lifespan Events ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")

    # TODO: 初始化数据库连接
    # TODO: 初始化AI服务
    # TODO: 初始化Redis连接

    yield

    # 关闭时执行
    logger.info("应用关闭中...")

    # TODO: 关闭数据库连接
    # TODO: 关闭AI服务
    # TODO: 关闭Redis连接


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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用量限制中间件（记录搜索次数）
app.add_middleware(UsageLimitMiddleware)


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
