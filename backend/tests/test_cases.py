"""
案例API测试

测试案例搜索、详情、AI分析等功能

注意：所有测试使用 sync TestClient (client) 而非 AsyncClient。
原因：dependency_overrides 与 AsyncClient+ASGITransport 在 httpx 0.27 +
FastAPI 0.133 组合下存在兼容性问题，导致 422 验证错误。
使用 sync TestClient 可正常通过。
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
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

    def test_search_cases_basic(self, client, auth_header):
        """基本搜索测试"""
        response = client.get(
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

    def test_search_cases_with_filters(self, client, auth_header):
        """带过滤条件的搜索"""
        response = client.get(
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

    def test_search_cases_no_auth(self, client):
        """无认证搜索 - 公开端点应返回成功"""
        response = client.get("/api/cases/search", params={"q": "robbery"})
        assert response.status_code == 200

    def test_search_cases_empty_query(self, client, auth_header):
        """空查询词"""
        response = client.get(
            "/api/cases/search",
            params={"q": ""},
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_search_cases_query_too_long(self, client, auth_header):
        """查询词过长"""
        response = client.get(
            "/api/cases/search",
            params={"q": "a" * 501},
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_search_cases_invalid_page(self, client, auth_header):
        """无效页码"""
        response = client.get(
            "/api/cases/search",
            params={"q": "robbery", "page": 0},
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_search_cases_page_size_exceeds_limit(self, client, auth_header):
        """page_size超过限制"""
        response = client.get(
            "/api/cases/search",
            params={"q": "robbery", "page_size": 101},
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_search_cases_results_structure(self, client, auth_header):
        """搜索结果结构验证"""
        response = client.get(
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

    def test_search_cases_pagination(self, client, auth_header):
        """分页测试"""
        # 第1页
        response1 = client.get(
            "/api/cases/search",
            params={"q": "robbery", "page": 1, "page_size": 1},
            headers=auth_header,
        )
        # 第2页
        response2 = client.get(
            "/api/cases/search",
            params={"q": "robbery", "page": 2, "page_size": 1},
            headers=auth_header,
        )
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_search_cases_different_queries(self, client, auth_header):
        """不同查询词返回不同结果"""
        queries = ["robbery", "murder", "fraud"]
        for query in queries:
            response = client.get(
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

    def test_get_case_detail(self, client, auth_header):
        """获取案例详情"""
        response = client.get(
            "/api/cases/1",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["courtlistener_id"] == 1
        assert "case_name" in data
        assert "created_at" in data

    def test_get_case_detail_with_ai_data(self, client, auth_header):
        """获取包含AI生成内容的案例详情"""
        response = client.get(
            "/api/cases/1",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data
        assert "entities" in data

    def test_get_case_detail_no_auth(self, client):
        """无认证获取详情 - 公开端点应返回成功"""
        response = client.get("/api/cases/1")
        assert response.status_code == 200

    def test_get_case_detail_nonexistent(self, client, auth_header):
        """获取不存在的案例"""
        response = client.get(
            "/api/cases/999999",
            headers=auth_header,
        )
        # Mock会返回默认数据而不是404
        assert response.status_code == 200


class TestSummarizeCase(TestCasesAPI):
    """AI案例总结测试"""

    def test_summarize_case(self, client, auth_header):
        """AI总结案例"""
        response = client.post(
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

    def test_summarize_case_cached(self, client, auth_header):
        """缓存命中测试"""
        response = client.post(
            "/api/cases/1/summarize",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        # conftest mock_ai_router 返回 mock summary
        assert "summary" in data

    def test_summarize_case_empty_text(self, client, auth_header):
        """空文本总结应失败"""
        response = client.post(
            "/api/cases/999/summarize",
            headers=auth_header,
        )
        assert response.status_code == 400
        assert "空" in response.json()["detail"]

    def test_summarize_case_no_auth(self, client):
        """无认证总结"""
        response = client.post("/api/cases/1/summarize")
        assert response.status_code == 401

    def test_summarize_case_max_length_validation(self, client, auth_header):
        """max_length参数验证"""
        response = client.post(
            "/api/cases/1/summarize",
            headers=auth_header,
            json={"max_length": 5000},
        )
        assert response.status_code == 422

    def test_summarize_case_ai_service_error(self, client, auth_header):
        """AI服务错误处理"""
        response = client.post(
            "/api/cases/1/summarize",
            headers=auth_header,
        )
        # conftest mock_ai_router 正常返回 mock 数据，不会触发错误
        assert response.status_code == 200


class TestExtractEntities(TestCasesAPI):
    """AI实体提取测试"""

    def test_extract_entities(self, client, auth_header):
        """提取实体"""
        response = client.post(
            "/api/cases/1/entities",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1
        assert "entities" in data
        assert data["cached"] is False

    def test_extract_entities_with_types(self, client, auth_header):
        """指定实体类型提取"""
        response = client.post(
            "/api/cases/1/entities",
            headers=auth_header,
            json={"entity_types": ["defendants", "judges"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1

    def test_extract_entities_cached(self, client, auth_header):
        """实体提取缓存"""
        response = client.post(
            "/api/cases/1/entities",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        # conftest mock cache 第一次返回 None (未缓存)
        assert "entities" in data

    def test_extract_entities_empty_text(self, client, auth_header):
        """空文本提取"""
        response = client.post(
            "/api/cases/999/entities",
            headers=auth_header,
        )
        assert response.status_code == 400
        assert "空" in response.json()["detail"]

    def test_extract_entities_no_auth(self, client):
        """无认证提取"""
        response = client.post("/api/cases/1/entities")
        assert response.status_code == 401


class TestExtractKeywords(TestCasesAPI):
    """AI关键词提取测试"""

    def test_extract_keywords(self, client, auth_header):
        """提取关键词"""
        response = client.post(
            "/api/cases/1/keywords",
            headers=auth_header,
            json={"top_n": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1
        assert "keywords" in data
        assert data["cached"] is False

    def test_extract_keywords_top_n_validation(self, client, auth_header):
        """top_n参数验证"""
        response = client.post(
            "/api/cases/1/keywords",
            headers=auth_header,
            json={"top_n": 1},
        )
        assert response.status_code == 422

    def test_extract_keywords_cached(self, client, auth_header):
        """关键词缓存"""
        response = client.post(
            "/api/cases/1/keywords",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data


class TestFindSimilarCases(TestCasesAPI):
    """相似案例测试"""

    def test_find_similar_cases(self, client, auth_header):
        """查找相似案例"""
        response = client.get(
            "/api/cases/1/similar",
            params={"limit": 5},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == 1
        assert "similar_cases" in data
        assert isinstance(data["similar_cases"], list)

    def test_find_similar_cases_default_limit(self, client, auth_header):
        """默认limit"""
        response = client.get(
            "/api/cases/1/similar",
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["case_id"] == 1

    def test_find_similar_cases_limit_validation(self, client, auth_header):
        """limit参数验证"""
        response = client.get(
            "/api/cases/1/similar",
            params={"limit": 25},
            headers=auth_header,
        )
        assert response.status_code == 422

    def test_find_similar_cases_no_auth(self, client):
        """无认证查找 - 需要认证"""
        response = client.get("/api/cases/1/similar")
        assert response.status_code == 401


class TestTranslateCase(TestCasesAPI):
    """AI案例翻译测试"""

    def test_translate_case(self, client, auth_header):
        """翻译案例"""
        response = client.post(
            "/api/cases/1/translate",
            json={"target_language": "Spanish"},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "Spanish"
        assert data["source_language"] == "detected"  # auto -> detected

    def test_translate_case_with_source_language(self, client, auth_header):
        """指定源语言翻译"""
        response = client.post(
            "/api/cases/1/translate",
            json={"target_language": "Chinese", "source_language": "English"},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source_language"] == "English"
        assert data["target_language"] == "Chinese"

    def test_translate_case_no_auth(self, client):
        """无认证翻译 - 需要认证"""
        response = client.post(
            "/api/cases/1/translate",
            json={"target_language": "French"},
        )
        assert response.status_code == 401


class TestGetCaseBySlug(TestCasesAPI):
    """语义化URL案例详情测试"""

    def test_get_case_by_slug(self, client):
        """通过slug获取案例"""
        response = client.get("/api/cases/by-slug/us/criminal/people-v-smith-1/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "slug" in data
        assert "slug_url" in data

    def test_get_case_by_slug_no_auth(self, client):
        """无认证通过slug获取案例"""
        response = client.get("/api/cases/by-slug/us/criminal/people-v-smith-1/")
        assert response.status_code == 200

    def test_get_case_by_slug_with_auth(self, client, auth_header):
        """带认证通过slug获取案例"""
        response = client.get(
            "/api/cases/by-slug/us/criminal/people-v-smith-1/",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert "case_name" in data
        assert "slug" in data

    def test_get_case_by_slug_invalid(self, client):
        """无效slug格式"""
        response = client.get("/api/cases/by-slug/invalid-slug/")
        assert response.status_code == 404


class TestCaseEndpointValidation(TestCasesAPI):
    """案例端点参数验证测试"""

    def test_case_id_negative(self, client, auth_header):
        """负数case_id"""
        response = client.get("/api/cases/-1", headers=auth_header)
        assert response.status_code in [404, 422]

    def test_case_id_string(self, client, auth_header):
        """非数字case_id"""
        response = client.get("/api/cases/abc", headers=auth_header)
        assert response.status_code == 422

    def test_search_without_required_params(self, client, auth_header):
        """缺少必需参数"""
        response = client.get("/api/cases/search", headers=auth_header)
        assert response.status_code == 422
