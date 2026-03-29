"""
Subscription API Routes

订阅管理和用量统计相关 API
数据统一存储在 SQLite users 表中（subscription_tier、daily_search_count、last_search_date）
集成 Stripe 时需要替换相关逻辑
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field

from app.api.auth import get_current_user, get_session_local, DBUser
from app.config import settings
from app.middleware.audit import AuditEvent, log_audit

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== Subscription Plans Definition ====================

SUBSCRIPTION_PLANS = {
    "free": {
        "id": "free",
        "name": "Free",
        "price": 0,
        "price_monthly": 0,
        "searches_per_day": 10,
        "ai_summaries": False,
        "entity_extraction": False,
        "similar_cases": False,
        "api_access": False,
        "team_accounts": False,
        "description": "For individuals just getting started",
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "price": 290,
        "price_monthly": 290,
        "display_price": 2.9,
        "searches_per_day": -1,  # unlimited
        "ai_summaries": True,
        "entity_extraction": True,
        "similar_cases": True,
        "api_access": False,
        "team_accounts": False,
        "description": "For legal professionals and researchers",
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise",
        "price": 590,
        "price_monthly": 590,
        "display_price": 5.9,
        "searches_per_day": -1,  # unlimited
        "ai_summaries": True,
        "entity_extraction": True,
        "similar_cases": True,
        "api_access": True,
        "team_accounts": True,
        "description": "For law firms and organizations",
    },
}


# ==================== Helper Functions ====================

def _get_next_billing_date() -> date:
    """获取下一个账单日期（模拟：每月1日）"""
    today = date.today()
    if today.day == 1:
        return today + timedelta(days=30)
    return today.replace(day=1) + timedelta(days=32)


def _get_user_subscription_info(user_id: int) -> Dict:
    """从 SQLite 读取用户订阅信息。"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            return {
                "plan": "free",
                "status": "active",
                "current_period_start": datetime.utcnow().replace(day=1).isoformat(),
                "current_period_end": _get_next_billing_date().isoformat(),
                "cancel_at_period_end": False,
            }
        return {
            "plan": user.subscription_tier or "free",
            "status": "active",
            "current_period_start": datetime.utcnow().replace(day=1).isoformat(),
            "current_period_end": _get_next_billing_date().isoformat(),
            "cancel_at_period_end": False,
        }
    finally:
        db.close()


def _get_user_usage(user_id: int) -> tuple[int, datetime]:
    """从 SQLite 读取用户今日搜索次数和上次搜索时间。"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            return 0, datetime.utcnow()
        return user.daily_search_count or 0, user.last_search_date or datetime.utcnow()
    finally:
        db.close()


def _reset_daily_search_if_needed(user_id: int) -> int:
    """如果上次搜索日期不是今天，重置计数器。返回今日搜索次数。"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            return 0
        today = date.today()
        if user.last_search_date is None:
            user.daily_search_count = 1
            user.last_search_date = datetime.utcnow()
            db.commit()
            return 1
        last_date = user.last_search_date.date()
        if last_date != today:
            user.daily_search_count = 1
            user.last_search_date = datetime.utcnow()
            db.commit()
            return 1
        return user.daily_search_count or 0
    finally:
        db.close()


def _increment_daily_search(user_id: int) -> int:
    """增加用户今日搜索次数。返回新的计数。"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            return 0
        today = datetime.utcnow().date()
        last_date = user.last_search_date.date() if user.last_search_date else None
        if last_date != today:
            user.daily_search_count = 1
        else:
            user.daily_search_count = (user.daily_search_count or 0) + 1
        user.last_search_date = datetime.utcnow()
        db.commit()
        return user.daily_search_count
    finally:
        db.close()


# ==================== Pydantic Models ====================

class PlanResponse(BaseModel):
    """订阅计划响应"""
    id: str
    name: str
    price: int
    price_monthly: int
    display_price: Optional[float] = None
    searches_per_day: int
    ai_summaries: bool
    entity_extraction: bool
    similar_cases: bool
    api_access: bool
    team_accounts: bool
    description: str


class SubscriptionResponse(BaseModel):
    """订阅状态响应"""
    plan: str
    plan_name: str
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool
    features: Dict[str, bool]


class UpgradeRequest(BaseModel):
    """升级订阅请求"""
    plan: str = Field(..., description="目标计划 (pro/enterprise)")


class UpgradeResponse(BaseModel):
    """升级响应"""
    success: bool
    message: str
    checkout_url: Optional[str] = None


class CancelResponse(BaseModel):
    """取消订阅响应"""
    success: bool
    message: str
    current_period_end: str


class UsageStatsResponse(BaseModel):
    """用量统计响应"""
    today_searches: int
    daily_limit: int
    is_unlimited: bool
    monthly_usage: Dict[str, int]
    monthly_total: int


class FeatureAccessResponse(BaseModel):
    """功能访问权限响应"""
    ai_summaries: bool
    entity_extraction: bool
    similar_cases: bool
    api_access: bool
    team_accounts: bool
    can_search: bool


# ==================== API Routes ====================

@router.get(
    "/plans",
    response_model=dict[str, PlanResponse],
    summary="获取订阅计划",
    description="获取所有可用的订阅计划",
)
async def get_plans():
    """获取所有订阅计划列表"""
    return {
        plan_id: PlanResponse(**plan_info)
        for plan_id, plan_info in SUBSCRIPTION_PLANS.items()
    }


@router.get(
    "/me",
    response_model=SubscriptionResponse,
    summary="获取我的订阅",
    description="获取当前用户的订阅状态",
)
async def get_my_subscription(current_user: dict = Depends(get_current_user)):
    """获取当前用户的订阅信息"""
    user_id = current_user["id"]
    subscription = _get_user_subscription_info(user_id)
    plan_info = SUBSCRIPTION_PLANS.get(subscription["plan"], SUBSCRIPTION_PLANS["free"])

    return SubscriptionResponse(
        plan=subscription["plan"],
        plan_name=plan_info["name"],
        status=subscription["status"],
        current_period_start=subscription["current_period_start"],
        current_period_end=subscription["current_period_end"],
        cancel_at_period_end=subscription["cancel_at_period_end"],
        features={
            "ai_summaries": plan_info["ai_summaries"],
            "entity_extraction": plan_info["entity_extraction"],
            "similar_cases": plan_info["similar_cases"],
            "api_access": plan_info["api_access"],
            "team_accounts": plan_info["team_accounts"],
        },
    )


@router.post(
    "/upgrade",
    response_model=UpgradeResponse,
    summary="升级订阅",
    description="升级到付费计划（模拟 Stripe checkout）",
)
async def upgrade_subscription(
    request: UpgradeRequest,
    req: Request,
    current_user: dict = Depends(get_current_user),
):
    """升级订阅"""
    user_id = current_user["id"]
    target_plan = request.plan

    if target_plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {target_plan}",
        )

    if target_plan == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upgrade to free plan",
        )

    plan_info = SUBSCRIPTION_PLANS[target_plan]

    logger.info(f"User {current_user['email']} upgrading to {target_plan} (${plan_info['price']}/month)")

    # ==================== STRIPE INTEGRATION PLACEHOLDER ====================
    # 集成 Stripe 时：创建 Stripe Checkout Session，返回 checkout_url
    # ==================== END STRIPE INTEGRATION PLACEHOLDER ====================

    # 模拟：直接升级，更新 SQLite users 表
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.subscription_tier = target_plan
        db.commit()
    finally:
        db.close()

    # 审计日志
    log_audit(
        user_id=user_id,
        event_type=AuditEvent.SUBSCRIPTION_CHANGE,
        request=req,
        status_code=200,
        resource_type="subscription",
        resource_id=str(user_id),
        metadata={
            "old_plan": "free",
            "new_plan": target_plan,
            "price_monthly": plan_info["price"],
        },
    )

    return UpgradeResponse(
        success=True,
        message=f"Successfully upgraded to {plan_info['name']}!",
        checkout_url=None,
    )


@router.post(
    "/cancel",
    response_model=CancelResponse,
    summary="取消订阅",
    description="取消当前订阅（降级到免费计划）",
)
async def cancel_subscription(req: Request, current_user: dict = Depends(get_current_user)):
    """取消订阅"""
    user_id = current_user["id"]
    subscription = _get_user_subscription_info(user_id)

    if subscription["plan"] == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already on the free plan",
        )

    # ==================== STRIPE INTEGRATION PLACEHOLDER ====================
    # 集成 Stripe 时：stripe_service.cancel_subscription(subscription["stripe_subscription_id"])
    # ==================== END STRIPE INTEGRATION PLACEHOLDER ====================

    # 模拟：降级到免费计划
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        user.subscription_tier = "free"
        db.commit()
    finally:
        db.close()

    logger.info(f"User {current_user['email']} cancelled subscription (plan: {subscription['plan']})")

    log_audit(
        user_id=user_id,
        event_type=AuditEvent.SUBSCRIPTION_CANCEL,
        request=req,
        status_code=200,
        resource_type="subscription",
        resource_id=str(user_id),
        metadata={
            "plan": subscription["plan"],
            "current_period_end": subscription["current_period_end"],
        },
    )

    return CancelResponse(
        success=True,
        message="Subscription will be cancelled at the end of the current billing period",
        current_period_end=subscription["current_period_end"],
    )


@router.get(
    "/usage",
    response_model=UsageStatsResponse,
    summary="获取用量统计",
    description="获取当月用量统计",
)
async def get_usage(current_user: dict = Depends(get_current_user)):
    """获取用户用量统计"""
    user_id = current_user["id"]
    subscription = _get_user_subscription_info(user_id)
    plan_info = SUBSCRIPTION_PLANS.get(subscription["plan"], SUBSCRIPTION_PLANS["free"])

    # 确保计数是最新的（如果昨天搜索过，今天重置）
    today_count = _reset_daily_search_if_needed(user_id)
    searches_per_day = plan_info.get("searches_per_day", 10)

    # 月度用量：只包含今天的记录（SQLite users 表只存储每日计数）
    monthly_usage = {date.today().isoformat(): today_count}
    monthly_total = today_count

    return UsageStatsResponse(
        today_searches=today_count,
        daily_limit=searches_per_day,
        is_unlimited=searches_per_day == -1,
        monthly_usage=monthly_usage,
        monthly_total=monthly_total,
    )


@router.get(
    "/features",
    response_model=FeatureAccessResponse,
    summary="获取功能权限",
    description="获取当前用户的功能访问权限",
)
async def get_feature_access(current_user: dict = Depends(get_current_user)):
    """获取用户功能访问权限"""
    user_id = current_user["id"]
    subscription = _get_user_subscription_info(user_id)
    plan_info = SUBSCRIPTION_PLANS.get(subscription["plan"], SUBSCRIPTION_PLANS["free"])

    return FeatureAccessResponse(
        ai_summaries=plan_info["ai_summaries"],
        entity_extraction=plan_info["entity_extraction"],
        similar_cases=plan_info["similar_cases"],
        api_access=plan_info["api_access"],
        team_accounts=plan_info["team_accounts"],
        can_search=True,
    )


# ==================== Webhook Endpoint (for Stripe integration) ====================

@router.post(
    "/webhook",
    summary="Stripe Webhook",
    description="处理 Stripe webhook 事件（集成 Stripe 时启用）",
)
async def stripe_webhook(payload: dict, current_user: dict = Depends(get_current_user)):
    """
    处理 Stripe webhook 事件

    集成 Stripe 时需要：
    1. 验证 webhook 签名
    2. 处理 checkout.session.completed 事件 → 升级订阅
    3. 处理 customer.subscription.updated 事件 → 更新订阅状态
    4. 处理 customer.subscription.deleted 事件 → 降级到免费计划
    """
    # ==================== STRIPE INTEGRATION PLACEHOLDER ====================
    # TODO: 集成 Stripe 时实现完整 webhook 处理
    # ==================== END STRIPE INTEGRATION PLACEHOLDER ====================
    return {"received": True, "note": "Webhook endpoint - integrate Stripe to activate"}
