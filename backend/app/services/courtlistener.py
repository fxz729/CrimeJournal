"""CourtListener API客户端"""
import logging
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class CourtListenerClient:
    """
    CourtListener API客户端

    用于查询美国法院判例数据
    API文档: https://www.courtlistener.com/api/rest/v3/
    """

    BASE_URL = "https://www.courtlistener.com/api/rest/v3"

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: CourtListener API密钥（可选，部分接口需要）
        """
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CrimeJournal/1.0 (Legal Research Application)"
        }
        if api_key:
            self.headers["Authorization"] = f"Token {api_key}"

        self._client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """初始化HTTP客户端"""
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self.headers,
            timeout=30.0
        )
        logger.info("CourtListener客户端初始化成功")

    async def close(self) -> None:
        """关闭HTTP客户端"""
        if self._client:
            await self._client.aclose()
            logger.info("CourtListener客户端已关闭")

    async def search_opinions(
        self,
        query: str,
        court: Optional[str] = None,
        case_number: Optional[str] = None,
        date_min: Optional[str] = None,
        date_max: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索判例意见

        Args:
            query: 搜索关键词
            court: 法院代码
            case_number: 案件编号
            date_min: 开始日期 (YYYY-MM-DD)
            date_max: 结束日期 (YYYY-MM-DD)
            page: 页码
            page_size: 每页数量

        Returns:
            搜索结果
        """
        params = {
            "q": query,
            "page": page,
            "page_size": page_size
        }

        if court:
            params["court"] = court
        if case_number:
            params["docket_number"] = case_number
        if date_min:
            params["dateFiled_min"] = date_min
        if date_max:
            params["dateFiled_max"] = date_max

        try:
            response = await self._client.get("/search/", params=params)
            response.raise_for_status()
            data = response.json()

            logger.info(f"搜索到 {data.get('count', 0)} 条判例")
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"CourtListener搜索失败: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"CourtListener搜索异常: {str(e)}")
            raise

    async def get_opinion_by_id(self, opinion_id: int) -> Dict[str, Any]:
        """
        根据ID获取判例意见详情

        Args:
            opinion_id: 意见ID

        Returns:
            判例详情
        """
        try:
            response = await self._client.get(f"/opinions/{opinion_id}/")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"获取判例失败: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"获取判例异常: {str(e)}")
            raise

    async def get_case_opinions(
        self,
        docket_id: int
    ) -> List[Dict[str, Any]]:
        """
        获取案件的所有意见

        Args:
            docket_id: 案件ID

        Returns:
            意见列表
        """
        try:
            response = await self._client.get(f"/dockets/{docket_id}/opinions/")
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

        except httpx.HTTPStatusError as e:
            logger.error(f"获取案件意见失败: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"获取案件意见异常: {str(e)}")
            raise

    async def get_courts(
        self,
        court_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取法院列表

        Args:
            court_type: 法院类型 (federal, state, etc.)

        Returns:
            法院列表
        """
        params = {}
        if court_type:
            params["court_type"] = court_type

        try:
            response = await self._client.get("/courts/", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

        except httpx.HTTPStatusError as e:
            logger.error(f"获取法院列表失败: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"获取法院列表异常: {str(e)}")
            raise

    async def get_citation_network(
        self,
        citation_type: str,
        cite_urn: str
    ) -> Dict[str, Any]:
        """
        获取引用网络

        Args:
            citation_type: 引用类型 (authorities 或 cited-by)
            cite_urn: 引用URN

        Returns:
            引用网络数据
        """
        endpoint = f"/{citation_type}/{cite_urn}/"

        try:
            response = await self._client.get(endpoint)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"获取引用网络失败: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"获取引用网络异常: {str(e)}")
            raise

    async def get_cluster_by_id(self, cluster_id: int) -> Dict[str, Any]:
        """
        获取案件簇信息（包含所有相关意见）

        Args:
            cluster_id: 簇ID

        Returns:
            簇详情
        """
        try:
            response = await self._client.get(f"/clusters/{cluster_id}/")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"获取簇信息失败: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"获取簇信息异常: {str(e)}")
            raise

    async def search_by_citation(
        self,
        citation: str
    ) -> Dict[str, Any]:
        """
        通过引用搜索案件

        Args:
            citation: 引文格式 (e.g., "123 F.3d 456")

        Returns:
            搜索结果
        """
        params = {"citation": citation}

        try:
            response = await self._client.get("/search/", params=params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"引用搜索失败: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"引用搜索异常: {str(e)}")
            raise

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
