"""
Cache Service Tests

测试 Redis 缓存服务
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.services.cache import CacheService, AIServiceCache


class TestCacheServiceInit:
    """缓存服务初始化测试"""

    def test_default_values(self):
        """默认参数"""
        cache = CacheService()

        assert cache.host == "localhost"
        assert cache.port == 6379
        assert cache.db == 0
        assert cache.password is None
        assert cache.key_prefix == "crimejournal:"
        assert cache._client is None

    def test_custom_values(self):
        """自定义参数"""
        cache = CacheService(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            key_prefix="custom:",
        )

        assert cache.host == "redis.example.com"
        assert cache.port == 6380
        assert cache.db == 1
        assert cache.password == "secret"
        assert cache.key_prefix == "custom:"

    def test_default_ttl_values(self):
        """默认TTL值"""
        assert CacheService.DEFAULT_TTL == 3600
        assert CacheService.SHORT_TTL == 300
        assert CacheService.LONG_TTL == 86400


class TestCacheServiceInitialize:
    """缓存服务连接测试"""

    @pytest.mark.asyncio
    async def test_initialize_creates_client(self):
        """初始化创建Redis客户端"""
        cache = CacheService()

        with patch("redis.asyncio.Redis") as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client

            await cache.initialize()

            mock_redis.assert_called_once()
            mock_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_ping_failure(self):
        """Redis连接失败时优雅降级到内存模式"""
        cache = CacheService()

        with patch("redis.asyncio.Redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.side_effect = Exception("Connection refused")
            mock_redis.return_value = mock_client

            # 不应抛出异常，而是优雅降级
            await cache.initialize()

            # 验证缓存服务处于不可用状态（降级模式）
            assert cache._available is False
            assert cache._client is None


class TestCacheServiceClose:
    """缓存服务关闭测试"""

    @pytest.mark.asyncio
    async def test_close_with_client(self):
        """关闭有客户端的服务"""
        cache = CacheService()
        cache._client = AsyncMock()

        await cache.close()

        cache._client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_client(self):
        """关闭无客户端的服务"""
        cache = CacheService()

        # 不应抛出异常
        await cache.close()


class TestCacheServiceBuildKey:
    """缓存键构建测试"""

    def test_build_key_with_prefix(self):
        """带前缀构建键"""
        cache = CacheService(key_prefix="test:")
        key = cache._build_key("mykey")
        assert key == "test:mykey"

    def test_build_key_default_prefix(self):
        """默认前缀"""
        cache = CacheService()
        key = cache._build_key("mykey")
        assert key == "crimejournal:mykey"


class TestCacheServiceGet:
    """缓存获取测试"""

    @pytest.mark.asyncio
    async def test_get_exists(self):
        """获取存在的键"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.get = AsyncMock(return_value='{"data": "value"}')

        result = await cache.get("test_key")

        assert result == {"data": "value"}
        cache._client.get.assert_called_once_with("crimejournal:test_key")

    @pytest.mark.asyncio
    async def test_get_not_exists(self):
        """获取不存在的键"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.get = AsyncMock(return_value=None)

        result = await cache.get("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_non_json_value(self):
        """获取非JSON值"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.get = AsyncMock(return_value="plain text")

        result = await cache.get("test")

        assert result == "plain text"

    @pytest.mark.asyncio
    async def test_get_error(self):
        """获取错误"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.get = AsyncMock(side_effect=Exception("Redis error"))

        result = await cache.get("test")

        assert result is None


class TestCacheServiceSet:
    """缓存设置测试"""

    @pytest.mark.asyncio
    async def test_set_dict(self):
        """设置字典"""
        cache = CacheService()
        cache._client = AsyncMock()

        result = await cache.set("key", {"data": "value"}, ttl=100)

        assert result is True
        cache._client.setex.assert_called_once()
        call_args = cache._client.setex.call_args
        assert call_args[0][0] == "crimejournal:key"
        assert call_args[0][1] == 100

    @pytest.mark.asyncio
    async def test_set_list(self):
        """设置列表"""
        cache = CacheService()
        cache._client = AsyncMock()

        await cache.set("key", ["a", "b", "c"])

        call_args = cache._client.setex.call_args
        assert json.loads(call_args[0][2]) == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_set_string(self):
        """设置字符串"""
        cache = CacheService()
        cache._client = AsyncMock()

        await cache.set("key", "plain string")

        call_args = cache._client.setex.call_args
        assert call_args[0][2] == "plain string"

    @pytest.mark.asyncio
    async def test_set_default_ttl(self):
        """默认TTL"""
        cache = CacheService()
        cache._client = AsyncMock()

        await cache.set("key", "value")

        call_args = cache._client.setex.call_args
        assert call_args[0][1] == CacheService.DEFAULT_TTL

    @pytest.mark.asyncio
    async def test_set_error(self):
        """设置错误"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.setex = AsyncMock(side_effect=Exception("Redis error"))

        result = await cache.set("key", "value")

        assert result is False


class TestCacheServiceDelete:
    """缓存删除测试"""

    @pytest.mark.asyncio
    async def test_delete_exists(self):
        """删除存在的键"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.delete = AsyncMock(return_value=1)

        result = await cache.delete("test_key")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_exists(self):
        """删除不存在的键"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.delete = AsyncMock(return_value=0)

        result = await cache.delete("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_error(self):
        """删除错误"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.delete = AsyncMock(side_effect=Exception("Error"))

        result = await cache.delete("test")

        assert result is False


class TestCacheServiceExists:
    """缓存存在检查测试"""

    @pytest.mark.asyncio
    async def test_exists_true(self):
        """键存在"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.exists = AsyncMock(return_value=1)

        result = await cache.exists("test_key")

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        """键不存在"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.exists = AsyncMock(return_value=0)

        result = await cache.exists("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_error(self):
        """检查错误"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.exists = AsyncMock(side_effect=Exception("Error"))

        result = await cache.exists("test")

        assert result is False


class TestCacheServiceGetOrSet:
    """缓存获取或设置测试"""

    @pytest.mark.asyncio
    async def test_get_or_set_cache_hit(self):
        """缓存命中"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.get = AsyncMock(return_value='{"cached": true}')

        fetch_func = AsyncMock()
        result = await cache.get_or_set("key", fetch_func)

        assert result == {"cached": True}  # JSON deserializes to Python True
        fetch_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_set_cache_miss(self):
        """缓存未命中"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.get = AsyncMock(return_value=None)
        cache._client.setex = AsyncMock()

        fetch_func = AsyncMock(return_value="fetched data")

        result = await cache.get_or_set("key", fetch_func)

        assert result == "fetched data"
        fetch_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_or_set_fetch_returns_none(self):
        """获取函数返回None"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.get = AsyncMock(return_value=None)

        fetch_func = AsyncMock(return_value=None)

        result = await cache.get_or_set("key", fetch_func)

        assert result is None
        cache._client.setex.assert_not_called()


class TestCacheServiceClearPattern:
    """缓存模式清除测试"""

    @pytest.mark.asyncio
    async def test_clear_pattern(self):
        """清除匹配模式"""
        cache = CacheService()
        cache._client = AsyncMock()

        # Mock scan_iter
        async def mock_scan_iter(match):
            keys = ["crimejournal:user:1", "crimejournal:user:2"]
            for key in keys:
                if match in key or match.replace("*", "") in key:
                    yield key

        cache._client.scan_iter = mock_scan_iter
        cache._client.delete = AsyncMock(return_value=2)

        result = await cache.clear_pattern("user:*")

        assert result == 2

    @pytest.mark.asyncio
    async def test_clear_pattern_no_matches(self):
        """无匹配"""
        cache = CacheService()
        cache._client = AsyncMock()

        async def mock_scan_iter(match):
            return
            yield  # Empty generator

        cache._client.scan_iter = mock_scan_iter

        result = await cache.clear_pattern("nonexistent:*")

        assert result == 0

    @pytest.mark.asyncio
    async def test_clear_pattern_error(self):
        """模式清除异常"""
        cache = CacheService()
        cache._client = AsyncMock()

        # Must be an async generator (yield + raise) to match real scan_iter behavior
        async def mock_scan_iter_error(match):
            yield  # Must yield at least once before raising
            raise Exception("Redis scan error")

        cache._client.scan_iter = mock_scan_iter_error

        result = await cache.clear_pattern("user:*")

        assert result == 0


class TestCacheServiceIncr:
    """缓存递增测试"""

    @pytest.mark.asyncio
    async def test_incr(self):
        """递增"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.incrby = AsyncMock(return_value=5)

        result = await cache.incr("counter")

        assert result == 5

    @pytest.mark.asyncio
    async def test_incr_with_amount(self):
        """带增量递增"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.incrby = AsyncMock(return_value=10)

        result = await cache.incr("counter", amount=5)

        assert result == 10
        cache._client.incrby.assert_called_with("crimejournal:counter", 5)

    @pytest.mark.asyncio
    async def test_incr_error(self):
        """递增错误"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.incrby = AsyncMock(side_effect=Exception("Error"))

        result = await cache.incr("counter")

        assert result == 0


class TestCacheServiceTTL:
    """缓存TTL测试"""

    @pytest.mark.asyncio
    async def test_get_ttl(self):
        """获取TTL"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.ttl = AsyncMock(return_value=3600)

        result = await cache.get_ttl("key")

        assert result == 3600

    @pytest.mark.asyncio
    async def test_get_ttl_error(self):
        """获取TTL错误"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.ttl = AsyncMock(side_effect=Exception("Error"))

        result = await cache.get_ttl("key")

        assert result == -1

    @pytest.mark.asyncio
    async def test_expire(self):
        """设置过期时间"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.expire = AsyncMock(return_value=True)

        result = await cache.expire("key", 3600)

        assert result is True

    @pytest.mark.asyncio
    async def test_expire_error(self):
        """设置过期时间错误"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.expire = AsyncMock(side_effect=Exception("Error"))

        result = await cache.expire("key", 3600)

        assert result is False


class TestCacheServiceHealthCheck:
    """缓存健康检查测试"""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """健康检查成功"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.ping = AsyncMock(return_value=True)

        result = await cache.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """健康检查失败"""
        cache = CacheService()
        cache._client = AsyncMock()
        cache._client.ping.side_effect = Exception("Connection failed")

        result = await cache.health_check()

        assert result is False


class TestCacheServiceContextManager:
    """缓存上下文管理器测试"""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """异步上下文管理器"""
        cache = CacheService()

        with patch("redis.asyncio.Redis") as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client

            async with cache:
                mock_redis.assert_called_once()

            mock_client.close.assert_called_once()


class TestAIServiceCache:
    """AI服务缓存辅助类测试"""

    @pytest.fixture
    def mock_cache_service(self):
        """Mock缓存服务"""
        cache = MagicMock(spec=CacheService)
        cache._build_key = lambda k: f"crimejournal:{k}"
        return cache

    def test_init(self):
        """初始化"""
        mock_cache = MagicMock()
        ai_cache = AIServiceCache(mock_cache)

        assert ai_cache.cache is mock_cache

    def test_hash_prompt(self):
        """哈希提示"""
        mock_cache = MagicMock()
        ai_cache = AIServiceCache(mock_cache)

        hash1 = ai_cache._hash_prompt("test prompt")
        hash2 = ai_cache._hash_prompt("test prompt")
        hash3 = ai_cache._hash_prompt("different prompt")

        assert len(hash1) == 16
        assert hash1 == hash2  # 相同提示产生相同哈希
        assert hash1 != hash3  # 不同提示产生不同哈希

    @pytest.mark.asyncio
    async def test_cache_summary(self):
        """缓存总结"""
        mock_cache = MagicMock()
        mock_cache.set = AsyncMock(return_value=True)

        ai_cache = AIServiceCache(mock_cache)
        result = await ai_cache.cache_summary("hash123", "summary text")

        assert result is True
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cached_summary(self):
        """获取缓存总结"""
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value="cached summary")

        ai_cache = AIServiceCache(mock_cache)
        result = await ai_cache.get_cached_summary("hash123")

        assert result == "cached summary"

    @pytest.mark.asyncio
    async def test_cache_entities(self):
        """缓存实体"""
        mock_cache = MagicMock()
        mock_cache.set = AsyncMock(return_value=True)

        ai_cache = AIServiceCache(mock_cache)
        entities = {"defendants": ["John"]}
        result = await ai_cache.cache_entities("hash123", entities)

        assert result is True

    @pytest.mark.asyncio
    async def test_get_cached_entities(self):
        """获取缓存实体"""
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value={"defendants": ["Jane"]})

        ai_cache = AIServiceCache(mock_cache)
        result = await ai_cache.get_cached_entities("hash123")

        assert result == {"defendants": ["Jane"]}

    @pytest.mark.asyncio
    async def test_cache_keywords(self):
        """缓存关键词"""
        mock_cache = MagicMock()
        mock_cache.set = AsyncMock(return_value=True)

        ai_cache = AIServiceCache(mock_cache)
        keywords = ["kw1", "kw2"]
        result = await ai_cache.cache_keywords("hash123", keywords)

        assert result is True

    @pytest.mark.asyncio
    async def test_get_cached_keywords(self):
        """获取缓存关键词"""
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value=["kw1", "kw2"])

        ai_cache = AIServiceCache(mock_cache)
        result = await ai_cache.get_cached_keywords("hash123")

        assert result == ["kw1", "kw2"]
