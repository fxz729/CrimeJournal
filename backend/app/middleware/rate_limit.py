"""
API Rate Limiting Middleware

基于 IP 的请求限流中间件
- 每分钟最多 60 个请求（每 IP）
- 使用内存字典记录请求计数
- 超限返回 429 Too Many Requests
"""

import logging
import time
from collections import defaultdict
from typing import Callable, Dict, List, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# ==================== In-Memory Rate Limiting Storage ====================

# 请求记录: ip -> [(timestamp, count), ...]
# 每个元素是 (请求时间戳, 请求计数) 的列表
_rate_limit_db: Dict[str, List[Tuple[float, int]]] = defaultdict(list)

# 注意：Python GIL 使得简单字典操作在 CPython 中是原子的，无需额外加锁。

# 限流配置
RATE_LIMIT_WINDOW = 60       # 时间窗口：60秒（1分钟）
RATE_LIMIT_MAX_REQUESTS = 60  # 每窗口最大请求数


def _cleanup_old_entries(ip: str, current_time: float) -> None:
    """清理过期的请求记录"""
    cutoff = current_time - RATE_LIMIT_WINDOW
    _rate_limit_db[ip] = [
        (ts, count) for ts, count in _rate_limit_db[ip]
        if ts > cutoff
    ]


def check_rate_limit(ip: str) -> Tuple[bool, int, int]:
    """
    检查 IP 的请求频率

    Args:
        ip: 客户端 IP 地址

    Returns:
        (是否允许, 当前请求数, 限制数)
    """
    current_time = time.time()

    # 清理过期记录
    _cleanup_old_entries(ip, current_time)

    # 获取当前窗口内的请求数
    current_count = sum(count for _, count in _rate_limit_db[ip])
    total_requests = current_count + 1  # 即将发送的请求

    if total_requests > RATE_LIMIT_MAX_REQUESTS:
        return False, current_count, RATE_LIMIT_MAX_REQUESTS

    # 记录新请求
    _rate_limit_db[ip].append((current_time, 1))
    return True, total_requests, RATE_LIMIT_MAX_REQUESTS


def get_rate_limit_remaining(ip: str) -> int:
    """获取 IP 的剩余请求配额"""
    current_time = time.time()
    _cleanup_old_entries(ip, current_time)
    current_count = sum(count for _, count in _rate_limit_db[ip])
    return max(0, RATE_LIMIT_MAX_REQUESTS - current_count)


# ==================== ASGI Middleware ====================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    API 限流中间件

    限制所有 /api/* 请求的频率
    - 每 IP 每分钟最多 60 个请求
    - 超限返回 429 状态码
    """

    # 限流的路径模式（空列表表示限流所有 /api/*）
    PROTECTED_PREFIX = "/api"

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 只限流 /api/* 路径
        path = request.url.path
        if not path.startswith(self.PROTECTED_PREFIX):
            return await call_next(request)

        # 获取客户端 IP
        client_ip = self._get_client_ip(request)

        # 检查限流
        allowed, current, limit = check_rate_limit(client_ip)

        if not allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {current}/{limit}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Maximum {limit} requests per minute allowed.",
                    "current_requests": current,
                    "limit": limit,
                    "retry_after": RATE_LIMIT_WINDOW,
                },
                headers={
                    "Retry-After": str(RATE_LIMIT_WINDOW),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + RATE_LIMIT_WINDOW),
                },
            )

        # 添加限流响应头
        response = await call_next(request)
        remaining = get_rate_limit_remaining(client_ip)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + RATE_LIMIT_WINDOW)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实 IP

        优先从 X-Forwarded-For 头获取（反向代理场景），
        否则使用连接的客户端 IP
        """
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # X-Forwarded-For 可能包含多个 IP，取第一个
            return forwarded.split(",")[0].strip()

        # 检查 X-Real-IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # 使用连接的对端地址
        if request.client:
            return request.client.host

        return "unknown"
