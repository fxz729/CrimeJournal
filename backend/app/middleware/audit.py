"""
Audit Log Middleware

集中记录关键用户操作和系统事件到 SQLite 数据库。

审计事件类型:
- auth_register: 用户注册
- auth_login: 用户登录
- auth_logout: 用户登出
- auth_profile_update: 资料更新
- auth_password_change: 密码修改
- auth_account_delete: 账户删除
- search: 案例搜索
- case_view: 查看案例
- case_favorite: 收藏/取消收藏
- case_summary: AI摘要生成
- case_similar: 相似案例查找
- subscription_change: 订阅变更
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Any
from enum import Enum
import json

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from app.config import settings

logger = logging.getLogger(__name__)

# ==================== Audit Event Types ====================


class AuditEvent(str, Enum):
    """审计事件类型枚举"""
    # Authentication
    AUTH_REGISTER = "auth_register"
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"
    AUTH_PROFILE_UPDATE = "auth_profile_update"
    AUTH_PASSWORD_CHANGE = "auth_password_change"
    AUTH_ACCOUNT_DELETE = "auth_account_delete"
    AUTH_TOKEN_REFRESH = "auth_token_refresh"

    # Case operations
    CASE_SEARCH = "case_search"
    CASE_VIEW = "case_view"
    CASE_FAVORITE_ADD = "case_favorite_add"
    CASE_FAVORITE_REMOVE = "case_favorite_remove"
    CASE_SUMMARY = "case_summary"
    CASE_SIMILAR = "case_similar"

    # Subscription
    SUBSCRIPTION_CHANGE = "subscription_change"
    SUBSCRIPTION_CANCEL = "subscription_cancel"

    # System
    SYSTEM_ERROR = "system_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


# ==================== Audit Log Database Model ====================

_audit_engine = None
_AuditSessionLocal = None

_audit_Base = declarative_base()


class AuditLog(_audit_Base):
    """审计日志数据库模型"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID for correlation
    user_id = Column(Integer, nullable=True, index=True)  # null for anonymous
    event_type = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)  # e.g. "case", "user", "subscription"
    resource_id = Column(String(200), nullable=True)  # e.g. case ID, user ID
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON: search_query, old_values, new_values, etc.
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


def _get_audit_engine():
    """Get or create the audit database engine."""
    global _audit_engine
    if _audit_engine is None:
        db_url = settings.database_url
        # Normalize sqlite+aiosqlite:/// to sqlite:/// for sync engine
        if "sqlite+aiosqlite:" in db_url:
            db_url = db_url.replace("sqlite+aiosqlite:", "sqlite:")

        connect_args = {}
        if "sqlite" in db_url:
            connect_args = {"check_same_thread": False}

        # Preserve the full path for SQLite (e.g. sqlite:///data/app.db -> sqlite:///data/app.db)
        # For other DBs, use as-is
        if db_url.startswith("sqlite:"):
            # sqlite:///absolute/path.db or sqlite:///relative/path.db
            _audit_engine = create_engine(
                db_url,
                connect_args=connect_args,
                echo=False,
            )
        else:
            _audit_engine = create_engine(
                db_url,
                connect_args=connect_args,
                echo=False,
            )
    return _audit_engine


def _get_audit_session():
    """Get or create the audit session factory."""
    global _AuditSessionLocal
    if _AuditSessionLocal is None:
        _AuditSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_get_audit_engine(),
        )
    return _AuditSessionLocal


def init_audit_db():
    """Initialize the audit log database table."""
    _audit_Base.metadata.create_all(bind=_get_audit_engine())


# Initialize on module load
try:
    init_audit_db()
except Exception as e:
    logger.warning(f"Audit log DB initialization skipped: {e}")


# ==================== Audit Logger ====================


class AuditLogger:
    """
    审计日志记录器

    用法：
    ```python
    audit = AuditLogger(user_id=123, event_type=AuditEvent.AUTH_LOGIN)
    audit.set_metadata(search_query="contract breach")
    audit.set_resource("case", "456")
    audit.info(request=req, status_code=200)
    ```

    或者使用便捷方法：
    ```python
    log_audit(
        user_id=123,
        event_type=AuditEvent.CASE_SEARCH,
        request=request,
        metadata={"query": "contract breach", "results_count": 42},
    )
    ```
    """

    def __init__(
        self,
        user_id: Optional[int] = None,
        event_type: AuditEvent = AuditEvent.SYSTEM_ERROR,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        self.event_id = str(uuid.uuid4())
        self.user_id = user_id
        self.event_type = event_type.value if isinstance(event_type, AuditEvent) else event_type
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.ip_address: Optional[str] = None
        self.user_agent: Optional[str] = None
        self.request_path: Optional[str] = None
        self.request_method: Optional[str] = None
        self.status_code: Optional[int] = None
        self.metadata: Optional[dict] = None
        self.error_message: Optional[str] = None
        self._request: Optional[Request] = None

    def set_resource(self, resource_type: str, resource_id: str) -> 'AuditLogger':
        """设置资源信息"""
        self.resource_type = resource_type
        self.resource_id = resource_id
        return self

    def set_metadata(self, **kwargs) -> 'AuditLogger':
        """设置元数据（搜索词、旧值、新值等）"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata.update(kwargs)
        return self

    def set_request(self, request: Request) -> 'AuditLogger':
        """从 Request 对象提取信息"""
        self._request = request
        self.request_path = str(request.url.path)
        self.request_method = request.method
        self.ip_address = request.client.host if request.client else None
        self.user_agent = request.headers.get("user-agent", "")[:500]
        return self

    def info(self, request: Optional[Request] = None, status_code: int = 200) -> None:
        """记录 INFO 级别审计日志"""
        self._log(request, status_code, level="info")

    def error(self, request: Optional[Request] = None, status_code: int = 500, error: Optional[str] = None) -> None:
        """记录 ERROR 级别审计日志"""
        self.status_code = status_code
        self.error_message = error
        self._log(request, status_code, level="error")

    def warning(self, request: Optional[Request] = None, status_code: int = 429) -> None:
        """记录 WARNING 级别审计日志"""
        self._log(request, status_code, level="warning")

    def _log(self, request: Optional[Request], status_code: int, level: str) -> None:
        """内部日志记录方法"""
        if request and not self._request:
            self.set_request(request)
        if status_code:
            self.status_code = status_code

        try:
            SessionLocal = _get_audit_session()
            db = SessionLocal()
            try:
                log_entry = AuditLog(
                    event_id=self.event_id,
                    user_id=self.user_id,
                    event_type=self.event_type,
                    resource_type=self.resource_type,
                    resource_id=self.resource_id,
                    ip_address=self.ip_address,
                    user_agent=self.user_agent,
                    request_path=self.request_path,
                    request_method=self.request_method,
                    status_code=self.status_code,
                    extra_data=json.dumps(self.metadata) if self.metadata else None,
                    error_message=self.error_message,
                )
                db.add(log_entry)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to write audit log: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Audit logger error: {e}")

        # Also log to standard logger
        log_data = {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "resource": f"{self.resource_type}/{self.resource_id}" if self.resource_type else None,
            "path": self.request_path,
            "status": self.status_code,
        }
        getattr(logger, level)(f"AUDIT: {json.dumps(log_data)}")


def log_audit(
    user_id: Optional[int],
    event_type: AuditEvent,
    request: Optional[Request] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    status_code: int = 200,
    **metadata,
) -> None:
    """
    便捷函数：记录审计日志

    用法：
    ```python
    log_audit(
        user_id=current_user["id"],
        event_type=AuditEvent.AUTH_LOGIN,
        request=request,
        status_code=200,
    )
    ```
    """
    AuditLogger(
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
    ).set_metadata(**metadata).info(request=request, status_code=status_code)


# ==================== Audit Middleware ====================


class AuditMiddleware(BaseHTTPMiddleware):
    """
    审计日志中间件

    自动记录所有 API 请求的审计日志。
    可选地支持详细的请求/响应日志记录。

    特点：
    - 只记录 /api/* 路径的请求
    - 排除健康检查和根路径
    - 不记录静态资源
    - 请求完成时记录日志（包含状态码）
    """

    # 不记录的路径模式
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    }

    # 标记为需要用户上下文的路径（需要从 token 解析 user_id）
    USER_CONTEXT_PATHS = ["/api/auth/", "/api/cases/"]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 只记录 API 请求
        path = request.url.path
        if not path.startswith("/api/") or path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # 获取用户 ID（如果可能）
        user_id: Optional[int] = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                # Local import to avoid circular dependency
                from app.api.auth import decode_token
                token = auth_header.replace("Bearer ", "")
                payload = decode_token(token)
                user_id = int(payload.get("sub"))
            except Exception:
                pass

        # 记录开始时间
        start_time = datetime.utcnow()

        # 处理请求
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            log_audit(
                user_id=user_id,
                event_type=AuditEvent.SYSTEM_ERROR,
                request=request,
                status_code=status_code,
                error=str(e)[:500],
            )
            raise

        # 记录审计日志（使用线程，避免阻塞）
        try:
            log_audit(
                user_id=user_id,
                event_type=self._infer_event_type(path, request.method),
                request=request,
                status_code=status_code,
                duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
            )
        except Exception as e:
            logger.debug(f"Audit middleware log error: {e}")

        return response

    def _infer_event_type(self, path: str, method: str) -> AuditEvent:
        """根据路径和方法推断事件类型"""
        path_lower = path.lower()

        # Auth endpoints
        if "/auth/register" in path:
            return AuditEvent.AUTH_REGISTER
        if "/auth/login" in path:
            return AuditEvent.AUTH_LOGIN
        if "/auth/logout" in path:
            return AuditEvent.AUTH_LOGOUT
        if "/auth/profile" in path:
            return AuditEvent.AUTH_PROFILE_UPDATE
        if "/auth/password" in path:
            return AuditEvent.AUTH_PASSWORD_CHANGE
        if "/auth/account" in path and method == "DELETE":
            return AuditEvent.AUTH_ACCOUNT_DELETE

        # Case endpoints
        if "/cases/search" in path:
            return AuditEvent.CASE_SEARCH
        if "/cases/" in path and method == "GET":
            return AuditEvent.CASE_VIEW
        if "/cases/" in path and method == "POST" and "/favorite" in path:
            return AuditEvent.CASE_FAVORITE_ADD
        if "/cases/" in path and method == "DELETE" and "/favorite" in path:
            return AuditEvent.CASE_FAVORITE_REMOVE
        if "/cases/" in path and "/summary" in path:
            return AuditEvent.CASE_SUMMARY
        if "/cases/" in path and "/similar" in path:
            return AuditEvent.CASE_SIMILAR

        # Subscription
        if "/subscriptions/" in path:
            return AuditEvent.SUBSCRIPTION_CHANGE

        # Rate limit
        if "rate_limit" in path_lower:
            return AuditEvent.RATE_LIMIT_EXCEEDED

        return AuditEvent.SYSTEM_ERROR
