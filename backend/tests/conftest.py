"""
pytest配置和共享fixtures

提供测试数据库、测试客户端、Mock服务等
"""
import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# 确保app模块在路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 设置测试环境变量
os.environ.setdefault("CLAUDE_API_KEY", "test-claude-key")
os.environ.setdefault("DEEPSEEK_API_KEY", "test-deepseek-key")
os.environ.setdefault("COURTLISTENER_API_TOKEN", "test-courtlistener-token")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_HOURS", "24")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("DEBUG", "true")


# ==================== 事件循环Fixture ====================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建session级别的事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ==================== Mock服务 ====================

class MockCourtListenerClient:
    """Mock CourtListener客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self._client = MagicMock()

    async def initialize(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def search_opinions(
        self,
        query: str,
        court: str = None,
        case_number: str = None,
        date_min: str = None,
        date_max: str = None,
        page: int = 1,
        page_size: int = 20
    ):
        """Mock搜索判例"""
        results = []
        count = 0

        # 根据查询词返回不同的mock数据
        if "robbery" in query.lower():
            results = [
                {
                    "id": 1,
                    "cluster": {
                        "id": 1,
                        "case_name": "People v. Smith",
                        "court": "California Court of Appeal",
                        "court_id": "calapp",
                        "date_filed": "2023-01-15",
                        "citation": "89 Cal.App.4th 123",
                        "docket_number": "A123456",
                    }
                },
                {
                    "id": 2,
                    "cluster": {
                        "id": 2,
                        "case_name": "State v. Johnson",
                        "court": "Supreme Court of California",
                        "court_id": "cal",
                        "date_filed": "2023-02-20",
                        "citation": "89 Cal.4th 456",
                        "docket_number": "B654321",
                    }
                },
            ]
            count = 2
        elif "murder" in query.lower():
            results = [
                {
                    "id": 3,
                    "cluster": {
                        "id": 3,
                        "case_name": "Commonwealth v. Williams",
                        "court": "Superior Court of Pennsylvania",
                        "court_id": "pennapp",
                        "date_filed": "2022-11-10",
                        "citation": "250 A.3d 1",
                        "docket_number": "C111222",
                    }
                },
            ]
            count = 1
        elif "fraud" in query.lower():
            results = [
                {
                    "id": 4,
                    "cluster": {
                        "id": 4,
                        "case_name": "United States v. Anderson",
                        "court": "United States Court of Appeals for the Ninth Circuit",
                        "court_id": "ca9",
                        "date_filed": "2023-03-05",
                        "citation": "45 F.4th 789",
                        "docket_number": "D333444",
                    }
                },
            ]
            count = 1
        else:
            results = [
                {
                    "id": 100,
                    "cluster": {
                        "id": 100,
                        "case_name": f"Test Case for '{query}'",
                        "court": "District Court",
                        "court_id": "dcd",
                        "date_filed": "2023-06-01",
                        "citation": "1 F.4th 100",
                        "docket_number": "TEST001",
                    }
                },
            ]
            count = 1

        return {
            "count": count,
            "next": None,
            "previous": None,
            "results": results
        }

    async def get_opinion_by_id(self, opinion_id: int):
        """Mock获取判例详情"""
        if opinion_id == 1:
            return {
                "id": 1,
                "cluster": {
                    "id": 1,
                    "case_name": "People v. Smith",
                    "case_name_full": "The People of the State of California v. John Smith",
                    "court": "California Court of Appeal",
                    "court_id": "calapp",
                    "date_filed": "2023-01-15",
                    "date_decided": "2023-03-20",
                    "citation": "89 Cal.App.4th 123",
                    "docket_number": "A123456",
                    "keywords": '["robbery", "theft", "California"]',
                    "entities": '{"defendants": ["John Smith"], "courts": ["California Court of Appeal"], "judges": ["Justice Davis"]}',
                },
                "plain_text": "This is a test case about robbery. The defendant John Smith was charged with armed robbery.",
                "html": "<p>This is a test case about robbery.</p>",
            }
        elif opinion_id == 2:
            return {
                "id": 2,
                "cluster": {
                    "id": 2,
                    "case_name": "State v. Johnson",
                    "case_name_full": "State of California v. Michael Johnson",
                    "court": "Supreme Court of California",
                    "court_id": "cal",
                    "date_filed": "2023-02-20",
                    "date_decided": "2023-04-15",
                    "citation": "89 Cal.4th 456",
                    "docket_number": "B654321",
                    "keywords": '["criminal law", "appeal"]',
                    "entities": '{"defendants": ["Michael Johnson"]}',
                },
                "plain_text": "The defendant Michael Johnson appealed his conviction for residential burglary.",
                "html": "<p>Appeal case text.</p>",
            }
        elif opinion_id == 999:
            return {
                "id": 999,
                "cluster": {
                    "id": 999,
                    "case_name": "Empty Case",
                    "court": "Test Court",
                    "court_id": "test",
                    "date_filed": "2023-05-01",
                },
                "plain_text": "",
                "html": "",
            }
        else:
            return {
                "id": opinion_id,
                "cluster": {
                    "id": opinion_id,
                    "case_name": f"Test Case {opinion_id}",
                    "court": "Test Court",
                    "court_id": "test",
                    "date_filed": "2023-01-01",
                },
                "plain_text": f"Test case content for case {opinion_id}",
                "html": f"<p>Test case {opinion_id}</p>",
            }

    async def get_case_opinions(self, docket_id: int):
        """Mock获取案件意见"""
        return [await self.get_opinion_by_id(docket_id)]

    async def get_courts(self, court_type: str = None):
        """Mock获取法院列表"""
        courts = [
            {"id": "ca9", "full_name": "United States Court of Appeals for the Ninth Circuit", "court_type": "federal"},
            {"id": "cal", "full_name": "Supreme Court of California", "court_type": "state"},
        ]
        if court_type:
            courts = [c for c in courts if c.get("court_type") == court_type]
        return courts

    async def get_citation_network(self, citation_type: str, cite_urn: str):
        """Mock引用网络"""
        return {
            "count": 0,
            "results": []
        }

    async def get_cluster_by_id(self, cluster_id: int):
        """Mock获取簇信息"""
        return await self.get_opinion_by_id(cluster_id)

    async def search_by_citation(self, citation: str):
        """Mock引用搜索"""
        return {
            "count": 1,
            "results": [await self.get_opinion_by_id(1)]
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockAIService:
    """Mock AI服务基类"""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def close(self) -> None:
        self._initialized = False

    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Mock生成文本"""
        if "summary" in prompt.lower() or "总结" in prompt:
            return "This is a mock summary of the case."
        elif "entity" in prompt.lower() or "实体" in prompt:
            return '{"defendants": ["Mock Defendant"], "courts": ["Mock Court"]}'
        elif "keyword" in prompt.lower() or "关键词" in prompt:
            return '["mock", "test", "keywords"]'
        else:
            return "Mock AI response"

    async def extract_entities(self, text: str, entity_types: list = None) -> dict:
        """Mock实体提取"""
        return {
            "defendants": ["John Doe"],
            "plaintiffs": ["State"],
            "courts": ["Superior Court"],
            "judges": ["Justice Mock"],
        }

    async def summarize(self, text: str, max_length: int = 500) -> str:
        """Mock总结"""
        if not text:
            return ""
        return f"Mock summary of case ({len(text)} chars). The case involves important legal issues."

    async def extract_keywords(self, text: str, top_n: int = 10) -> list:
        """Mock关键词提取"""
        return ["robbery", "theft", "criminal", "law", "court", "defendant", "prosecution", "verdict", "appeal", "conviction"]

    async def classify(self, text: str, categories: list) -> str:
        """Mock分类"""
        return categories[0] if categories else "unknown"

    async def health_check(self) -> bool:
        return True


class MockCacheService:
    """Mock Redis缓存服务"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: str = None, key_prefix: str = "crimejournal:", **kwargs):
        self._store = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def close(self) -> None:
        self._initialized = False

    def _build_key(self, key: str) -> str:
        return key

    async def get(self, key: str):
        return self._store.get(key)

    async def set(self, key: str, value, ttl: int = None) -> bool:
        self._store[key] = value
        return True

    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        return key in self._store

    async def get_or_set(self, key: str, fetch_func, ttl: int = None):
        if key in self._store:
            return self._store[key]
        value = await fetch_func()
        if value is not None:
            self._store[key] = value
        return value

    async def clear_pattern(self, pattern: str) -> int:
        keys_to_delete = [k for k in self._store if pattern.replace("*", "") in k]
        for k in keys_to_delete:
            del self._store[k]
        return len(keys_to_delete)

    async def incr(self, key: str, amount: int = 1) -> int:
        if key not in self._store:
            self._store[key] = 0
        self._store[key] += amount
        return self._store[key]

    async def get_ttl(self, key: str) -> int:
        return -1  # 无过期

    async def expire(self, key: str, ttl: int) -> bool:
        return True

    async def health_check(self) -> bool:
        return True


# ==================== Mock缓存辅助类 ====================

class MockAIServiceCache:
    """Mock AI服务缓存"""

    def __init__(self, cache_service: MockCacheService):
        self.cache = cache_service

    async def cache_summary(self, text_hash: str, summary: str, ttl: int = 3600) -> bool:
        return await self.cache.set(f"summary:{text_hash}", summary, ttl)

    async def get_cached_summary(self, text_hash: str):
        return await self.cache.get(f"summary:{text_hash}")

    async def cache_entities(self, text_hash: str, entities: dict, ttl: int = 3600) -> bool:
        return await self.cache.set(f"entities:{text_hash}", entities, ttl)

    async def get_cached_entities(self, text_hash: str):
        return await self.cache.get(f"entities:{text_hash}")

    async def cache_keywords(self, text_hash: str, keywords: list, ttl: int = 3600) -> bool:
        return await self.cache.set(f"keywords:{text_hash}", keywords, ttl)

    async def get_cached_keywords(self, text_hash: str):
        return await self.cache.get(f"keywords:{text_hash}")


# ==================== 应用Fixture ====================

@pytest_asyncio.fixture
async def mock_courtlistener():
    """提供Mock CourtListener客户端"""
    client = MockCourtListenerClient()
    await client.initialize()
    yield client
    await client.close()


@pytest_asyncio.fixture
async def mock_cache_service():
    """提供Mock缓存服务"""
    cache = MockCacheService()
    await cache.initialize()
    yield cache
    await cache.close()


@pytest.fixture
def mock_ai_service():
    """提供Mock AI服务"""
    return MockAIService("test-key", "test-model")


@pytest.fixture
def mock_ai_cache():
    """提供Mock AI缓存辅助类"""
    cache = MockCacheService()
    return MockAIServiceCache(cache)


# ==================== 认证辅助 ====================

@pytest.fixture
def test_user_email():
    return "test@example.com"


@pytest.fixture
def test_user_password():
    return "SecurePass123!"


@pytest.fixture
def test_user_data(test_user_email, test_user_password):
    return {
        "email": test_user_email,
        "password": test_user_password,
        "full_name": "Test User",
    }


# ==================== FastAPI测试客户端 ====================

@pytest.fixture
def app():
    """创建测试应用实例"""
    from app.main import app
    return app


@pytest.fixture
def client(app) -> TestClient:
    """创建同步测试客户端"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ==================== Token生成辅助 ====================

@pytest.fixture
def create_auth_token():
    """创建认证Token的辅助函数"""
    from datetime import datetime, timedelta
    import jwt
    from app.config import settings

    def _create_token(user_id: int, email: str) -> str:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    return _create_token


@pytest.fixture
def auth_headers(create_auth_token, test_user_email):
    """创建认证请求头"""
    token = create_auth_token(user_id=1, email=test_user_email)
    return {"Authorization": f"Bearer {token}"}


# ==================== 清空Fake数据库 ====================

@pytest.fixture(autouse=True)
def clear_fake_db():
    """每个测试前后清空Fake数据库"""
    from app.api import auth as auth_module
    # 保存原始数据库
    auth_original = auth_module.FAKE_USERS_DB.copy()
    auth_module.FAKE_USERS_DB.clear()

    # 保存search模块的fake数据库
    import app.api.search as search_module
    search_history_original = search_module.FAKE_SEARCH_HISTORY.copy()
    favorites_original = search_module.FAKE_FAVORITES.copy()
    search_module.FAKE_SEARCH_HISTORY.clear()
    search_module.FAKE_FAVORITES.clear()

    yield

    # 恢复
    auth_module.FAKE_USERS_DB.clear()
    auth_module.FAKE_USERS_DB.update(auth_original)
    search_module.FAKE_SEARCH_HISTORY.clear()
    search_module.FAKE_SEARCH_HISTORY.update(search_history_original)
    search_module.FAKE_FAVORITES.clear()
    search_module.FAKE_FAVORITES.update(favorites_original)


# ==================== 重置全局服务实例 ====================

@pytest.fixture(autouse=True)
def reset_global_services():
    """每个测试后重置全局服务实例"""
    yield
    # 重置cases.py中的全局服务实例
    import app.api.cases as cases_module
    cases_module._courtlistener_client = None
    cases_module._ai_router = None
    cases_module._cache_service = None
