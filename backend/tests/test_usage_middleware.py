"""
Usage Middleware Tests

测试用量限制中间件和辅助函数（SQLite-backed）
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

from app.middleware.usage import (
    DAILY_SEARCH_LIMITS,
    get_today_str,
    get_user_daily_usage,
    increment_user_usage,
    get_daily_limit,
    check_and_record_search,
    UsageLimitMiddleware,
    check_search_access,
)
from app.api.auth import get_session_local, DBUser, get_password_hash


@pytest.fixture
def setup_test_user():
    """创建测试用户并清理用量"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.email == "usage_test@example.com").first()
        if user is None:
            user = DBUser(
                email="usage_test@example.com",
                hashed_password=get_password_hash("UsagePass123!"),
                full_name="Usage Test",
                subscription_tier="free",
                is_active=True,
                is_verified=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.daily_search_count = 0
            user.last_search_date = None
            db.commit()
        yield user.id
    finally:
        user.daily_search_count = 0
        user.last_search_date = None
        db.commit()
        db.close()


class TestDailySearchLimits:
    """每日搜索限制配置测试"""

    def test_free_limit(self):
        """Free用户限制"""
        assert DAILY_SEARCH_LIMITS["free"] == 10

    def test_pro_limit(self):
        """Pro用户限制（无限制）"""
        assert DAILY_SEARCH_LIMITS["pro"] == -1

    def test_enterprise_limit(self):
        """Enterprise用户限制（无限制）"""
        assert DAILY_SEARCH_LIMITS["enterprise"] == -1

    def test_unknown_tier_defaults_to_free(self):
        """未知订阅等级默认为Free限制"""
        assert get_daily_limit("unknown_tier") == DAILY_SEARCH_LIMITS["free"]


class TestGetTodayStr:
    """获取今日日期字符串测试"""

    def test_get_today_str_format(self):
        """日期格式为YYYY-MM-DD"""
        today_str = get_today_str()
        assert len(today_str) == 10
        assert today_str[4] == "-"
        assert today_str[7] == "-"

    def test_get_today_str_is_valid(self):
        """日期字符串可以解析"""
        today_str = get_today_str()
        parsed = date.fromisoformat(today_str)
        assert parsed == date.today()


class TestGetUserDailyUsage:
    """获取用户每日用量测试（SQLite）"""

    def test_no_usage_returns_zero(self, setup_test_user):
        """无用量返回0"""
        usage = get_user_daily_usage(setup_test_user)
        assert usage == 0

    def test_with_usage_returns_count(self, setup_test_user):
        """有用量返回计数"""
        user_id = setup_test_user
        # 直接写入SQLite
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            user = db.query(DBUser).filter(DBUser.id == user_id).first()
            user.daily_search_count = 5
            user.last_search_date = __import__("datetime").datetime.utcnow()
            db.commit()
        finally:
            db.close()

        usage = get_user_daily_usage(user_id)
        assert usage == 5


class TestIncrementUserUsage:
    """增加用户用量测试（SQLite）"""

    def test_increment_new_user(self, setup_test_user):
        """新用户从0开始"""
        count = increment_user_usage(setup_test_user)
        assert count == 1

    def test_increment_existing_user(self, setup_test_user):
        """已存在用户递增"""
        user_id = setup_test_user
        # 先设置初始计数
        increment_user_usage(user_id)
        increment_user_usage(user_id)
        increment_user_usage(user_id)
        increment_user_usage(user_id)
        increment_user_usage(user_id)

        count = increment_user_usage(user_id)
        assert count == 6


class TestGetDailyLimit:
    """获取每日限制测试"""

    def test_free_plan_limit(self):
        """Free计划限制10次"""
        limit = get_daily_limit("free")
        assert limit == 10

    def test_pro_plan_limit(self):
        """Pro计划无限制"""
        limit = get_daily_limit("pro")
        assert limit == -1

    def test_enterprise_plan_limit(self):
        """Enterprise计划无限制"""
        limit = get_daily_limit("enterprise")
        assert limit == -1


class TestCheckAndRecordSearch:
    """检查并记录搜索测试（SQLite）"""

    def test_anonymous_user_no_limit(self):
        """匿名用户不限制"""
        allowed, msg, count, limit = check_and_record_search(
            user_id=None,
            subscription_tier="free"
        )
        assert allowed is True
        assert msg == ""
        assert count == 0
        assert limit == 0

    def test_free_user_within_limit(self, setup_test_user):
        """Free用户在限制内"""
        user_id = setup_test_user
        # 设置初始计数
        for _ in range(5):
            increment_user_usage(user_id)

        allowed, msg, count, limit = check_and_record_search(
            user_id=user_id,
            subscription_tier="free"
        )
        assert allowed is True
        assert msg == ""
        assert count == 6  # 记录后递增
        assert limit == 10

    def test_pro_user_unlimited(self, setup_test_user):
        """Pro用户无限制"""
        user_id = setup_test_user
        # 即使大量记录，也应该允许
        for _ in range(100):
            allowed, msg, count, limit = check_and_record_search(
                user_id=user_id,
                subscription_tier="pro"
            )
            assert allowed is True
            assert msg == ""
            assert limit == -1


class TestCheckSearchAccess:
    """检查搜索访问权限测试（SQLite）"""

    def test_free_user_within_limit_no_exception(self, setup_test_user):
        """Free用户在限制内不抛异常"""
        user_id = setup_test_user
        # 先设置5次
        for _ in range(5):
            increment_user_usage(user_id)
        # 不应抛出异常
        check_search_access(user_id=user_id, subscription_tier="free")

    def test_free_user_at_limit_raises(self, setup_test_user):
        """Free用户达到限制时抛出异常"""
        user_id = setup_test_user
        # 直接设置到10次
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            user = db.query(DBUser).filter(DBUser.id == user_id).first()
            user.daily_search_count = 10
            user.last_search_date = __import__("datetime").datetime.utcnow()
            db.commit()
        finally:
            db.close()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            check_search_access(user_id=user_id, subscription_tier="free")
        assert exc_info.value.status_code == 429
        assert "daily_limit_reached" in exc_info.value.detail["error"]

    def test_pro_user_never_raises(self, setup_test_user):
        """Pro用户永远不会抛异常"""
        user_id = setup_test_user
        # 不应抛出异常
        check_search_access(user_id=user_id, subscription_tier="pro")


class TestUsageLimitMiddleware:
    """用量限制中间件测试"""

    @pytest.fixture
    def mock_app(self):
        """创建模拟FastAPI应用"""
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/api/cases/search")
        async def search():
            return {"results": []}

        @app.get("/other")
        async def other():
            return {"message": "other"}

        return app

    def test_middleware_allows_non_search_paths(self, mock_app):
        """中间件允许非搜索路径"""
        middleware = UsageLimitMiddleware(mock_app)
        assert "/other" not in middleware.PROTECTED_PATHS

    def test_middleware_protects_search_path(self, mock_app):
        """中间件保护搜索路径"""
        middleware = UsageLimitMiddleware(mock_app)
        assert "/api/cases/search" in middleware.PROTECTED_PATHS

    def test_protected_paths_configuration(self):
        """保护路径配置"""
        middleware = UsageLimitMiddleware(app=MagicMock())
        assert isinstance(middleware.PROTECTED_PATHS, list)
        assert len(middleware.PROTECTED_PATHS) > 0


class TestUsageIntegration:
    """用量限制集成测试（SQLite）"""

    def test_free_user_daily_limit_flow(self, setup_test_user):
        """Free用户每日限制流程"""
        user_id = setup_test_user

        for i in range(12):
            allowed, msg, count, limit = check_and_record_search(
                user_id=user_id,
                subscription_tier="free"
            )

            if i < 10:
                assert allowed is True
                assert count == i + 1
            else:
                assert allowed is False
                assert "limit" in msg.lower()

    def test_pro_user_unlimited_flow(self, setup_test_user):
        """Pro用户无限制流程"""
        user_id = setup_test_user

        for _ in range(100):
            allowed, msg, count, limit = check_and_record_search(
                user_id=user_id,
                subscription_tier="pro"
            )
            assert allowed is True
            assert limit == -1
