"""
Authentication API Routes

用户注册、登录、认证相关API
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, field_validator
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings
from app.middleware.audit import AuditEvent, log_audit

logger = logging.getLogger(__name__)
router = APIRouter()

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer认证
security = HTTPBearer()

# ==================== SQLAlchemy Database Setup ====================

_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the database engine (singleton)."""
    global _engine
    if _engine is None:
        from sqlalchemy import create_engine

        db_url = settings.database_url
        # Normalize sqlite+aiosqlite:/// to sqlite:/// for sync engine
        # aiosqlite is used by tests but we use sync operations in FastAPI endpoints
        if "sqlite+aiosqlite:" in db_url:
            db_url = db_url.replace("sqlite+aiosqlite:", "sqlite:")

        connect_args = {}
        if "sqlite" in db_url:
            connect_args = {"check_same_thread": False}

        _engine = create_engine(
            db_url,
            connect_args=connect_args,
            echo=False,
        )
    return _engine


def get_session_local():
    """Get or create the session factory (singleton)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


# SQLAlchemy declarative base and model
_db_Base = declarative_base()


class DBUser(_db_Base):
    """SQLAlchemy User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    subscription_tier = Column(String(50), default="free")
    stripe_customer_id = Column(String(200))
    subscription_end_date = Column(DateTime)
    daily_search_count = Column(Integer, default=0)
    last_search_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


def init_db():
    """Initialize the database tables."""
    _db_Base.metadata.create_all(bind=get_engine())


# Initialize the database on module load
init_db()


# ==================== Pydantic Models ====================

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    full_name: Optional[str] = Field(None, max_length=200, description="姓名")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含至少一个小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含至少一个数字")
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    email: str
    full_name: Optional[str]
    subscription_tier: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """认证响应（包含用户信息和Token）"""
    user: UserResponse
    token: TokenResponse


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True


class UpdateProfileRequest(BaseModel):
    """更新资料请求"""
    full_name: Optional[str] = Field(None, max_length=200)


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含至少一个小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含至少一个数字")
        return v


# ==================== Database Model ====================
# Users are stored exclusively in SQLite. DO NOT use FAKE_USERS_DB.


# ==================== Helper Functions ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_access_token(user_id: int, email: str) -> str:
    """创建JWT访问令牌"""
    expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str) -> dict:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _user_to_response(user) -> UserResponse:
    """Convert a DBUser or dict user to UserResponse."""
    if isinstance(user, dict):
        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            subscription_tier=user.get("subscription_tier", "free"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"],
        )
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        subscription_tier=user.subscription_tier,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _db_user_to_dict(db_user) -> dict:
    """Convert a DBUser to a dict matching the FAKE_USERS_DB format."""
    return {
        "id": db_user.id,
        "email": db_user.email,
        "hashed_password": db_user.hashed_password,
        "full_name": db_user.full_name,
        "subscription_tier": db_user.subscription_tier,
        "is_active": db_user.is_active,
        "is_verified": db_user.is_verified,
        "created_at": db_user.created_at,
    }


# ==================== Auth Dependencies ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    获取当前认证用户

    JWT认证依赖，用于保护需要认证的路由
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id = int(payload.get("sub"))
    email = payload.get("email")

    # 只从 SQLite 读取用户数据
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = _db_user_to_dict(db_user)
    finally:
        db.close()

    if user.get("is_active") is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return {"id": user_id, "email": email}


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """
    获取当前用户（可选）

    用于某些可选认证的场景
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# ==================== API Routes ====================

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新用户，返回访问令牌",
)
async def register(req: Request, body: UserRegisterRequest):
    """
    用户注册

    - **email**: 邮箱地址（唯一）
    - **password**: 密码（至少6位）
    - **full_name**: 姓名（可选）
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        # 检查邮箱是否已在数据库中
        existing = db.query(DBUser).filter(DBUser.email == body.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已注册",
            )

        # 创建新用户
        hashed_password = get_password_hash(body.password)
        new_user = DBUser(
            email=body.email,
            hashed_password=hashed_password,
            full_name=body.full_name,
            subscription_tier="free",
            is_active=True,
            is_verified=False,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 生成Token
        access_token = create_access_token(new_user.id, new_user.email)

        logger.info(f"新用户注册: {body.email}")

        # 审计日志
        log_audit(
            user_id=new_user.id,
            event_type=AuditEvent.AUTH_REGISTER,
            request=req,
            status_code=201,
            metadata={
                "email": body.email,
                "subscription_tier": "free",
                "has_full_name": bool(body.full_name),
            },
        )

        return AuthResponse(
            user=_user_to_response(new_user),
            token=TokenResponse(
                access_token=access_token,
                expires_in=settings.jwt_expiration_hours * 3600,
            ),
        )
    finally:
        db.close()


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="用户登录",
    description="用户登录，返回访问令牌",
)
async def login(req: Request, body: UserLoginRequest):
    """
    用户登录

    - **email**: 邮箱地址
    - **password**: 密码
    """
    # 只从 SQLite 读取用户数据
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        db_user = db.query(DBUser).filter(DBUser.email == body.email).first()
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误",
            )
        user = _db_user_to_dict(db_user)
    finally:
        db.close()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )

    if not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )

    if user.get("is_active") is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 生成Token
    access_token = create_access_token(user["id"], user["email"])

    logger.info(f"用户登录: {body.email}")

    # 审计日志
    log_audit(
        user_id=user["id"],
        event_type=AuditEvent.AUTH_LOGIN,
        request=req,
        status_code=200,
        metadata={
            "email": body.email,
            "subscription_tier": user.get("subscription_tier", "free"),
        },
    )

    return AuthResponse(
        user=_user_to_response(user),
        token=TokenResponse(
            access_token=access_token,
            expires_in=settings.jwt_expiration_hours * 3600,
        ),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户",
    description="获取当前登录用户的信息",
)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息

    需要有效的JWT Token
    """
    user_id = current_user["id"]

    # 只从 SQLite 读取
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )
        user = _db_user_to_dict(db_user)
    finally:
        db.close()

    return _user_to_response(user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="用户登出",
    description="当前会话登出（客户端应删除Token）",
)
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    """
    用户登出

    注意：这只是通知服务器，客户端需要自行删除Token
    JWT是无状态的，服务器不保存Token黑名单
    如需实现真正的登出，需要使用Token黑名单机制
    """
    logger.info(f"用户登出: {current_user['email']}")
    log_audit(
        user_id=current_user["id"],
        event_type=AuditEvent.AUTH_LOGOUT,
        request=request,
        status_code=200,
    )
    return MessageResponse(message="登出成功")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新Token",
    description="刷新访问令牌",
)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    刷新访问令牌

    获取新的JWT Token
    """
    user_id = current_user["id"]
    email = current_user["email"]

    access_token = create_access_token(user_id, email)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.jwt_expiration_hours * 3600,
    )


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="更新个人资料",
    description="更新当前用户的姓名",
)
async def update_profile(
    request: Request,
    update_req: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    更新个人资料

    - **full_name**: 姓名（可选）
    """
    user_id = current_user["id"]

    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        old_full_name = user.full_name  # 在更新前保存旧值
        user.full_name = update_req.full_name
        db.commit()
        db.refresh(user)

        logger.info(f"用户更新资料: {current_user['email']}")
        log_audit(
            user_id=current_user["id"],
            event_type=AuditEvent.AUTH_PROFILE_UPDATE,
            request=request,
            status_code=200,
            metadata={
                "old_full_name": old_full_name,
                "new_full_name": update_req.full_name,
            },
        )
        return _user_to_response(user)
    finally:
        db.close()


@router.put(
    "/password",
    response_model=MessageResponse,
    summary="修改密码",
    description="修改当前用户的密码",
)
async def change_password(
    request: Request,
    pwd_req: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    修改密码

    - **old_password**: 当前密码
    - **new_password**: 新密码（至少6位）
    """
    user_id = current_user["id"]

    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        # 验证旧密码
        if not verify_password(pwd_req.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误",
            )

        # 更新新密码
        user.hashed_password = get_password_hash(pwd_req.new_password)
        db.commit()

        logger.info(f"用户修改密码: {current_user['email']}")
        log_audit(
            user_id=current_user["id"],
            event_type=AuditEvent.AUTH_PASSWORD_CHANGE,
            request=request,
            status_code=200,
        )
        return MessageResponse(message="密码修改成功")
    finally:
        db.close()


@router.delete(
    "/account",
    response_model=MessageResponse,
    summary="删除账户",
    description="永久删除当前用户账户",
)
async def delete_account(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    删除账户

    永久删除当前登录用户的账户
    """
    user_id = current_user["id"]

    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        email = user.email
        db.delete(user)
        db.commit()

        logger.info(f"用户删除账户: {email}")
        log_audit(
            user_id=user_id,
            event_type=AuditEvent.AUTH_ACCOUNT_DELETE,
            request=request,
            status_code=200,
            metadata={"deleted_email": email},
        )
        return MessageResponse(message="账户已删除")
    finally:
        db.close()
