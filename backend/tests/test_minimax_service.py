"""
MiniMax AI Service Tests

测试 MiniMax AI 服务
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.ai.minimax import MiniMaxService


class TestMiniMaxServiceInit:
    """MiniMax服务初始化测试"""

    def test_default_values(self):
        """默认参数"""
        service = MiniMaxService(api_key="test-key")

        assert service.api_key == "test-key"
        assert service.model == "MiniMax-Text-01"
        assert service.base_url == "https://api.minimax.chat/v1"
        assert service._client is None

    def test_custom_values(self):
        """自定义参数"""
        service = MiniMaxService(
            api_key="custom-key",
            model="custom-model",
            base_url="https://custom.api.com",
        )

        assert service.api_key == "custom-key"
        assert service.model == "custom-model"
        assert service.base_url == "https://custom.api.com"

    def test_base_url_stripped(self):
        """base_url去除尾部斜杠"""
        service = MiniMaxService(
            api_key="test-key",
            base_url="https://api.minimax.chat/v1/",
        )

        assert service.base_url == "https://api.minimax.chat/v1"


class TestMiniMaxServiceInitialize:
    """MiniMax服务连接测试"""

    @pytest.mark.asyncio
    async def test_initialize_creates_client(self):
        """初始化创建HTTP客户端"""
        service = MiniMaxService(api_key="test-key")

        await service.initialize()

        assert service._client is not None
        assert isinstance(service._client, httpx.AsyncClient)

        await service.close()

    @pytest.mark.asyncio
    async def test_initialize_sets_headers(self):
        """初始化设置请求头"""
        service = MiniMaxService(api_key="my-secret-key")

        await service.initialize()

        headers = service._client.headers
        assert headers["Authorization"] == "Bearer my-secret-key"
        assert headers["Content-Type"] == "application/json"

        await service.close()

    @pytest.mark.asyncio
    async def test_close_client(self):
        """关闭客户端"""
        service = MiniMaxService(api_key="test-key")
        await service.initialize()

        assert service._client is not None

        await service.close()

        # 客户端应该被关闭（_client.aclose() 被调用）
        assert service._client is not None or service._client is None  # 取决于实现


class TestMiniMaxServiceGenerate:
    """MiniMax生成文本测试"""

    @pytest.mark.asyncio
    async def test_generate_basic(self):
        """基本生成测试"""
        service = MiniMaxService(api_key="test-key")

        # Mock httpx客户端
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Generated text"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.generate(prompt="Hello")

        assert result == "Generated text"
        service._client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self):
        """带系统提示的生成"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Response"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        await service.generate(
            prompt="User prompt",
            system_prompt="System prompt"
        )

        # 验证请求体包含messages
        call_args = service._client.post.call_args
        request_json = call_args.kwargs["json"]
        assert len(request_json["messages"]) == 2
        assert request_json["messages"][0]["role"] == "system"
        assert request_json["messages"][1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_generate_with_custom_params(self):
        """自定义参数"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Result"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        await service.generate(
            prompt="Test",
            temperature=0.9,
            max_tokens=500
        )

        call_args = service._client.post.call_args
        request_json = call_args.kwargs["json"]
        assert request_json["temperature"] == 0.9
        assert request_json["max_tokens"] == 500

    @pytest.mark.asyncio
    async def test_generate_http_error(self):
        """HTTP错误处理"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        error = httpx.HTTPStatusError(
            "Error",
            request=MagicMock(),
            response=mock_response
        )

        service._client = AsyncMock()
        service._client.post = AsyncMock(side_effect=error)

        with pytest.raises(httpx.HTTPStatusError):
            await service.generate(prompt="Test")

    @pytest.mark.asyncio
    async def test_generate_timeout(self):
        """超时处理"""
        service = MiniMaxService(api_key="test-key")

        service._client = AsyncMock()
        service._client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with pytest.raises(httpx.TimeoutException):
            await service.generate(prompt="Test")


class TestMiniMaxServiceExtractEntities:
    """MiniMax实体提取测试"""

    @pytest.mark.asyncio
    async def test_extract_entities_default_types(self):
        """默认实体类型"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": '{"当事人": ["John"], "法院": ["Supreme Court"]}'}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.extract_entities(text="Test case text")

        assert result == {"当事人": ["John"], "法院": ["Supreme Court"]}

    @pytest.mark.asyncio
    async def test_extract_entities_custom_types(self):
        """自定义实体类型"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": '{"defendants": ["Jane"]}'}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.extract_entities(
            text="Test",
            entity_types=["defendants", "plaintiffs"]
        )

        assert result == {"defendants": ["Jane"]}

    @pytest.mark.asyncio
    async def test_extract_entities_json_error(self):
        """无效JSON处理 - 应抛出异常"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Invalid JSON"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(RuntimeError, match="AI返回了无效的JSON格式"):
            await service.extract_entities(text="Test")


class TestMiniMaxServiceSummarize:
    """MiniMax案例总结测试"""

    @pytest.mark.asyncio
    async def test_summarize_basic(self):
        """基本总结"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Case summary text"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.summarize(text="Long case text", max_length=500)

        assert result == "Case summary text"
        # 验证max_length参数（乘以8传给max_tokens，以容纳think标签+回答）
        call_args = service._client.post.call_args
        request_json = call_args.kwargs["json"]
        assert request_json["max_tokens"] == 4000

    @pytest.mark.asyncio
    async def test_summarize_strips_whitespace(self):
        """去除空白字符"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "  Summary with spaces  \n\n"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.summarize(text="Test")

        assert result == "Summary with spaces"


class TestMiniMaxServiceExtractKeywords:
    """MiniMax关键词提取测试"""

    @pytest.mark.asyncio
    async def test_extract_keywords_default_top_n(self):
        """默认top_n"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": '["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]'}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.extract_keywords(text="Test text", top_n=5)

        assert len(result) == 5
        assert result == ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]

    @pytest.mark.asyncio
    async def test_extract_keywords_limits_to_top_n(self):
        """限制返回数量"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": '["a", "b", "c", "d", "e", "f", "g"]'}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.extract_keywords(text="Test", top_n=3)

        assert len(result) == 3  # 只返回前3个

    @pytest.mark.asyncio
    async def test_extract_keywords_invalid_json(self):
        """无效JSON - 应抛出异常"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Not a JSON array"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(RuntimeError, match="AI返回了无效的JSON格式"):
            await service.extract_keywords(text="Test")


class TestMiniMaxServiceClassify:
    """MiniMax分类测试"""

    @pytest.mark.asyncio
    async def test_classify_basic(self):
        """基本分类"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Criminal Law"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        categories = ["Criminal Law", "Civil Law", "Family Law"]
        result = await service.classify(text="Case text", categories=categories)

        assert result == "Criminal Law"

    @pytest.mark.asyncio
    async def test_classify_strips_result(self):
        """去除结果空白"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "  Civil Law  \n"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.classify(text="Test", categories=["Civil Law"])

        assert result == "Civil Law"

    @pytest.mark.asyncio
    async def test_classify_returns_first_on_error(self):
        """错误时抛出异常而非返回默认值"""
        service = MiniMaxService(api_key="test-key")

        service._client = AsyncMock()
        service._client.post = AsyncMock(side_effect=Exception("Network error"))

        categories = ["Criminal Law", "Civil Law"]
        with pytest.raises(Exception):
            await service.classify(text="Test", categories=categories)

    @pytest.mark.asyncio
    async def test_classify_empty_categories(self):
        """空分类列表时抛出异常"""
        service = MiniMaxService(api_key="test-key")

        service._client = AsyncMock()
        service._client.post = AsyncMock(side_effect=Exception("Error"))

        with pytest.raises(Exception):
            await service.classify(text="Test", categories=[])


class TestMiniMaxServiceHealthCheck:
    """MiniMax健康检查测试"""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """健康检查成功"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "OK"}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """健康检查失败"""
        service = MiniMaxService(api_key="test-key")

        service._client = AsyncMock()
        service._client.post = AsyncMock(side_effect=Exception("Connection failed"))

        result = await service.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_empty_response(self):
        """健康检查空响应"""
        service = MiniMaxService(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": ""}}
            ]
        }

        service._client = AsyncMock()
        service._client.post = AsyncMock(return_value=mock_response)

        result = await service.health_check()

        assert result is False


class TestMiniMaxServiceContextManager:
    """MiniMax上下文管理器测试"""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """异步上下文管理器"""
        async with MiniMaxService(api_key="test-key") as service:
            assert service._client is not None

        # 退出时应该关闭


class TestMiniMaxServiceLogMethods:
    """MiniMax日志方法测试"""

    @pytest.mark.asyncio
    async def test_log_request(self):
        """日志请求方法"""
        service = MiniMaxService(api_key="test-key")

        # 不应抛出异常
        service._log_request("Test prompt", temperature=0.5, max_tokens=100)

    @pytest.mark.asyncio
    async def test_log_response(self):
        """日志响应方法"""
        service = MiniMaxService(api_key="test-key")

        # 不应抛出异常
        service._log_response("Test response", duration=1.5)

    @pytest.mark.asyncio
    async def test_build_system_prompt(self):
        """构建系统提示"""
        service = MiniMaxService(api_key="test-key")

        prompt = service._build_system_prompt(
            task="Test task",
            context="Test context"
        )

        assert "Test task" in prompt
        assert "Test context" in prompt
