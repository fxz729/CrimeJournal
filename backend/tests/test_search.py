"""
Search API Tests

测试搜索历史、收藏夹等功能
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from app.api.search import (
    FAKE_SEARCH_HISTORY,
    FAKE_FAVORITES,
)


class TestSearchHistoryAPI:
    """搜索历史API测试基类"""

    @pytest.fixture
    def user_token(self, client: TestClient):
        """创建已认证用户的Token"""
        user_data = {
            "email": "search_test@example.com",
            "password": "SearchPass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        return reg_resp.json()["token"]["access_token"]

    @pytest.fixture
    def auth_header(self, user_token: str):
        """认证请求头"""
        return {"Authorization": f"Bearer {user_token}"}


class TestGetSearchHistory(TestSearchHistoryAPI):
    """获取搜索历史测试"""

    def test_get_history_empty(self, client: TestClient, auth_header):
        """空搜索历史"""
        response = client.get("/api/search/history", headers=auth_header)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 0
        assert data["items"] == []

    def test_get_history_with_data(self, client: TestClient):
        """有数据的搜索历史"""
        # 添加搜索历史
        from app.api.search import FAKE_SEARCH_HISTORY

        # 注册用户
        user_data = {
            "email": "history_test@example.com",
            "password": "HistoryPass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        token = reg_resp.json()["token"]["access_token"]
        user_id = reg_resp.json()["user"]["id"]

        # 添加两条历史记录，使用正确的user_id
        FAKE_SEARCH_HISTORY[1] = {
            "id": 1,
            "user_id": user_id,
            "query": "robbery case",
            "filters": '{"court": "calapp"}',
            "created_at": datetime.utcnow(),
        }
        FAKE_SEARCH_HISTORY[2] = {
            "id": 2,
            "user_id": user_id,
            "query": "murder trial",
            "filters": None,
            "created_at": datetime.utcnow(),
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/search/history", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_get_history_pagination(self, client: TestClient):
        """搜索历史分页"""
        # 注册用户
        user_data = {
            "email": "page_test@example.com",
            "password": "PagePass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        token = reg_resp.json()["token"]["access_token"]
        user_id = reg_resp.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 添加多条历史记录
        for i in range(25):
            FAKE_SEARCH_HISTORY[i + 100] = {
                "id": i + 100,
                "user_id": user_id,
                "query": f"test query {i}",
                "filters": None,
                "created_at": datetime.utcnow(),
            }

        # 第1页，每页10条
        response = client.get(
            "/api/search/history",
            params={"page": 1, "page_size": 10},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["items"]) == 10

        # 第2页
        response2 = client.get(
            "/api/search/history",
            params={"page": 2, "page_size": 10},
            headers=headers,
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) == 10

        # 第3页
        response3 = client.get(
            "/api/search/history",
            params={"page": 3, "page_size": 10},
            headers=headers,
        )

        assert response3.status_code == 200
        data3 = response3.json()
        assert len(data3["items"]) == 5

    def test_get_history_invalid_page(self, client: TestClient, auth_header):
        """无效页码"""
        response = client.get(
            "/api/search/history",
            params={"page": 0},
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_get_history_page_size_limit(self, client: TestClient, auth_header):
        """page_size超过限制"""
        response = client.get(
            "/api/search/history",
            params={"page_size": 101},
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_get_history_no_auth(self, client: TestClient):
        """无认证获取历史应失败"""
        response = client.get("/api/search/history")
        assert response.status_code == 401


class TestDeleteSearchHistory(TestSearchHistoryAPI):
    """删除搜索历史测试"""

    def test_delete_history_success(self, client: TestClient):
        """删除历史记录成功"""
        # 注册用户
        user_data = {
            "email": "delete_hist_test@example.com",
            "password": "DeletePass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        token = reg_resp.json()["token"]["access_token"]
        user_id = reg_resp.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 添加历史记录
        FAKE_SEARCH_HISTORY[1] = {
            "id": 1,
            "user_id": user_id,
            "query": "test query",
            "filters": None,
            "created_at": datetime.utcnow(),
        }

        # 删除
        response = client.delete("/api/search/history/1", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "删除成功"
        assert data["success"] is True

    def test_delete_history_not_found(self, client: TestClient, auth_header):
        """删除不存在的历史"""
        response = client.delete("/api/search/history/99999", headers=auth_header)
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]

    def test_delete_history_no_auth(self, client: TestClient):
        """无认证删除应失败"""
        response = client.delete("/api/search/history/1")
        assert response.status_code == 401


class TestClearSearchHistory(TestSearchHistoryAPI):
    """清空搜索历史测试"""

    def test_clear_history_success(self, client: TestClient):
        """清空历史成功"""
        # 注册用户
        user_data = {
            "email": "clear_hist_test@example.com",
            "password": "ClearPass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        token = reg_resp.json()["token"]["access_token"]
        user_id = reg_resp.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 添加历史记录
        FAKE_SEARCH_HISTORY[1] = {
            "id": 1,
            "user_id": user_id,
            "query": "test1",
            "filters": None,
            "created_at": datetime.utcnow(),
        }
        FAKE_SEARCH_HISTORY[2] = {
            "id": 2,
            "user_id": user_id,
            "query": "test2",
            "filters": None,
            "created_at": datetime.utcnow(),
        }

        # 清空
        response = client.delete("/api/search/history", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "已清空" in data["message"]
        assert data["success"] is True

    def test_clear_history_no_auth(self, client: TestClient):
        """无认证清空应失败"""
        response = client.delete("/api/search/history")
        assert response.status_code == 401


class TestFavoritesAPI(TestSearchHistoryAPI):
    """收藏API测试基类"""


class TestGetFavorites(TestFavoritesAPI):
    """获取收藏列表测试"""

    def test_get_favorites_empty(self, client: TestClient, auth_header):
        """空收藏列表"""
        response = client.get("/api/search/favorites", headers=auth_header)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 0
        assert data["items"] == []

    def test_get_favorites_with_data(self, client: TestClient):
        """有数据的收藏列表"""
        # 注册用户
        user_data = {
            "email": "fav_test@example.com",
            "password": "FavPass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        token = reg_resp.json()["token"]["access_token"]
        user_id = reg_resp.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 添加收藏
        FAKE_FAVORITES[1] = {
            "id": 1,
            "user_id": user_id,
            "case_id": 123,
            "case_name": "People v. Smith",
            "court": "California Court of Appeal",
            "date_filed": datetime.utcnow(),
            "created_at": datetime.utcnow(),
        }

        # 获取收藏
        response = client.get("/api/search/favorites", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["case_name"] == "People v. Smith"

    def test_get_favorites_pagination(self, client: TestClient):
        """收藏分页"""
        # 注册用户
        user_data = {
            "email": "fav_page_test@example.com",
            "password": "FavPagePass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        token = reg_resp.json()["token"]["access_token"]
        user_id = reg_resp.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 添加多个收藏
        for i in range(15):
            FAKE_FAVORITES[i + 200] = {
                "id": i + 200,
                "user_id": user_id,
                "case_id": 1000 + i,
                "case_name": f"Test Case {i}",
                "court": "Test Court",
                "date_filed": datetime.utcnow(),
                "created_at": datetime.utcnow(),
            }

        # 获取第1页
        response = client.get(
            "/api/search/favorites",
            params={"page": 1, "page_size": 10},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10

    def test_get_favorites_no_auth(self, client: TestClient):
        """无认证获取收藏应失败"""
        response = client.get("/api/search/favorites")
        assert response.status_code == 401


class TestAddFavorite(TestFavoritesAPI):
    """添加收藏测试"""

    def test_add_favorite_success(self, client: TestClient, auth_header):
        """添加收藏成功"""
        response = client.post(
            "/api/search/favorites",
            json={
                "case_id": 123,
                "case_name": "People v. Smith",
                "court": "California Court of Appeal",
            },
            headers=auth_header,
        )

        assert response.status_code == 201
        data = response.json()

        assert data["id"] is not None
        assert data["case_id"] == 123
        assert data["message"] == "收藏成功"

    def test_add_favorite_with_all_fields(self, client: TestClient, auth_header):
        """添加收藏包含所有字段"""
        response = client.post(
            "/api/search/favorites",
            json={
                "case_id": 456,
                "case_name": "State v. Johnson",
                "court": "Supreme Court",
                "date_filed": "2023-01-15T00:00:00",
            },
            headers=auth_header,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] == 456

    def test_add_favorite_duplicate(self, client: TestClient, auth_header):
        """重复收藏应失败"""
        # 第一次收藏
        client.post(
            "/api/search/favorites",
            json={
                "case_id": 789,
                "case_name": "Test Case",
            },
            headers=auth_header,
        )

        # 第二次收藏同一案例
        response = client.post(
            "/api/search/favorites",
            json={
                "case_id": 789,
                "case_name": "Test Case",
            },
            headers=auth_header,
        )

        assert response.status_code == 400
        assert "已在收藏夹中" in response.json()["detail"]

    def test_add_favorite_missing_case_id(self, client: TestClient, auth_header):
        """缺少case_id"""
        response = client.post(
            "/api/search/favorites",
            json={
                "case_name": "Test Case",
            },
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_add_favorite_missing_case_name(self, client: TestClient, auth_header):
        """缺少case_name"""
        response = client.post(
            "/api/search/favorites",
            json={
                "case_id": 123,
            },
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_add_favorite_no_auth(self, client: TestClient):
        """无认证添加收藏应失败"""
        response = client.post(
            "/api/search/favorites",
            json={
                "case_id": 123,
                "case_name": "Test Case",
            },
        )
        assert response.status_code == 401


class TestDeleteFavorite(TestFavoritesAPI):
    """删除收藏测试"""

    def test_delete_favorite_success(self, client: TestClient):
        """删除收藏成功"""
        # 注册用户
        user_data = {
            "email": "del_fav_test@example.com",
            "password": "DelFavPass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        token = reg_resp.json()["token"]["access_token"]
        user_id = reg_resp.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 添加收藏
        FAKE_FAVORITES[1] = {
            "id": 1,
            "user_id": user_id,
            "case_id": 123,
            "case_name": "Test Case",
            "created_at": datetime.utcnow(),
        }

        # 删除
        response = client.delete("/api/search/favorites/1", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "删除成功"
        assert data["success"] is True

    def test_delete_favorite_not_found(self, client: TestClient, auth_header):
        """删除不存在的收藏"""
        response = client.delete("/api/search/favorites/99999", headers=auth_header)
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]

    def test_delete_favorite_no_auth(self, client: TestClient):
        """无认证删除应失败"""
        response = client.delete("/api/search/favorites/1")
        assert response.status_code == 401


class TestClearFavorites(TestFavoritesAPI):
    """清空收藏夹测试"""

    def test_clear_favorites_success(self, client: TestClient):
        """清空收藏成功"""
        # 注册用户
        user_data = {
            "email": "clear_fav_test@example.com",
            "password": "ClearFavPass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        token = reg_resp.json()["token"]["access_token"]
        user_id = reg_resp.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 添加收藏
        FAKE_FAVORITES[1] = {
            "id": 1,
            "user_id": user_id,
            "case_id": 123,
            "case_name": "Test Case 1",
            "created_at": datetime.utcnow(),
        }
        FAKE_FAVORITES[2] = {
            "id": 2,
            "user_id": user_id,
            "case_id": 456,
            "case_name": "Test Case 2",
            "created_at": datetime.utcnow(),
        }

        # 清空
        response = client.delete("/api/search/favorites", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "已清空" in data["message"]
        assert data["success"] is True

    def test_clear_favorites_no_auth(self, client: TestClient):
        """无认证清空应失败"""
        response = client.delete("/api/search/favorites")
        assert response.status_code == 401


class TestCheckFavorite(TestFavoritesAPI):
    """检查收藏状态测试"""

    def test_check_favorite_not_favorited(self, client: TestClient, auth_header):
        """案例未收藏"""
        response = client.get(
            "/api/search/favorites/check/999",
            headers=auth_header,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["case_id"] == 999
        assert data["is_favorited"] is False
        assert data["favorite_id"] is None

    def test_check_favorite_is_favorited(self, client: TestClient, auth_header):
        """案例已收藏"""
        # 先添加收藏
        client.post(
            "/api/search/favorites",
            json={
                "case_id": 555,
                "case_name": "Test Case",
            },
            headers=auth_header,
        )

        # 检查
        response = client.get(
            "/api/search/favorites/check/555",
            headers=auth_header,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["case_id"] == 555
        assert data["is_favorited"] is True
        assert data["favorite_id"] is not None

    def test_check_favorite_no_auth(self, client: TestClient):
        """无认证检查应失败"""
        response = client.get("/api/search/favorites/check/123")
        assert response.status_code == 401


class TestUserDataIsolation(TestSearchHistoryAPI):
    """用户数据隔离测试"""

    def test_user_history_isolation(self, client: TestClient):
        """用户搜索历史隔离"""
        # 用户1
        user1_data = {
            "email": "user1_history@example.com",
            "password": "User1Pass123!",
        }
        reg1_resp = client.post("/api/auth/register", json=user1_data)
        token1 = reg1_resp.json()["token"]["access_token"]
        user1_id = reg1_resp.json()["user"]["id"]

        # 用户2
        user2_data = {
            "email": "user2_history@example.com",
            "password": "User2Pass123!",
        }
        reg2_resp = client.post("/api/auth/register", json=user2_data)
        token2 = reg2_resp.json()["token"]["access_token"]
        user2_id = reg2_resp.json()["user"]["id"]

        # 用户1添加历史
        FAKE_SEARCH_HISTORY[1] = {
            "id": 1,
            "user_id": user1_id,
            "query": "User1 Query",
            "filters": None,
            "created_at": datetime.utcnow(),
        }

        # 用户2添加历史
        FAKE_SEARCH_HISTORY[2] = {
            "id": 2,
            "user_id": user2_id,
            "query": "User2 Query",
            "filters": None,
            "created_at": datetime.utcnow(),
        }

        # 用户1获取历史，只能看到自己的
        response1 = client.get(
            "/api/search/history",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert response1.json()["total"] == 1
        assert response1.json()["items"][0]["query"] == "User1 Query"

        # 用户2获取历史，只能看到自己的
        response2 = client.get(
            "/api/search/history",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response2.json()["total"] == 1
        assert response2.json()["items"][0]["query"] == "User2 Query"

    def test_user_favorites_isolation(self, client: TestClient):
        """用户收藏隔离"""
        # 用户1
        user1_data = {
            "email": "user1_fav@example.com",
            "password": "User1Pass123!",
        }
        reg1_resp = client.post("/api/auth/register", json=user1_data)
        token1 = reg1_resp.json()["token"]["access_token"]
        user1_id = reg1_resp.json()["user"]["id"]

        # 用户2
        user2_data = {
            "email": "user2_fav@example.com",
            "password": "User2Pass123!",
        }
        reg2_resp = client.post("/api/auth/register", json=user2_data)
        token2 = reg2_resp.json()["token"]["access_token"]
        user2_id = reg2_resp.json()["user"]["id"]

        # 用户1添加收藏
        FAKE_FAVORITES[1] = {
            "id": 1,
            "user_id": user1_id,
            "case_id": 111,
            "case_name": "User1 Case",
            "created_at": datetime.utcnow(),
        }

        # 用户2添加收藏
        FAKE_FAVORITES[2] = {
            "id": 2,
            "user_id": user2_id,
            "case_id": 222,
            "case_name": "User2 Case",
            "created_at": datetime.utcnow(),
        }

        # 用户1获取收藏
        response1 = client.get(
            "/api/search/favorites",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert response1.json()["total"] == 1
        assert response1.json()["items"][0]["case_name"] == "User1 Case"

        # 用户2获取收藏
        response2 = client.get(
            "/api/search/favorites",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response2.json()["total"] == 1
        assert response2.json()["items"][0]["case_name"] == "User2 Case"
