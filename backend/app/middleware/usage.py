"""
Usage Limit Middleware

搜索频率限制中间件
- Free 用户：每天 10 次搜索
- Pro 用户：无限制
- 用量存储在内存中（生产环境需要数据库）

每日凌晨自动重置计数器
"""

import logging
from datetime import datetime, date
from collections import defaultdict
from typing import Callable, Optional
from threading import Lock

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse

from app.api.auth import get_optional_user
from app.config import settings

logger = logging.getLogger(__name__)

# ==================== In-Memory Usage Tracking ====================
# TODO: 后续集成真实数据库

# 用量存储: user_id -> { "YYYY-MM-DD": count }
_usage_db: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))

# 每日限制配置
DAILY_SEARCH_LIMITS = {
    "free": 10,
    "pro": -1,       # unlimited
    "enterprise": -1,  # unlimited
}

# 最近检查过的用户（用于调试/日志）
_last_checked: dict[int, str] = {}

# 线程安全锁
_usage_lock = Lock()


# ==================== Usage Tracking Functions ====================

def get_today_str() -> str:
    """获取今天的日期字符串"""
    return date.today().isoformat()


def get_user_daily_usage(user_id: int) -> int:
    """获取用户今日搜索次数"""
    today_str = get_today_str()
    return _usage_db[user_id].get(today_str, 0)


def increment_user_usage(user_id: int) -> int:
    """增加用户今日搜索次数，返回新的计数"""
    today_str = get_today_str()
    with _usage_lock:
        _usage_db[user_id][today_str] += 1
        return _usage_db[user_id][today_str]


def get_daily_limit(subscription_tier: str) -> int:
    """获取用户每日搜索限制"""
    return DAILY_SEARCH_LIMITS.get(subscription_tier, DAILY_SEARCH_LIMITS["free"])


def check_and_record_search(user_id: int, subscription_tier: str) -> tuple[bool, str, int, int]:
    """
    检查并记录搜索

    返回: (是否允许, 错误消息, 当前用量, 每日限制)

    如果用户未登录（anonymous），不限制但也不记录
    """
    if user_id is None:
        # 未登录用户，不限制
        return True, "", 0, 0

    daily_limit = get_daily_limit(subscription_tier)

    # -1 表示无限制
    if daily_limit == -1:
        # Pro/Enterprise 用户，记录但不限制
        count = increment_user_usage(user_id)
        return True, "", count, -1

    current_usage = get_user_daily_usage(user_id)

    if current_usage >= daily_limit:
        return False, f"Daily search limit reached ({current_usage}/{daily_limit})", current_usage, daily_limit

    # 记录搜索
    count = increment_user_usage(user_id)
    return True, "", count, daily_limit


def cleanup_old_entries():
    """
    清理过期的用量记录

    保留最近 7 天的数据，删除更旧的记录
    生产环境应该在数据库层面处理，或使用 TTL
    """
    from datetime import timedelta
    cutoff = (date.today() - timedelta(days=7)).isoformat()

    with _usage_lock:
        for user_id in list(_usage_db.keys()):
            user_usage = _usage_db[user_id]
            keys_to_delete = [k for k in user_usage if k < cutoff]
            for k in keys_to_delete:
                del user_usage[k]

            # 如果用户没有数据了，删除用户条目
            if not user_usage:
                del _usage_db[user_id]


# ==================== ASGI Middleware ====================
# 注意：FastAPI 路径参数可能需要从请求中获取 user_id


class UsageLimitMiddleware(BaseHTTPMiddleware):
    """
    用量限制中间件

    在每次搜索请求时检查用户用量
    - 只限制 /api/cases/search 端点
    - 未登录用户不受限制（但也不记录用量）
    - Free 用户每日限制 10 次
    - Pro/Enterprise 用户无限制

    注意：当前实现仅记录用量，实际限制在 cases.py 的 search_cases 端点中
    这个中间件主要用于在请求级别做初步过滤和日志记录
    """

    # 需要检查用量的路径模式
    PROTECTED_PATHS = [
        "/api/cases/search",
    ]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 只检查特定路径
        path = request.url.path

        # 检查是否是搜索路径
        is_search = any(path.startswith(p) for p in self.PROTECTED_PATHS)

        if not is_search:
            return await call_next(request)

        # 获取认证信息（可选）
        # 注意：这里使用 Starlette 的方式获取 header
        # 实际 token 验证在端点层通过 Depends 实现
        auth_header = request.headers.get("authorization", "")

        if not auth_header.startswith("Bearer "):
            # 未登录用户，不记录用量
            return await call_next(request)

        try:
            # 解析 token 获取用户信息
            from app.api.auth import decode_token
            token = auth_header.replace("Bearer ", "")
            payload = decode_token(token)
            user_id = int(payload.get("sub"))
            email = payload.get("email")

            # 记录搜索（用于统计）
            increment_user_usage(user_id)
            _last_checked[user_id] = f"{get_today_str()} {datetime.utcnow().isoformat()}"

            logger.debug(
                f"Usage tracked - user {email}: "
                f"today={get_user_daily_usage(user_id)}"
            )

        except Exception as e:
            # Token 解析失败，不记录（也不阻止请求）
            logger.debug(f"Usage tracking skipped: {str(e)}")

        return await call_next(request)


# ==================== Endpoint-Level Usage Check ====================
# 在 cases.py 中使用的辅助函数


def check_search_access(user_id: int, subscription_tier: str) -> None:
    """
    在搜索端点中检查访问权限

    如果超过限制，抛出 HTTPException

    用法（在 cases.py 中）：
    ```
    async def search_cases(
        ...,
        current_user: Optional[dict] = Depends(get_optional_user),
    ):
        if current_user:
            user_id = current_user["id"]
            # 需要从 FAKE_SUBSCRIPTIONS_DB 获取真实订阅等级
            # 这里简化处理，使用 auth.py 中的 subscription_tier
            check_search_access(user_id, "free")  # 或从 DB 获取
    ```
    """
    daily_limit = get_daily_limit(subscription_tier)

    # -1 表示无限制
    if daily_limit == -1:
        return

    current_usage = get_user_daily_usage(user_id)

    if current_usage >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "daily_limit_reached",
                "message": f"Daily search limit reached ({current_usage}/{daily_limit}). "
                           f"Please upgrade to Pro for unlimited searches.",
                "current_usage": current_usage,
                "daily_limit": daily_limit,
                "upgrade_url": "/upgrade",
            }
        )
