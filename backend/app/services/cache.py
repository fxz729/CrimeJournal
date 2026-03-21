"""Redis缓存服务"""
import json
import logging
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis缓存服务

    提供统一的缓存接口，支持自动序列化/反序列化
    """

    # 默认过期时间
    DEFAULT_TTL = 3600  # 1小时
    SHORT_TTL = 300     # 5分钟
    LONG_TTL = 86400    # 24小时

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "crimejournal:",
        **kwargs
    ):
        """
        初始化缓存服务

        Args:
            host: Redis主机
            port: Redis端口
            db: 数据库编号
            password: 密码（可选）
            key_prefix: 键前缀
            **kwargs: 其他Redis配置
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.key_prefix = key_prefix
        self._client: Optional[redis.Redis] = None

    async def initialize(self) -> None:
        """初始化Redis连接"""
        self._client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True,
            encoding="utf-8"
        )

        # 测试连接
        try:
            await self._client.ping()
            logger.info(f"Redis连接成功: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise

    async def close(self) -> None:
        """关闭Redis连接"""
        if self._client:
            await self._client.close()
            logger.info("Redis连接已关闭")

    def _build_key(self, key: str) -> str:
        """构建带前缀的键"""
        return f"{self.key_prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在返回None
        """
        try:
            full_key = self._build_key(key)
            value = await self._client.get(full_key)

            if value is None:
                return None

            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except Exception as e:
            logger.error(f"缓存获取失败: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）

        Returns:
            是否成功
        """
        try:
            full_key = self._build_key(key)

            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            else:
                value = str(value)

            expire_time = ttl if ttl is not None else self.DEFAULT_TTL

            await self._client.setex(full_key, expire_time, value)
            logger.debug(f"缓存设置成功: {full_key}, TTL: {expire_time}s")
            return True

        except Exception as e:
            logger.error(f"缓存设置失败: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否成功
        """
        try:
            full_key = self._build_key(key)
            result = await self._client.delete(full_key)
            return result > 0

        except Exception as e:
            logger.error(f"缓存删除失败: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            full_key = self._build_key(key)
            return await self._client.exists(full_key) > 0
        except Exception as e:
            logger.error(f"缓存检查失败: {str(e)}")
            return False

    async def get_or_set(
        self,
        key: str,
        fetch_func,
        ttl: Optional[int] = None
    ) -> Any:
        """
        获取缓存，不存在则调用函数获取并缓存

        Args:
            key: 缓存键
            fetch_func: 获取数据的异步函数
            ttl: 过期时间

        Returns:
            缓存值
        """
        # 尝试获取缓存
        cached = await self.get(key)
        if cached is not None:
            logger.debug(f"缓存命中: {key}")
            return cached

        # 调用函数获取数据
        logger.debug(f"缓存未命中，执行fetch: {key}")
        value = await fetch_func()

        # 缓存结果
        if value is not None:
            await self.set(key, value, ttl)

        return value

    async def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的所有键

        Args:
            pattern: 匹配模式（如 "user:*"）

        Returns:
            删除的键数量
        """
        try:
            full_pattern = self._build_key(pattern)
            keys = []

            async for key in self._client.scan_iter(match=full_pattern):
                keys.append(key)

            if keys:
                deleted = await self._client.delete(*keys)
                logger.info(f"清除 {deleted} 个缓存键，模式: {pattern}")
                return deleted

            return 0

        except Exception as e:
            logger.error(f"缓存模式清除失败: {str(e)}")
            return 0

    async def incr(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        try:
            full_key = self._build_key(key)
            return await self._client.incrby(full_key, amount)
        except Exception as e:
            logger.error(f"缓存递增失败: {str(e)}")
            return 0

    async def get_ttl(self, key: str) -> int:
        """获取键的剩余TTL（秒）"""
        try:
            full_key = self._build_key(key)
            return await self._client.ttl(full_key)
        except Exception as e:
            logger.error(f"获取TTL失败: {str(e)}")
            return -1

    async def expire(self, key: str, ttl: int) -> bool:
        """设置键的过期时间"""
        try:
            full_key = self._build_key(key)
            return await self._client.expire(full_key, ttl)
        except Exception as e:
            logger.error(f"设置过期时间失败: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            pong = await self._client.ping()
            return pong is True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {str(e)}")
            return False

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


# AI服务相关的缓存辅助类
class AIServiceCache:
    """AI服务结果缓存"""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service

    def _hash_prompt(self, prompt: str) -> str:
        """对长提示进行哈希，生成短键"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()[:16]

    async def cache_summary(
        self,
        text_hash: str,
        summary: str,
        ttl: int = CacheService.LONG_TTL
    ) -> bool:
        """缓存案例总结"""
        key = f"summary:{text_hash}"
        return await self.cache.set(key, summary, ttl)

    async def get_cached_summary(self, text_hash: str) -> Optional[str]:
        """获取缓存的案例总结"""
        key = f"summary:{text_hash}"
        return await self.cache.get(key)

    async def cache_entities(
        self,
        text_hash: str,
        entities: dict,
        ttl: int = CacheService.LONG_TTL
    ) -> bool:
        """缓存实体提取结果"""
        key = f"entities:{text_hash}"
        return await self.cache.set(key, entities, ttl)

    async def get_cached_entities(self, text_hash: str) -> Optional[dict]:
        """获取缓存的实体"""
        key = f"entities:{text_hash}"
        return await self.cache.get(key)

    async def cache_keywords(
        self,
        text_hash: str,
        keywords: list,
        ttl: int = CacheService.LONG_TTL
    ) -> bool:
        """缓存关键词"""
        key = f"keywords:{text_hash}"
        return await self.cache.set(key, keywords, ttl)

    async def get_cached_keywords(self, text_hash: str) -> Optional[list]:
        """获取缓存的关键词"""
        key = f"keywords:{text_hash}"
        return await self.cache.get(key)
