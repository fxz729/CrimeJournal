"""
Subscription API Routes

订阅管理和用量统计相关 API
注意：当前为模拟实现，数据存储在内存中
集成 Stripe 时需要替换相关逻辑
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from jose import jwt

from app.api.auth import get_current_user
from app.config import settings

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
        "price": 50,
        "price_monthly": 50,
        "searches_per_day": -1,  # unlimited
        "ai_summaries": True,
        "entity_extraction": True,
        "similar_cases": True,
        "api_access": False,
        "team_accounts": False,
        "description": "For legal professionals and researchers",
    },
    # Enterprise plan is optional/simplified
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise",
        "price": 500,
        "price_monthly": 500,
        "searches_per_day": -1,  # unlimited
        "ai_summaries": True,
        "entity_extraction": True,
        "similar_cases": True,
        "api_access": True,
        "team_accounts": True,
        "description": "For law firms and organizations",
    },
}


# ==================== In-Memory Database Simulation ====================
# TODO: 后续集成真实数据库

# 用户订阅状态存储: user_id -> subscription_info
FAKE_SUBSCRIPTIONS_DB: Dict[int, Dict[str, Any]] = {}

# 用户用量统计: user_id -> { "YYYY-MM-DD": count }
FAKE_USAGE_DB: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

# Stripe checkout session storage (模拟)
# 在集成 Stripe 时，这里存储真实 checkout session ID
FAKE_CHECKOUT_SESSIONS: Dict[str, Dict[str, Any]] = {}


# ==================== Helper Functions ====================

def get_user_subscription(user_id: int) -> Dict[str, Any]:
    """获取用户订阅状态"""
    if user_id not in FAKE_SUBSCRIPTIONS_DB:
        # 默认免费计划
        return {
            "plan": "free",
            "status": "active",
            "current_period_start": datetime.utcnow().replace(day=1).isoformat(),
            "current_period_end": _get_next_billing_date().isoformat(),
            "cancel_at_period_end": False,
            "stripe_customer_id": None,
            "stripe_subscription_id": None,
        }
    return FAKE_SUBSCRIPTIONS_DB[user_id]


def get_today_date_str() -> str:
    """获取今天的日期字符串"""
    return date.today().isoformat()


def _get_next_billing_date() -> date:
    """获取下一个账单日期（模拟：每月1日）"""
    today = date.today()
    if today.day == 1:
        return today + timedelta(days=30)  # 特殊情况：今天就是1号，下个月
    return today.replace(day=1) + timedelta(days=32)


def get_user_usage_today(user_id: int) -> int:
    """获取用户今日搜索次数"""
    today_str = get_today_date_str()
    return FAKE_USAGE_DB[user_id].get(today_str, 0)


def check_search_limit(user_id: int, subscription_plan: str) -> tuple[bool, str]:
    """
    检查用户是否超过搜索限制
    返回: (是否允许, 错误消息)
    """
    plan_info = SUBSCRIPTION_PLANS.get(subscription_plan, SUBSCRIPTION_PLANS["free"])
    searches_per_day = plan_info.get("searches_per_day", 10)

    # -1 表示无限制
    if searches_per_day == -1:
        return True, ""

    today_count = get_user_usage_today(user_id)
    if today_count >= searches_per_day:
        return False, f"Daily search limit reached ({today_count}/{searches_per_day})"

    return True, ""


def record_search(user_id: int) -> None:
    """记录一次搜索"""
    today_str = get_today_date_str()
    FAKE_USAGE_DB[user_id][today_str] += 1


def get_monthly_usage(user_id: int) -> Dict[str, int]:
    """获取用户本月用量统计"""
    today = date.today()
    year = today.year
    month = today.month

    usage = {}
    for day_str, count in FAKE_USAGE_DB[user_id].items():
        try:
            d = datetime.fromisoformat(day_str).date()
            if d.year == year and d.month == month:
                usage[day_str] = count
        except (ValueError, TypeError):
            continue

    return usage


# ==================== Pydantic Models ====================

class PlanResponse(BaseModel):
    """订阅计划响应"""
    id: str
    name: str
    price: int
    price_monthly: int
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
    # 集成 Stripe 时: checkout_url 指向 Stripe Checkout Session
    # mock: checkout_url = "/upgrade/success?session_id=xxx"


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
    """
    获取所有订阅计划列表

    返回每个计划的详细信息，包括价格、功能限制等
    """
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
    """
    获取当前用户的订阅信息

    包括当前计划、状态、账单周期等
    """
    user_id = current_user["id"]
    subscription = get_user_subscription(user_id)
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
    current_user: dict = Depends(get_current_user),
):
    """
    升级订阅

    当前为模拟实现：
    1. 验证目标计划
    2. 生成模拟 checkout session
    3. 返回模拟成功响应

    集成 Stripe 时替换为：
    1. 创建 Stripe Checkout Session
    2. 返回 stripe.checkout.session.completed webhook
    3. 更新用户订阅状态
    """
    user_id = current_user["id"]
    target_plan = request.plan

    # 验证目标计划
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
    # TODO: 集成 Stripe 时替换此处
    #
    # Stripe 集成代码示例：
    #
    # from app.services.stripe import stripe_service
    #
    # checkout_session = stripe_service.create_checkout_session(
    #     user_id=user_id,
    #     email=current_user['email'],
    #     plan_id=target_plan,
    #     price_id=plan_info['stripe_price_id'],
    #     success_url="/upgrade/success?session_id={CHECKOUT_SESSION_ID}",
    #     cancel_url="/upgrade?canceled=true",
    # )
    #
    # return UpgradeResponse(
    #     success=True,
    #     message="Redirecting to Stripe checkout",
    #     checkout_url=checkout_session.url,
    # )
    # ==================== END STRIPE INTEGRATION PLACEHOLDER ====================

    # 模拟：直接升级（不经过支付）
    # 更新用户订阅状态
    next_billing = _get_next_billing_date()
    FAKE_SUBSCRIPTIONS_DB[user_id] = {
        "plan": target_plan,
        "status": "active",
        "current_period_start": datetime.utcnow().isoformat(),
        "current_period_end": next_billing.isoformat(),
        "cancel_at_period_end": False,
        "stripe_customer_id": f"cus_mock_{user_id}",
        "stripe_subscription_id": f"sub_mock_{user_id}_{int(datetime.utcnow().timestamp())}",
    }

    # 同步更新用户表中的订阅等级（通过修改 FAKE_USERS_DB）
    # 注意：这里需要访问 auth.py 中的 FAKE_USERS_DB
    from app.api.auth import FAKE_USERS_DB
    if user_id in FAKE_USERS_DB:
        FAKE_USERS_DB[user_id]["subscription_tier"] = target_plan

    return UpgradeResponse(
        success=True,
        message=f"Successfully upgraded to {plan_info['name']}!",
        checkout_url=None,  # 模拟模式，不需要跳转
    )


@router.post(
    "/cancel",
    response_model=CancelResponse,
    summary="取消订阅",
    description="取消当前订阅（降级到免费计划）",
)
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """
    取消订阅

    将订阅设置为在当前周期结束时取消
    用户可以继续使用直到当前周期结束

    注意：取消不等于立即降级，而是设置 cancel_at_period_end = True
    当前周期结束后自动降级为 Free
    """
    user_id = current_user["id"]
    subscription = get_user_subscription(user_id)

    if subscription["plan"] == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already on the free plan",
        )

    # ==================== STRIPE INTEGRATION PLACEHOLDER ====================
    # TODO: 集成 Stripe 时替换为：
    # stripe_service.cancel_subscription(subscription["stripe_subscription_id"])
    # ==================== END STRIPE INTEGRATION PLACEHOLDER ====================

    # 模拟：设置取消标志
    subscription["cancel_at_period_end"] = True
    FAKE_SUBSCRIPTIONS_DB[user_id] = subscription

    logger.info(f"User {current_user['email']} cancelled subscription (plan: {subscription['plan']})")

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
    """
    获取用户用量统计

    包括：
    - 今日搜索次数和每日限制
    - 本月每日用量明细
    - 本月总用量
    """
    user_id = current_user["id"]
    subscription = get_user_subscription(user_id)
    plan_info = SUBSCRIPTION_PLANS.get(subscription["plan"], SUBSCRIPTION_PLANS["free"])

    today_count = get_user_usage_today(user_id)
    searches_per_day = plan_info.get("searches_per_day", 10)
    monthly_usage = get_monthly_usage(user_id)
    monthly_total = sum(monthly_usage.values())

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
    """
    获取用户功能访问权限

    用于前端根据权限显示/隐藏功能按钮
    """
    user_id = current_user["id"]
    subscription = get_user_subscription(user_id)
    plan_info = SUBSCRIPTION_PLANS.get(subscription["plan"], SUBSCRIPTION_PLANS["free"])

    return FeatureAccessResponse(
        ai_summaries=plan_info["ai_summaries"],
        entity_extraction=plan_info["entity_extraction"],
        similar_cases=plan_info["similar_cases"],
        api_access=plan_info["api_access"],
        team_accounts=plan_info["team_accounts"],
        can_search=True,  # 所有人都可以搜索，只是限制次数
    )


# ==================== Webhook Endpoint (for Stripe integration) ====================
# 注意：Webhook 需要在 Stripe Dashboard 中配置
# 当 Stripe Checkout Session 完成时会触发此端点

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
    2. 处理 checkout.session.completed 事件
    3. 处理 customer.subscription.updated 事件
    4. 处理 customer.subscription.deleted 事件

    示例实现：
    - checkout.session.completed: 升级用户订阅
    - invoice.payment_succeeded: 续订订阅
    - customer.subscription.deleted: 降级到免费计划
    """
    # ==================== STRIPE INTEGRATION PLACEHOLDER ====================
    # TODO: 集成 Stripe 时实现完整 webhook 处理
    #
    # from app.services.stripe import stripe_service
    #
    # # 验证 webhook 签名
    # event = stripe_service.verify_webhook_signature(
    #     payload=payload,
    #     sig_header=headers.get("stripe-signature"),
    # )
    #
    # if event["type"] == "checkout.session.completed":
    #     session = event["data"]["object"]
    #     user_id = int(session["metadata"]["user_id"])
    #     plan_id = session["metadata"]["plan_id"]
    #
    #     # 更新订阅状态
    #     FAKE_SUBSCRIPTIONS_DB[user_id] = {
    #         "plan": plan_id,
    #         "status": "active",
    #         "stripe_subscription_id": session["subscription"],
    #         "stripe_customer_id": session["customer"],
    #         ...
    #     }
    #
    # elif event["type"] == "customer.subscription.deleted":
    #     # 降级到免费计划
    #     subscription = event["data"]["object"]
    #     customer_id = subscription["customer"]
    #     # ... 查找并更新用户
    #
    # return {"received": True}
    # ==================== END STRIPE INTEGRATION PLACEHOLDER ====================

    return {"received": True, "note": "Webhook endpoint - integrate Stripe to activate"}
