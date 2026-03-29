"""
Subscription API Tests

测试订阅管理、用量统计等功能
"""
import pytest
from fastapi.testclient import TestClient

from app.api.subscriptions import (
    SUBSCRIPTION_PLANS,
    _get_user_subscription_info,
    _increment_daily_search,
    _reset_daily_search_if_needed,
)
from app.api.auth import get_session_local, DBUser


class TestSubscriptionPlans:
    """订阅计划测试"""

    def test_subscription_plans_exist(self):
        """订阅计划已定义"""
        assert "free" in SUBSCRIPTION_PLANS
        assert "pro" in SUBSCRIPTION_PLANS
        assert "enterprise" in SUBSCRIPTION_PLANS

    def test_free_plan_limits(self):
        """Free计划限制"""
        free_plan = SUBSCRIPTION_PLANS["free"]
        assert free_plan["searches_per_day"] == 10
        assert free_plan["ai_summaries"] is False
        assert free_plan["entity_extraction"] is False
        assert free_plan["price"] == 0

    def test_pro_plan_limits(self):
        """Pro计划限制"""
        pro_plan = SUBSCRIPTION_PLANS["pro"]
        assert pro_plan["searches_per_day"] == -1  # unlimited
        assert pro_plan["ai_summaries"] is True
        assert pro_plan["entity_extraction"] is True
        assert pro_plan["similar_cases"] is True
        assert pro_plan["price"] == 290

    def test_enterprise_plan_limits(self):
        """Enterprise计划限制"""
        enterprise_plan = SUBSCRIPTION_PLANS["enterprise"]
        assert enterprise_plan["searches_per_day"] == -1  # unlimited
        assert enterprise_plan["ai_summaries"] is True
        assert enterprise_plan["api_access"] is True
        assert enterprise_plan["team_accounts"] is True
        assert enterprise_plan["price"] == 590


class TestSubscriptionAPI:
    """订阅API测试基类"""

    @pytest.fixture
    def user_token(self, client: TestClient):
        """创建已认证用户的Token"""
        user_data = {
            "email": "sub_test@example.com",
            "password": "SubPass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        return reg_resp.json()["token"]["access_token"]

    @pytest.fixture
    def auth_header(self, user_token: str):
        """认证请求头"""
        return {"Authorization": f"Bearer {user_token}"}


class TestGetPlans(TestSubscriptionAPI):
    """获取订阅计划测试"""

    def test_get_plans_success(self, client: TestClient):
        """获取订阅计划列表"""
        response = client.get("/api/subscriptions/plans")
        assert response.status_code == 200
        data = response.json()
        assert "free" in data
        assert "pro" in data
        assert "enterprise" in data
        free_plan = data["free"]
        assert free_plan["id"] == "free"
        assert free_plan["name"] == "Free"
        assert free_plan["searches_per_day"] == 10
        assert free_plan["ai_summaries"] is False
        pro_plan = data["pro"]
        assert pro_plan["id"] == "pro"
        assert pro_plan["name"] == "Pro"
        assert pro_plan["searches_per_day"] == -1
        assert pro_plan["ai_summaries"] is True

    def test_get_plans_no_auth_required(self, client: TestClient):
        """获取计划不需要认证"""
        response = client.get("/api/subscriptions/plans")
        assert response.status_code == 200


class TestGetMySubscription(TestSubscriptionAPI):
    """获取我的订阅测试"""

    def test_get_my_subscription_free(self, client: TestClient, auth_header):
        """获取默认免费订阅"""
        response = client.get("/api/subscriptions/me", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["plan"] == "free"
        assert data["plan_name"] == "Free"
        assert data["status"] == "active"
        assert "current_period_start" in data
        assert "current_period_end" in data
        assert data["cancel_at_period_end"] is False
        assert "features" in data
        features = data["features"]
        assert features["ai_summaries"] is False
        assert features["entity_extraction"] is False

    def test_get_my_subscription_no_auth(self, client: TestClient):
        """无认证获取订阅应失败"""
        response = client.get("/api/subscriptions/me")
        assert response.status_code == 401


class TestUpgradeSubscription(TestSubscriptionAPI):
    """升级订阅测试"""

    def test_upgrade_to_pro(self, client: TestClient, auth_header):
        """升级到Pro计划"""
        response = client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "pro"},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Pro" in data["message"]

    def test_upgrade_to_enterprise(self, client: TestClient, auth_header):
        """升级到Enterprise计划"""
        response = client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "enterprise"},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Enterprise" in data["message"]

    def test_upgrade_invalid_plan(self, client: TestClient, auth_header):
        """无效计划"""
        response = client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "invalid_plan"},
            headers=auth_header,
        )
        assert response.status_code == 400
        assert "Invalid plan" in response.json()["detail"]

    def test_upgrade_to_free(self, client: TestClient, auth_header):
        """不能升级到free计划"""
        response = client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "free"},
            headers=auth_header,
        )
        assert response.status_code == 400
        assert "Cannot upgrade to free plan" in response.json()["detail"]

    def test_upgrade_no_auth(self, client: TestClient):
        """无认证升级应失败"""
        response = client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "pro"},
        )
        assert response.status_code == 401

    def test_upgrade_missing_plan(self, client: TestClient, auth_header):
        """缺少plan参数"""
        response = client.post(
            "/api/subscriptions/upgrade",
            json={},
            headers=auth_header,
        )
        assert response.status_code == 422


class TestCancelSubscription(TestSubscriptionAPI):
    """取消订阅测试"""

    def test_cancel_pro_subscription(self, client: TestClient, auth_header):
        """取消Pro订阅"""
        # 先升级到Pro
        client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "pro"},
            headers=auth_header,
        )
        # 取消订阅
        response = client.post(
            "/api/subscriptions/cancel",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cancelled" in data["message"].lower() or "end" in data["message"].lower()
        assert "current_period_end" in data

    def test_cancel_free_subscription(self, client: TestClient, auth_header):
        """取消免费订阅应失败"""
        response = client.post(
            "/api/subscriptions/cancel",
            headers=auth_header,
        )
        assert response.status_code == 400
        assert "free plan" in response.json()["detail"].lower()

    def test_cancel_no_auth(self, client: TestClient):
        """无认证取消应失败"""
        response = client.post("/api/subscriptions/cancel")
        assert response.status_code == 401


class TestGetUsage(TestSubscriptionAPI):
    """获取用量统计测试"""

    def test_get_usage_free_user(self, client: TestClient, auth_header):
        """获取免费用户用量"""
        response = client.get("/api/subscriptions/usage", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert "today_searches" in data
        assert "daily_limit" in data
        assert "is_unlimited" in data
        assert "monthly_usage" in data
        assert "monthly_total" in data
        assert data["is_unlimited"] is False
        assert data["daily_limit"] == 10

    def test_get_usage_pro_user(self, client: TestClient, auth_header):
        """获取Pro用户用量"""
        # 先升级到Pro
        client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "pro"},
            headers=auth_header,
        )
        response = client.get("/api/subscriptions/usage", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["is_unlimited"] is True
        assert data["daily_limit"] == -1

    def test_get_usage_no_auth(self, client: TestClient):
        """无认证获取用量应失败"""
        response = client.get("/api/subscriptions/usage")
        assert response.status_code == 401


class TestGetFeatureAccess(TestSubscriptionAPI):
    """获取功能权限测试"""

    def test_get_features_free_user(self, client: TestClient, auth_header):
        """获取免费用户功能权限"""
        response = client.get("/api/subscriptions/features", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert "ai_summaries" in data
        assert "entity_extraction" in data
        assert "similar_cases" in data
        assert "api_access" in data
        assert "team_accounts" in data
        assert "can_search" in data
        assert data["ai_summaries"] is False
        assert data["entity_extraction"] is False
        assert data["similar_cases"] is False
        assert data["can_search"] is True  # 所有人都可以搜索

    def test_get_features_pro_user(self, client: TestClient, auth_header):
        """获取Pro用户功能权限"""
        client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "pro"},
            headers=auth_header,
        )
        response = client.get("/api/subscriptions/features", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["ai_summaries"] is True
        assert data["entity_extraction"] is True
        assert data["similar_cases"] is True
        assert data["api_access"] is False  # Enterprise专属

    def test_get_features_enterprise_user(self, client: TestClient, auth_header):
        """获取Enterprise用户功能权限"""
        client.post(
            "/api/subscriptions/upgrade",
            json={"plan": "enterprise"},
            headers=auth_header,
        )
        response = client.get("/api/subscriptions/features", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["ai_summaries"] is True
        assert data["entity_extraction"] is True
        assert data["similar_cases"] is True
        assert data["api_access"] is True
        assert data["team_accounts"] is True

    def test_get_features_no_auth(self, client: TestClient):
        """无认证获取功能应失败"""
        response = client.get("/api/subscriptions/features")
        assert response.status_code == 401


class TestWebhookEndpoint(TestSubscriptionAPI):
    """Webhook端点测试"""

    def test_webhook_no_auth(self, client: TestClient):
        """无认证访问webhook应失败"""
        response = client.post("/api/subscriptions/webhook", json={})
        assert response.status_code == 401

    def test_webhook_no_implementation(self, client: TestClient, auth_header):
        """Webhook端点存在但未实现"""
        response = client.post(
            "/api/subscriptions/webhook",
            json={"type": "checkout.session.completed"},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("received") is True


class TestSubscriptionHelperFunctions:
    """订阅辅助函数测试（SQLite-backed）"""

    @pytest.fixture
    def clean_user(self):
        """确保测试用户存在于数据库"""
        from app.api.auth import get_session_local, DBUser, get_password_hash
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            # 查找或创建测试用户
            user = db.query(DBUser).filter(DBUser.email == "helper_test@example.com").first()
            if user is None:
                user = DBUser(
                    email="helper_test@example.com",
                    hashed_password=get_password_hash("HelperPass123!"),
                    full_name="Helper Test",
                    subscription_tier="free",
                    is_active=True,
                    is_verified=False,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                user.subscription_tier = "free"
                user.daily_search_count = 0
                user.last_search_date = None
                db.commit()
            yield user.id
        finally:
            db.close()

    def test_get_user_subscription_info_default(self, clean_user):
        """获取默认免费订阅"""
        subscription = _get_user_subscription_info(clean_user)
        assert subscription["plan"] == "free"
        assert subscription["status"] == "active"

    def test_get_user_subscription_info_nonexistent(self):
        """不存在的用户返回免费计划"""
        subscription = _get_user_subscription_info(999999)
        assert subscription["plan"] == "free"
        assert subscription["status"] == "active"

    def test_increment_daily_search(self, clean_user):
        """增加每日搜索计数"""
        count = _increment_daily_search(clean_user)
        assert count == 1
        count = _increment_daily_search(clean_user)
        assert count == 2
        count = _increment_daily_search(clean_user)
        assert count == 3

    def test_reset_daily_search_if_needed(self, clean_user):
        """重置每日搜索计数（新的一天）"""
        # 先增加计数
        _increment_daily_search(clean_user)
        _increment_daily_search(clean_user)
        # 重置（如果日期变了）
        count = _reset_daily_search_if_needed(clean_user)
        # 第一次调用会在新日期时重置为1，或返回当前计数
        assert count >= 1
