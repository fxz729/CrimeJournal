"""
Authentication API Routes

用户注册、登录、认证相关API
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
import jwt

from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer认证
security = HTTPBearer()


# ==================== Pydantic Models ====================

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    full_name: Optional[str] = Field(None, max_length=200, description="姓名")


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


# ==================== Database Model Simulation ====================
# TODO: 后续集成真实数据库
# 这里使用模拟数据，实际项目中需要替换为数据库操作

FAKE_USERS_DB = {}


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
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


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

    # TODO: 从数据库获取用户信息
    # 模拟从数据库获取用户
    user = FAKE_USERS_DB.get(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return {"id": user_id, "email": email}


def get_optional_user(
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
async def register(request: UserRegisterRequest):
    """
    用户注册

    - **email**: 邮箱地址（唯一）
    - **password**: 密码（至少6位）
    - **full_name**: 姓名（可选）
    """
    # 检查邮箱是否已存在
    # TODO: 替换为数据库查询
    for user in FAKE_USERS_DB.values():
        if user["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册",
            )

    # 创建新用户
    user_id = len(FAKE_USERS_DB) + 1
    hashed_password = get_password_hash(request.password)

    new_user = {
        "id": user_id,
        "email": request.email,
        "hashed_password": hashed_password,
        "full_name": request.full_name,
        "subscription_tier": "free",
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow(),
    }

    # TODO: 保存到数据库
    FAKE_USERS_DB[user_id] = new_user

    # 生成Token
    access_token = create_access_token(user_id, request.email)

    logger.info(f"新用户注册: {request.email}")

    return AuthResponse(
        user=UserResponse(
            id=new_user["id"],
            email=new_user["email"],
            full_name=new_user["full_name"],
            subscription_tier=new_user["subscription_tier"],
            is_active=new_user["is_active"],
            created_at=new_user["created_at"],
        ),
        token=TokenResponse(
            access_token=access_token,
            expires_in=settings.jwt_expiration_hours * 3600,
        ),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="用户登录",
    description="用户登录，返回访问令牌",
)
async def login(request: UserLoginRequest):
    """
    用户登录

    - **email**: 邮箱地址
    - **password**: 密码
    """
    # TODO: 替换为数据库查询
    user = None
    for u in FAKE_USERS_DB.values():
        if u["email"] == request.email:
            user = u
            break

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )

    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 生成Token
    access_token = create_access_token(user["id"], user["email"])

    logger.info(f"用户登录: {request.email}")

    return AuthResponse(
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            subscription_tier=user.get("subscription_tier", "free"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"],
        ),
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

    # TODO: 替换为数据库查询
    user = FAKE_USERS_DB.get(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user.get("full_name"),
        subscription_tier=user.get("subscription_tier", "free"),
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="用户登出",
    description="当前会话登出（客户端应删除Token）",
)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    用户登出

    注意：这只是通知服务器，客户端需要自行删除Token
    JWT是无状态的，服务器不保存Token黑名单
    如需实现真正的登出，需要使用Token黑名单机制
    """
    logger.info(f"用户登出: {current_user['email']}")
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
