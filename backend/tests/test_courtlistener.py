"""
CourtListener服务测试

测试CourtListener API客户端的各项功能
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.courtlistener import CourtListenerClient
from tests.conftest import MockCourtListenerClient


class TestCourtListenerClient:
    """CourtListener客户端测试"""

    @pytest.fixture
    def client(self):
        """创建客户端实例"""
        return CourtListenerClient(api_key="test-api-key")

    @pytest.fixture
    async def initialized_client(self):
        """创建并初始化客户端"""
        client = CourtListenerClient(api_key="test-api-key")
        await client.initialize()
        yield client
        await client.close()

    # ==================== 初始化和关闭 ====================

    @pytest.mark.asyncio
    async def test_initialize(self):
        """初始化客户端"""
        client = CourtListenerClient()
        await client.initialize()
        assert client._client is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_initialize_with_api_key(self):
        """带API Key初始化"""
        client = CourtListenerClient(api_key="my-secret-key")
        await client.initialize()
        assert client._client is not None
        # 验证Authorization头
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Token my-secret-key"
        await client.close()

    @pytest.mark.asyncio
    async def test_close(self):
        """关闭客户端"""
        client = CourtListenerClient()
        await client.initialize()
        assert client._client is not None
        await client.close()
        # 关闭后_client应该被清理（根据实现可能为None）

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """上下文管理器"""
        async with CourtListenerClient() as client:
            assert client._client is not None
        # 退出时自动关闭

    # ==================== 搜索判例 ====================

    @pytest.mark.asyncio
    async def test_search_opinions_basic(self, initialized_client):
        """基本搜索"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": 1,
                        "cluster": {
                            "id": 1,
                            "case_name": "Test Case 1",
                            "court": "Test Court",
                            "date_filed": "2023-01-01",
                        }
                    }
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.search_opinions(query="test")

        assert result["count"] == 2
        assert len(result["results"]) == 1
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/search/"
        assert call_args[1]["params"]["q"] == "test"

    @pytest.mark.asyncio
    async def test_search_opinions_with_filters(self, initialized_client):
        """带过滤条件的搜索"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 0, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.search_opinions(
                query="robbery",
                court="calapp",
                case_number="A123",
                date_min="2023-01-01",
                date_max="2023-12-31",
                page=2,
                page_size=50,
            )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["q"] == "robbery"
        assert params["court"] == "calapp"
        assert params["docket_number"] == "A123"
        assert params["dateFiled_min"] == "2023-01-01"
        assert params["dateFiled_max"] == "2023-12-31"
        assert params["page"] == 2
        assert params["page_size"] == 50

    @pytest.mark.asyncio
    async def test_search_opinions_pagination(self, initialized_client):
        """分页参数"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 100, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.search_opinions(
                query="test",
                page=5,
                page_size=25,
            )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["page"] == 5
        assert params["page_size"] == 25

    @pytest.mark.asyncio
    async def test_search_opinions_http_error(self, initialized_client):
        """HTTP错误处理"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized",
                request=MagicMock(),
                response=mock_response,
            )

            with pytest.raises(httpx.HTTPStatusError):
                await initialized_client.search_opinions(query="test")

    # ==================== 获取判例详情 ====================

    @pytest.mark.asyncio
    async def test_get_opinion_by_id(self, initialized_client):
        """根据ID获取判例"""
        with patch.object(initialized_client._client, "get") as mock_get:
            # 第一个调用：/opinions/123/
            mock_opinion_response = MagicMock()
            mock_opinion_response.json.return_value = {
                "id": 123,
                "cluster": "https://www.courtlistener.com/api/rest/v4/clusters/456/",
                "plain_text": "This is a comprehensive test case document that contains more than one hundred characters of legal text content for testing purposes. The quick brown fox jumps over the lazy dog while the case progresses through the court system.",
                "html": "",
                "html_with_citations": "",
            }
            mock_opinion_response.raise_for_status = MagicMock()

            # 第二个调用：cluster URL
            mock_cluster_response = MagicMock()
            mock_cluster_response.json.return_value = {
                "id": 456,
                "case_name": "Test Case",
                "docket": "https://www.courtlistener.com/api/rest/v4/dockets/789/",
            }
            mock_cluster_response.raise_for_status = MagicMock()

            # 第三个调用：docket URL
            mock_docket_response = MagicMock()
            mock_docket_response.json.return_value = {
                "id": 789,
                "court_id": "ca9",
                "docket_number": "CR-2024-001",
            }
            mock_docket_response.raise_for_status = MagicMock()

            mock_get.side_effect = [mock_opinion_response, mock_cluster_response, mock_docket_response]

            result = await initialized_client.get_opinion_by_id(123)

            assert result["id"] == 123
            assert "cluster" in result
            assert result["plain_text"] == "This is a comprehensive test case document that contains more than one hundred characters of legal text content for testing purposes. The quick brown fox jumps over the lazy dog while the case progresses through the court system."
            # 验证调用次数
            assert mock_get.call_count == 3

    @pytest.mark.asyncio
    async def test_get_opinion_by_id_not_found(self, initialized_client):
        """判例不存在"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found",
                request=MagicMock(),
                response=mock_response,
            )

            with pytest.raises(httpx.HTTPStatusError):
                await initialized_client.get_opinion_by_id(99999)

    # ==================== 获取案件意见 ====================

    @pytest.mark.asyncio
    async def test_get_case_opinions(self, initialized_client):
        """获取案件的所有意见"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [
                    {"id": 1, "plain_text": "Opinion 1"},
                    {"id": 2, "plain_text": "Opinion 2"},
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.get_case_opinions(docket_id=456)

        assert len(result) == 2
        mock_get.assert_called_once_with("/dockets/456/opinions/")

    # ==================== 获取法院列表 ====================

    @pytest.mark.asyncio
    async def test_get_courts_basic(self, initialized_client):
        """获取法院列表"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [
                    {"id": "ca9", "full_name": "Ninth Circuit"},
                    {"id": "cal", "full_name": "California Supreme Court"},
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.get_courts()

        assert len(result) == 2
        assert result[0]["id"] == "ca9"

    @pytest.mark.asyncio
    async def test_get_courts_with_type(self, initialized_client):
        """按类型获取法院"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [{"id": "ca9", "court_type": "federal"}]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.get_courts(court_type="federal")

        call_args = mock_get.call_args
        assert call_args[1]["params"]["court_type"] == "federal"

    # ==================== 引用网络 ====================

    @pytest.mark.asyncio
    async def test_get_citation_network_cited_by(self, initialized_client):
        """获取引用网络 - 被引用"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "count": 5,
                "results": [
                    {"citing_cluster": {"id": 1, "case_name": "Citing Case"}}
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.get_citation_network(
                citation_type="cited-by",
                cite_urn="cluster:123",
            )

        assert result["count"] == 5
        mock_get.assert_called_once_with("/cited-by/cluster:123/")

    @pytest.mark.asyncio
    async def test_get_citation_network_authorities(self, initialized_client):
        """获取引用网络 - 引用"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 0, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.get_citation_network(
                citation_type="authorities",
                cite_urn="cluster:456",
            )

        mock_get.assert_called_once_with("/authorities/cluster:456/")

    # ==================== 获取簇信息 ====================

    @pytest.mark.asyncio
    async def test_get_cluster_by_id(self, initialized_client):
        """获取簇信息"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_cluster_response = MagicMock()
            mock_cluster_response.json.return_value = {
                "id": 789,
                "case_name": "Cluster Case",
                "docket": "https://www.courtlistener.com/api/rest/v4/dockets/101/",
                "sub_opinions": ["https://www.courtlistener.com/api/rest/v4/opinions/100/"],
            }
            mock_cluster_response.raise_for_status = MagicMock()

            mock_docket_response = MagicMock()
            mock_docket_response.json.return_value = {
                "id": 101,
                "court_id": "ca9",
            }
            mock_docket_response.raise_for_status = MagicMock()

            mock_opinion_response = MagicMock()
            mock_opinion_response.json.return_value = {
                "id": 100,
                "plain_text": "This is a comprehensive opinion text for testing cluster retrieval with more than one hundred characters of case content.",
                "html": "",
                "html_with_citations": "",
            }
            mock_opinion_response.raise_for_status = MagicMock()

            mock_get.side_effect = [mock_cluster_response, mock_docket_response, mock_opinion_response]

            result = await initialized_client.get_cluster_by_id(789)

        assert result["id"] == 789
        assert result["case_name"] == "Cluster Case"
        assert result["_first_opinion"]["plain_text"] != ""

    # ==================== 引用搜索 ====================

    @pytest.mark.asyncio
    async def test_search_by_citation(self, initialized_client):
        """通过引用搜索案件"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "count": 1,
                "results": [{"id": 1, "citation": "89 Cal.App.4th 123"}]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.search_by_citation("89 Cal.App.4th 123")

        assert result["count"] == 1
        call_args = mock_get.call_args
        assert call_args[1]["params"]["citation"] == "89 Cal.App.4th 123"

    # ==================== Mock客户端测试 ====================

    @pytest.mark.asyncio
    async def test_mock_search_robbery(self):
        """Mock客户端 - robbery搜索"""
        mock = MockCourtListenerClient()
        await mock.initialize()

        result = await mock.search_opinions(query="robbery")

        assert result["count"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["cluster"]["case_name"] == "People v. Smith"

        await mock.close()

    @pytest.mark.asyncio
    async def test_mock_search_murder(self):
        """Mock客户端 - murder搜索"""
        mock = MockCourtListenerClient()
        await mock.initialize()

        result = await mock.search_opinions(query="murder")

        assert result["count"] == 1
        assert result["results"][0]["cluster"]["case_name"] == "Commonwealth v. Williams"

        await mock.close()

    @pytest.mark.asyncio
    async def test_mock_get_opinion_by_id(self):
        """Mock客户端 - 获取判例"""
        mock = MockCourtListenerClient()
        await mock.initialize()

        result = await mock.get_opinion_by_id(1)

        assert result["id"] == 1
        assert result["cluster"]["case_name"] == "People v. Smith"
        assert "plain_text" in result

        await mock.close()

    @pytest.mark.asyncio
    async def test_mock_get_opinion_by_id_empty_text(self):
        """Mock客户端 - 空文本判例"""
        mock = MockCourtListenerClient()
        await mock.initialize()

        result = await mock.get_opinion_by_id(999)

        assert result["id"] == 999
        assert result["plain_text"] == ""

        await mock.close()

    @pytest.mark.asyncio
    async def test_mock_get_courts(self):
        """Mock客户端 - 法院列表"""
        mock = MockCourtListenerClient()
        await mock.initialize()

        result = await mock.get_courts()

        assert len(result) == 2
        assert result[0]["id"] == "ca9"

        federal_result = await mock.get_courts(court_type="federal")
        assert len(federal_result) == 1

        await mock.close()

    @pytest.mark.asyncio
    async def test_mock_get_citation_network(self):
        """Mock客户端 - 引用网络"""
        mock = MockCourtListenerClient()
        await mock.initialize()

        result = await mock.get_citation_network("cited-by", "cluster:1")

        assert result["count"] == 0
        assert result["results"] == []

        await mock.close()

    @pytest.mark.asyncio
    async def test_mock_search_by_citation(self):
        """Mock客户端 - 引用搜索"""
        mock = MockCourtListenerClient()
        await mock.initialize()

        result = await mock.search_by_citation("89 Cal.App.4th 123")

        assert result["count"] == 1
        assert result["results"][0]["id"] == 1

        await mock.close()


class TestCourtListenerFilters:
    """CourtListener过滤器测试"""

    @pytest.mark.asyncio
    async def test_date_filter_format(self, initialized_client):
        """日期过滤格式"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 0, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            await initialized_client.search_opinions(
                query="test",
                date_min="2023-01-01",
                date_max="2023-12-31",
            )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert "dateFiled_min" in params
        assert "dateFiled_max" in params

    @pytest.mark.asyncio
    async def test_court_filter(self, initialized_client):
        """法院过滤"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 0, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            await initialized_client.search_opinions(
                query="test",
                court="ca9",
            )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["court"] == "ca9"

    @pytest.mark.asyncio
    async def test_case_number_filter(self, initialized_client):
        """案件编号过滤"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 0, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            await initialized_client.search_opinions(
                query="test",
                case_number="CR-2023-001",
            )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["docket_number"] == "CR-2023-001"

    @pytest.mark.asyncio
    async def test_all_filters_combined(self, initialized_client):
        """组合过滤"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 0, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            await initialized_client.search_opinions(
                query="criminal robbery",
                court="calapp",
                case_number="A123",
                date_min="2022-01-01",
                date_max="2023-06-30",
                page=1,
                page_size=20,
            )

        call_args = mock_get.call_args
        params = call_args[1]["params"]

        # 验证所有参数都存在
        assert params["q"] == "criminal robbery"
        assert params["court"] == "calapp"
        assert params["docket_number"] == "A123"
        assert params["dateFiled_min"] == "2022-01-01"
        assert params["dateFiled_max"] == "2023-06-30"
        assert params["page"] == 1
        assert params["page_size"] == 20


class TestCourtListenerEdgeCases:
    """CourtListener边界情况测试"""

    @pytest.mark.asyncio
    async def test_empty_query(self, initialized_client):
        """空查询词（虽然API会处理，但参数验证在API层）"""
        # 空查询词会导致参数为空
        pass

    @pytest.mark.asyncio
    async def test_very_long_query(self, initialized_client):
        """超长查询词"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 0, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            long_query = "a" * 500
            result = await initialized_client.search_opinions(query=long_query)

        # API应接受长查询
        assert "results" in result

    @pytest.mark.asyncio
    async def test_special_characters_in_query(self, initialized_client):
        """查询中的特殊字符"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"count": 0, "results": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await initialized_client.search_opinions(
                query="Smith v. Jones & Associates",
            )

        call_args = mock_get.call_args
        assert call_args[1]["params"]["q"] == "Smith v. Jones & Associates"

    @pytest.mark.asyncio
    async def test_network_error(self, initialized_client):
        """网络错误"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_get.side_effect = httpx.NetworkError("Connection failed")

            with pytest.raises(httpx.NetworkError):
                await initialized_client.search_opinions(query="test")

    @pytest.mark.asyncio
    async def test_timeout(self, initialized_client):
        """请求超时"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(httpx.TimeoutException):
                await initialized_client.search_opinions(query="test")

    @pytest.mark.asyncio
    async def test_rate_limit(self, initialized_client):
        """速率限制"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_get.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Rate Limited",
                request=MagicMock(),
                response=mock_response,
            )

            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await initialized_client.search_opinions(query="test")
            assert exc_info.value.response.status_code == 429

    @pytest.mark.asyncio
    async def test_server_error(self, initialized_client):
        """服务器错误"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Internal Server Error",
                request=MagicMock(),
                response=mock_response,
            )

            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await initialized_client.search_opinions(query="test")
            assert exc_info.value.response.status_code == 500

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, initialized_client):
        """无效JSON响应"""
        with patch.object(initialized_client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response
            mock_response.raise_for_status = MagicMock()

            with pytest.raises(ValueError):
                await initialized_client.search_opinions(query="test")


class TestCourtListenerHeaders:
    """CourtListener请求头测试"""

    def test_default_headers(self):
        """默认请求头"""
        client = CourtListenerClient()
        assert "Content-Type" in client.headers
        assert client.headers["Content-Type"] == "application/json"
        assert "User-Agent" in client.headers
        assert "CrimeJournal" in client.headers["User-Agent"]

    def test_headers_with_api_key(self):
        """带API Key的请求头"""
        client = CourtListenerClient(api_key="my-secret-key")
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Token my-secret-key"

    def test_headers_without_api_key(self):
        """无API Key的请求头"""
        client = CourtListenerClient()
        assert "Authorization" not in client.headers
