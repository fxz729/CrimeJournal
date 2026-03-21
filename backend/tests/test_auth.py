"""
认证API测试

测试用户注册、登录、Token验证等功能
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.api.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
    FAKE_USERS_DB,
)


class TestPasswordHashing:
    """密码哈希测试"""

    def test_password_hash_not_plain(self):
        """密码哈希后不应是明文"""
        password = "MySecurePass123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 20

    def test_password_hash_different_each_time(self):
        """每次哈希应产生不同结果（使用salt）"""
        password = "MySecurePass123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        # bcrypt每次生成不同的hash，但仍能验证
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """验证正确密码"""
        password = "MySecurePass123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """验证错误密码"""
        password = "MySecurePass123!"
        hashed = get_password_hash(password)
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty(self):
        """验证空密码"""
        password = "MySecurePass123!"
        hashed = get_password_hash(password)
        assert verify_password("", hashed) is False


class TestJWTToken:
    """JWT Token测试"""

    def test_create_access_token(self):
        """创建Token"""
        token = create_access_token(user_id=1, email="test@example.com")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    def test_decode_token_valid(self):
        """解码有效Token"""
        user_id = 42
        email = "decode@example.com"
        token = create_access_token(user_id=user_id, email=email)

        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["email"] == email

    def test_decode_token_invalid(self):
        """解码无效Token应抛出异常"""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_decode_token_tampered(self):
        """解码被篡改的Token应抛出异常"""
        from fastapi import HTTPException
        token = create_access_token(user_id=1, email="test@example.com")
        # 篡改token
        tampered = token[:-5] + "xxxxx"
        with pytest.raises(HTTPException) as exc_info:
            decode_token(tampered)
        assert exc_info.value.status_code == 401


class TestAuthAPI:
    """认证API测试"""

    # ==================== 用户注册 ====================

    def test_register_success(self, client: TestClient, test_user_data):
        """注册成功"""
        response = client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()

        # 验证响应结构
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert data["user"]["full_name"] == test_user_data["full_name"]
        assert data["user"]["subscription_tier"] == "free"
        assert data["user"]["is_active"] is True

        # 验证Token
        assert "access_token" in data["token"]
        assert data["token"]["token_type"] == "bearer"
        assert data["token"]["expires_in"] > 0

    def test_register_duplicate_email(self, client: TestClient, test_user_data):
        """重复邮箱注册应失败"""
        # 第一次注册
        response1 = client.post("/api/auth/register", json=test_user_data)
        assert response1.status_code == 201

        # 第二次注册同一邮箱
        response2 = client.post("/api/auth/register", json=test_user_data)
        assert response2.status_code == 400
        assert "已注册" in response2.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """无效邮箱格式"""
        response = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePass123!",
        })
        assert response.status_code == 422  # Pydantic验证失败

    def test_register_short_password(self, client: TestClient):
        """密码过短"""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "12345",  # 少于6位
        })
        assert response.status_code == 422

    def test_register_long_password(self, client: TestClient):
        """密码过长"""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "a" * 101,  # 超过100位
        })
        assert response.status_code == 422

    def test_register_without_full_name(self, client: TestClient):
        """注册可不提供姓名"""
        response = client.post("/api/auth/register", json={
            "email": "noname@example.com",
            "password": "SecurePass123!",
        })
        assert response.status_code == 201
        assert response.json()["user"]["full_name"] is None

    def test_register_empty_body(self, client: TestClient):
        """空请求体"""
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422

    def test_register_missing_email(self, client: TestClient):
        """缺少邮箱字段"""
        response = client.post("/api/auth/register", json={
            "password": "SecurePass123!",
        })
        assert response.status_code == 422

    def test_register_missing_password(self, client: TestClient):
        """缺少密码字段"""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
        })
        assert response.status_code == 422

    # ==================== 用户登录 ====================

    def test_login_success(self, client: TestClient, test_user_data):
        """登录成功"""
        # 先注册
        client.post("/api/auth/register", json=test_user_data)

        # 再登录
        response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })

        assert response.status_code == 200
        data = response.json()

        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert "access_token" in data["token"]

    def test_login_wrong_password(self, client: TestClient, test_user_data):
        """密码错误"""
        # 先注册
        client.post("/api/auth/register", json=test_user_data)

        # 使用错误密码登录
        response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": "WrongPassword123!",
        })

        assert response.status_code == 401
        assert "邮箱或密码错误" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """用户不存在"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        })

        assert response.status_code == 401
        assert "邮箱或密码错误" in response.json()["detail"]

    def test_login_invalid_email_format(self, client: TestClient):
        """无效邮箱格式"""
        response = client.post("/api/auth/login", json={
            "email": "not-valid-email",
            "password": "password123",
        })
        assert response.status_code == 422

    def test_login_empty_credentials(self, client: TestClient):
        """空凭据"""
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422

    def test_login_missing_password(self, client: TestClient):
        """缺少密码"""
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
        })
        assert response.status_code == 422

    def test_login_inactive_user(self, client: TestClient, test_user_data):
        """禁用用户登录"""
        from app.api import auth as auth_module

        # 注册用户
        client.post("/api/auth/register", json=test_user_data)

        # 手动禁用用户
        for user_id, user in auth_module.FAKE_USERS_DB.items():
            if user["email"] == test_user_data["email"]:
                user["is_active"] = False
                break

        # 尝试登录
        response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })

        assert response.status_code == 403
        assert "禁用" in response.json()["detail"]

    # ==================== 获取当前用户 ====================

    def test_get_current_user(self, client: TestClient, test_user_data, create_auth_token):
        """获取当前用户信息"""
        # 注册
        client.post("/api/auth/register", json=test_user_data)

        # 生成Token
        token = create_auth_token(user_id=1, email=test_user_data["email"])

        # 获取当前用户
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]

    def test_get_current_user_no_token(self, client: TestClient):
        """无Token访问"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # HTTPBearer默认返回403

    def test_get_current_user_invalid_token(self, client: TestClient):
        """无效Token访问"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token"}
        )
        assert response.status_code == 401

    def test_get_current_user_expired_token(self, client: TestClient):
        """过期Token访问"""
        from datetime import datetime, timedelta
        import jwt
        from app.config import settings

        # 创建已过期的Token
        expire = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "sub": "1",
            "email": "test@example.com",
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        expired_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert "过期" in response.json()["detail"]

    def test_get_current_user_nonexistent_user(self, client: TestClient, create_auth_token):
        """Token中的用户不存在"""
        # 用不存在的user_id生成token
        token = create_auth_token(user_id=9999, email="ghost@example.com")

        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    # ==================== 登出 ====================

    def test_logout(self, client: TestClient, test_user_data, create_auth_token):
        """登出"""
        # 注册
        client.post("/api/auth/register", json=test_user_data)

        # 生成Token
        token = create_auth_token(user_id=1, email=test_user_data["email"])

        # 登出
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "登出成功"

    def test_logout_no_token(self, client: TestClient):
        """无Token登出"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 403

    # ==================== Token刷新 ====================

    def test_refresh_token(self, client: TestClient, test_user_data, create_auth_token):
        """刷新Token"""
        # 注册
        client.post("/api/auth/register", json=test_user_data)

        # 生成Token
        token = create_auth_token(user_id=1, email=test_user_data["email"])

        # 刷新Token
        response = client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_refresh_token_no_auth(self, client: TestClient):
        """无认证刷新Token"""
        response = client.post("/api/auth/refresh")
        assert response.status_code == 403


class TestAuthIntegration:
    """认证集成测试"""

    def test_full_auth_flow(self, client: TestClient):
        """完整认证流程：注册 -> 登录 -> 获取用户 -> 登出"""
        user_data = {
            "email": "integration@example.com",
            "password": "TestPass123!",
            "full_name": "Integration Test",
        }

        # 1. 注册
        reg_response = client.post("/api/auth/register", json=user_data)
        assert reg_response.status_code == 201
        reg_data = reg_response.json()
        assert "access_token" in reg_data["token"]

        token = reg_data["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 获取当前用户
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == user_data["email"]

        # 3. 刷新Token
        refresh_response = client.post("/api/auth/refresh", headers=headers)
        assert refresh_response.status_code == 200

        # 4. 登出
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200

        # 5. 旧Token仍可使用（JWT无状态，登出不使Token失效）
        me_after_logout = client.get("/api/auth/me", headers=headers)
        assert me_after_logout.status_code == 200

    def test_login_after_register_same_password(self, client: TestClient, test_user_data):
        """注册后使用相同密码登录"""
        # 注册
        client.post("/api/auth/register", json=test_user_data)

        # 登录
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })

        assert login_response.status_code == 200
        # 两次获得的Token不同（每次生成新Token）
        assert "access_token" in login_response.json()["token"]

    def test_multiple_users_isolated(self, client: TestClient):
        """多用户数据隔离"""
        user1 = {"email": "user1@example.com", "password": "Pass123456!", "full_name": "User One"}
        user2 = {"email": "user2@example.com", "password": "Pass654321!", "full_name": "User Two"}

        # 注册两个用户
        client.post("/api/auth/register", json=user1)
        client.post("/api/auth/register", json=user2)

        # 登录用户1
        login1 = client.post("/api/auth/login", json={
            "email": user1["email"],
            "password": user1["password"],
        })
        assert login1.status_code == 200
        token1 = login1.json()["token"]["access_token"]

        # 登录用户2
        login2 = client.post("/api/auth/login", json={
            "email": user2["email"],
            "password": user2["password"],
        })
        assert login2.status_code == 200
        token2 = login2.json()["token"]["access_token"]

        # 使用用户1的Token获取用户信息，应得到用户1的数据
        me1 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token1}"})
        assert me1.json()["email"] == user1["email"]

        # 使用用户2的Token获取用户信息，应得到用户2的数据
        me2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token2}"})
        assert me2.json()["email"] == user2["email"]
