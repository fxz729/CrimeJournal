"""CourtListener API客户端"""
import logging
import re
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


def _extract_plain_text(opinion_data: Dict[str, Any]) -> str:
    """
    从 opinion 数据中提取纯文本。

    优先级：plain_text > html > html_with_citations (XML)
    """
    # 1. plain_text 字段
    plain_text = opinion_data.get("plain_text", "")
    if plain_text and len(plain_text.strip()) > 100:
        return plain_text.strip()

    # 2. html 字段
    html = opinion_data.get("html", "")
    if html and len(html.strip()) > 100:
        return _html_to_text(html)

    # 3. html_with_citations 字段 (XML 格式)
    xml_content = opinion_data.get("html_with_citations", "")
    if xml_content and len(xml_content.strip()) > 100:
        return _html_to_text(xml_content)

    return ""


def _html_to_text(html: str) -> str:
    """将 HTML/XML 内容转换为纯文本。"""
    if not html:
        return ""
    # 移除 XML/HTML 标签，保留文本
    text = re.sub(r'<[^>]+>', ' ', html)
    # 规范化空白字符
    text = re.sub(r'[\s\u200b\xa0]+', ' ', text).strip()
    # 移除多余的空格
    text = re.sub(r' +', ' ', text)
    return text


class CourtListenerClient:
    """
    CourtListener API客户端

    用于查询美国法院判例数据
    API文档: https://www.courtlistener.com/api/rest/v4/
    """

    BASE_URL = "https://www.courtlistener.com/api/rest/v4"

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

            # v4 搜索结果直接在顶层，不需要取 cluster 嵌套
            results = data.get("results", [])
            # 标准化：兼容 v3 格式（v3 results 嵌套在 cluster 中）
            normalized_results = []
            for item in results:
                # v4: 字段直接在顶层，v3: 字段在 cluster 中
                if "cluster" in item:
                    # v3 格式
                    cluster = item.get("cluster", item)
                    normalized_results.append(cluster)
                else:
                    # v4 格式：直接在 item 顶层
                    normalized_results.append(item)

            data["results"] = normalized_results
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
            判例详情（包含 cluster 和 docket 信息，以及纯文本）
        """
        try:
            response = await self._client.get(f"/opinions/{opinion_id}/")
            response.raise_for_status()
            opinion_data = response.json()

            # 提取纯文本（优先 plain_text > html > html_with_citations）
            plain_text = _extract_plain_text(opinion_data)
            opinion_data["plain_text"] = plain_text

            # v4: cluster 是 URL，需要额外请求获取 cluster 详情
            cluster_url = opinion_data.get("cluster")
            if cluster_url:
                cluster_response = await self._client.get(cluster_url)
                cluster_response.raise_for_status()
                cluster_data = cluster_response.json()
                opinion_data["cluster"] = cluster_data

                # 获取 docket 信息（包含 court_id）
                docket_url = cluster_data.get("docket")
                if docket_url:
                    docket_response = await self._client.get(docket_url)
                    docket_response.raise_for_status()
                    docket_data = docket_response.json()
                    opinion_data["docket"] = docket_data

            return opinion_data

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
            # v4: docket opinions endpoint
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
        # v4 中 citation network endpoint 可能返回 HTML 或需要特殊权限
        # 降级处理：返回空结果
        endpoint = f"/{citation_type}/{cite_urn}/"

        try:
            response = await self._client.get(endpoint)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.warning(f"获取引用网络失败（可能需要 Premium）: {e.response.status_code}")
            return {"results": []}
        except Exception as e:
            logger.warning(f"获取引用网络异常: {str(e)}")
            return {"results": []}

    async def get_cluster_by_id(self, cluster_id: int) -> Dict[str, Any]:
        """
        获取案件簇信息（包含所有相关意见）

        Args:
            cluster_id: 簇ID

        Returns:
            簇详情（包含 docket 信息和第一个意见的文本）
        """
        try:
            response = await self._client.get(f"/clusters/{cluster_id}/")
            response.raise_for_status()
            cluster_data = response.json()

            # v4: 获取 docket 信息（包含 court_id）
            docket_url = cluster_data.get("docket")
            if docket_url:
                docket_response = await self._client.get(docket_url)
                docket_response.raise_for_status()
                cluster_data["docket"] = docket_response.json()

            # 获取第一个意见的文本和引用信息
            sub_opinions = cluster_data.get("sub_opinions", [])
            if sub_opinions:
                first_opinion_url = sub_opinions[0]
                opinion_response = await self._client.get(first_opinion_url)
                opinion_response.raise_for_status()
                first_opinion = opinion_response.json()
                # 提取纯文本（优先 plain_text > html > html_with_citations）
                plain_text = _extract_plain_text(first_opinion)
                first_opinion["plain_text"] = plain_text
                cluster_data["_first_opinion"] = first_opinion

            return cluster_data

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
