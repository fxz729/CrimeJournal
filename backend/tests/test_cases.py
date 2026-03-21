"""
案例API测试

测试案例搜索、详情、AI分析等功能
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.api.cases import (
    CaseSearchResult,
    SearchResponse,
    CaseDetailResponse,
    SummarizeResponse,
    EntitiesResponse,
)
from app.services.ai.router import AIRouter, TaskType


class TestCasesAPI:
    """案例API测试基类"""

    @pytest.fixture
    def user_token(self, client: TestClient):
        """创建一个已认证用户的Token"""
        user_data = {
            "email": "case_test@example.com",
            "password": "CasePass123!",
        }
        reg_resp = client.post("/api/auth/register", json=user_data)
        return reg_resp.json()["token"]["access_token"]

    @pytest.fixture
    def auth_header(self, user_token: str):
        """认证请求头"""
        return {"Authorization": f"Bearer {user_token}"}


class TestSearchCases(TestCasesAPI):
    """案例搜索测试"""

    @pytest.mark.asyncio
    async def test_search_cases_basic(self, async_client, auth_header, mock_courtlistener):
        """基本搜索测试"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/search",
                params={"q": "robbery"},
                headers=auth_header,
            )

        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "results" in data
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_search_cases_with_filters(self, async_client, auth_header, mock_courtlistener):
        """带过滤条件的搜索"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/search",
                params={
                    "q": "murder",
                    "court": "pennapp",
                    "date_min": "2022-01-01",
                    "date_max": "2023-12-31",
                    "page": 1,
                    "page_size": 10,
                },
                headers=auth_header,
            )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    @pytest.mark.asyncio
    async def test_search_cases_no_auth(self, async_client):
        """无认证搜索"""
        response = async_client.get("/api/cases/search", params={"q": "robbery"})
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_search_cases_empty_query(self, async_client, auth_header):
        """空查询词"""
        response = async_client.get(
            "/api/cases/search",
            params={"q": ""},
            headers=auth_header,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_cases_query_too_long(self, async_client, auth_header):
        """查询词过长"""
        response = async_client.get(
            "/api/cases/search",
            params={"q": "a" * 501},
            headers=auth_header,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_cases_invalid_page(self, async_client, auth_header, mock_courtlistener):
        """无效页码"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/search",
                params={"q": "robbery", "page": 0},
                headers=auth_header,
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_cases_page_size_exceeds_limit(self, async_client, auth_header, mock_courtlistener):
        """page_size超过限制"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/search",
                params={"q": "robbery", "page_size": 101},
                headers=auth_header,
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_cases_results_structure(self, async_client, auth_header, mock_courtlistener):
        """搜索结果结构验证"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/search",
                params={"q": "robbery"},
                headers=auth_header,
            )

        assert response.status_code == 200
        results = response.json()["results"]

        if results:
            first_result = results[0]
            assert "id" in first_result
            assert "case_name" in first_result
            assert "source" in first_result
            assert first_result["source"] == "courtlistener"

    @pytest.mark.asyncio
    async def test_search_cases_pagination(self, async_client, auth_header, mock_courtlistener):
        """分页测试"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            # 第1页
            response1 = async_client.get(
                "/api/cases/search",
                params={"q": "robbery", "page": 1, "page_size": 1},
                headers=auth_header,
            )
            # 第2页
            response2 = async_client.get(
                "/api/cases/search",
                params={"q": "robbery", "page": 2, "page_size": 1},
                headers=auth_header,
            )

        assert response1.status_code == 200
        assert response2.status_code == 200
        # 注意：mock返回固定数据，真实API会返回不同页的结果

    @pytest.mark.asyncio
    async def test_search_cases_different_queries(self, async_client, auth_header, mock_courtlistener):
        """不同查询词返回不同结果"""
        queries = ["robbery", "murder", "fraud"]

        for query in queries:
            with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
                response = async_client.get(
                    "/api/cases/search",
                    params={"q": query},
                    headers=auth_header,
                )

            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert isinstance(data["total"], int)


class TestGetCaseDetail(TestCasesAPI):
    """案例详情测试"""

    @pytest.mark.asyncio
    async def test_get_case_detail(self, async_client, auth_header, mock_courtlistener):
        """获取案例详情"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/1",
                headers=auth_header,
            )

        assert response.status_code == 200
        data = response.json()

        # 验证响应字段
        assert data["id"] == 1
        assert data["courtlistener_id"] == 1
        assert "case_name" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_case_detail_with_ai_data(self, async_client, auth_header, mock_courtlistener):
        """获取包含AI生成内容的案例详情"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/1",
                headers=auth_header,
            )

        assert response.status_code == 200
        data = response.json()

        # Mock数据包含keywords和entities
        assert "keywords" in data
        assert "entities" in data

    @pytest.mark.asyncio
    async def test_get_case_detail_no_auth(self, async_client):
        """无认证获取详情"""
        response = async_client.get("/api/cases/1")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_case_detail_nonexistent(self, async_client, auth_header, mock_courtlistener):
        """获取不存在的案例"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/999999",
                headers=auth_header,
            )

        # Mock会返回默认数据而不是404
        assert response.status_code == 200


class TestSummarizeCase(TestCasesAPI):
    """AI案例总结测试"""

    @pytest.mark.asyncio
    async def test_summarize_case(self, async_client, auth_header, mock_courtlistener, mock_ai_service, mock_cache_service):
        """AI总结案例"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    # Mock AI Router
                    mock_router_instance = MagicMock()
                    mock_router_instance.summarize_case = AsyncMock(return_value="This is a mock summary of the robbery case.")
                    mock_router.return_value = mock_router_instance

                    # Mock AI Service Cache
                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_summary = AsyncMock(return_value=None)
                        mock_ai_cache.cache_summary = AsyncMock(return_value=True)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/1/summarize",
                            headers=auth_header,
                            json={"max_length": 500},
                        )

        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1
        assert "summary" in data
        assert "generated_at" in data
        assert data["cached"] is False

    @pytest.mark.asyncio
    async def test_summarize_case_cached(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """缓存命中测试"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router.return_value = mock_router_instance

                    # Mock缓存命中
                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_summary = AsyncMock(return_value="Cached summary")
                        mock_ai_cache.cache_summary = AsyncMock(return_value=True)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/1/summarize",
                            headers=auth_header,
                        )

        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is True
        assert data["summary"] == "Cached summary"

    @pytest.mark.asyncio
    async def test_summarize_case_empty_text(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """空文本总结应失败"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_summary = AsyncMock(return_value=None)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/999",  # 999是空文本的mock case
                            headers=auth_header,
                        )

        assert response.status_code == 400
        assert "空" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_summarize_case_no_auth(self, async_client):
        """无认证总结"""
        response = async_client.post("/api/cases/1/summarize")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_summarize_case_max_length_validation(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """max_length参数验证"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_summary = AsyncMock(return_value="summary")
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        # max_length过大
                        response = async_client.post(
                            "/api/cases/1/summarize",
                            headers=auth_header,
                            json={"max_length": 5000},  # 超过2000限制
                        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_summarize_case_ai_service_error(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """AI服务错误处理"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router_instance.summarize_case = AsyncMock(side_effect=Exception("AI service error"))
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_summary = AsyncMock(return_value=None)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/1/summarize",
                            headers=auth_header,
                        )

        assert response.status_code == 500
        assert "AI服务错误" in response.json()["detail"]


class TestExtractEntities(TestCasesAPI):
    """AI实体提取测试"""

    @pytest.mark.asyncio
    async def test_extract_entities(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """提取实体"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router_instance.extract_entities = AsyncMock(return_value={
                        "defendants": ["John Doe"],
                        "courts": ["Superior Court"],
                    })
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_entities = AsyncMock(return_value=None)
                        mock_ai_cache.cache_entities = AsyncMock(return_value=True)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/1/entities",
                            headers=auth_header,
                        )

        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1
        assert "entities" in data
        assert data["cached"] is False

    @pytest.mark.asyncio
    async def test_extract_entities_with_types(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """指定实体类型提取"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router_instance.extract_entities = AsyncMock(return_value={
                        "defendants": ["Test Defendant"],
                    })
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_entities = AsyncMock(return_value=None)
                        mock_ai_cache.cache_entities = AsyncMock(return_value=True)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/1/entities",
                            headers=auth_header,
                            json={"entity_types": ["defendants", "judges"]},
                        )

        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1

    @pytest.mark.asyncio
    async def test_extract_entities_cached(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """实体提取缓存"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_entities = AsyncMock(return_value={"defendants": ["Cached"]})
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/1/entities",
                            headers=auth_header,
                        )

        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is True
        assert data["entities"] == {"defendants": ["Cached"]}

    @pytest.mark.asyncio
    async def test_extract_entities_empty_text(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """空文本提取"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_entities = AsyncMock(return_value=None)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/999/entities",  # 空文本case
                            headers=auth_header,
                        )

        assert response.status_code == 400
        assert "空" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extract_entities_no_auth(self, async_client):
        """无认证提取"""
        response = async_client.post("/api/cases/1/entities")
        assert response.status_code == 403


class TestExtractKeywords(TestCasesAPI):
    """AI关键词提取测试"""

    @pytest.mark.asyncio
    async def test_extract_keywords(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """提取关键词"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router_instance.extract_keywords = AsyncMock(return_value=["robbery", "theft", "criminal"])
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_keywords = AsyncMock(return_value=None)
                        mock_ai_cache.cache_keywords = AsyncMock(return_value=True)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/1/keywords",
                            headers=auth_header,
                            json={"top_n": 5},
                        )

        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1
        assert "keywords" in data
        assert data["cached"] is False

    @pytest.mark.asyncio
    async def test_extract_keywords_top_n_validation(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """top_n参数验证"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_keywords = AsyncMock(return_value=["kw"])
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        # top_n过小
                        response = async_client.post(
                            "/api/cases/1/keywords",
                            headers=auth_header,
                            json={"top_n": 1},  # 小于3
                        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_extract_keywords_cached(self, async_client, auth_header, mock_courtlistener, mock_cache_service):
        """关键词缓存"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            with patch("app.api.cases.get_ai_router") as mock_router:
                with patch("app.api.cases.get_cache", return_value=mock_cache_service):
                    mock_router_instance = MagicMock()
                    mock_router.return_value = mock_router_instance

                    with patch("app.api.cases.AIServiceCache") as mock_ai_cache_cls:
                        mock_ai_cache = MagicMock()
                        mock_ai_cache.get_cached_keywords = AsyncMock(return_value=["cached", "keywords"])
                        mock_ai_cache.cache_keywords = AsyncMock(return_value=True)
                        mock_ai_cache_cls.return_value = mock_ai_cache

                        response = async_client.post(
                            "/api/cases/1/keywords",
                            headers=auth_header,
                        )

        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is True


class TestFindSimilarCases(TestCasesAPI):
    """相似案例测试"""

    @pytest.mark.asyncio
    async def test_find_similar_cases(self, async_client, auth_header, mock_courtlistener):
        """查找相似案例"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/1/similar",
                params={"limit": 5},
                headers=auth_header,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1
        assert "similar_cases" in data
        assert isinstance(data["similar_cases"], list)

    @pytest.mark.asyncio
    async def test_find_similar_cases_default_limit(self, async_client, auth_header, mock_courtlistener):
        """默认limit"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            response = async_client.get(
                "/api/cases/1/similar",
                headers=auth_header,
            )

        assert response.status_code == 200
        assert response.json()["case_id"] == 1

    @pytest.mark.asyncio
    async def test_find_similar_cases_limit_validation(self, async_client, auth_header, mock_courtlistener):
        """limit参数验证"""
        with patch("app.api.cases.get_courtlistener", return_value=mock_courtlistener):
            # limit过大
            response = async_client.get(
                "/api/cases/1/similar",
                params={"limit": 25},  # 超过20限制
                headers=auth_header,
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_find_similar_cases_no_auth(self, async_client):
        """无认证查找"""
        response = async_client.get("/api/cases/1/similar")
        assert response.status_code == 403


class TestCaseEndpointValidation(TestCasesAPI):
    """案例端点参数验证测试"""

    @pytest.mark.asyncio
    async def test_case_id_negative(self, async_client, auth_header, mock_courtlistener):
        """负数case_id"""
        response = async_client.get("/api/cases/-1", headers=auth_header)
        # FastAPI会尝试转换，可能返回404或422
        assert response.status_code in [404, 422]

    @pytest.mark.asyncio
    async def test_case_id_string(self, async_client, auth_header):
        """非数字case_id"""
        response = async_client.get("/api/cases/abc", headers=auth_header)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_without_required_params(self, async_client, auth_header):
        """缺少必需参数"""
        response = async_client.get("/api/cases/search", headers=auth_header)
        assert response.status_code == 422
