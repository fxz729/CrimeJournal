"""
API Routes Package

提供案件、认证、搜索等API路由
"""

from fastapi import APIRouter

from .cases import router as cases_router
from .auth import router as auth_router
from .search import router as search_router

# 创建主API路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(cases_router, prefix="/cases", tags=["cases"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(search_router, tags=["search"])

__all__ = [
    "api_router",
    "cases_router",
    "auth_router",
    "search_router",
]
