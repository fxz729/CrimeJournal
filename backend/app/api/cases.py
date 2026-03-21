"""
Cases API Routes

案例搜索、详情、AI分析相关API
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user, get_optional_user, FAKE_USERS_DB
from app.middleware.usage import check_search_access, get_user_daily_usage, get_daily_limit, increment_user_usage
from app.config import settings
from app.services import CourtListenerClient, AIRouter, AIServiceCache, CacheService
from app.services.ai import MiniMaxService, TaskType

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== Database Setup ====================
# TODO: 后续集成真实数据库和依赖注入
engine = None


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    global engine
    if engine is None:
        engine = create_engine(settings.database_url, echo=settings.debug)
    # 简化实现，实际应使用async session
    raise NotImplementedError("需要配置数据库会话")


# ==================== Pydantic Models ====================

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="搜索关键词")
    court: Optional[str] = Field(None, description="法院代码")
    date_min: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    date_max: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class CaseSearchResult(BaseModel):
    """案例搜索结果项"""
    id: int
    case_name: str
    court: Optional[str]
    court_id: Optional[str]
    date_filed: Optional[datetime]
    citation: Optional[str]
    docket_number: Optional[str]
    source: str = "courtlistener"


class SearchResponse(BaseModel):
    """搜索响应"""
    total: int
    page: int
    page_size: int
    results: List[CaseSearchResult]


class CaseDetailResponse(BaseModel):
    """案例详情响应"""
    id: int
    courtlistener_id: int
    case_name: str
    case_name_full: Optional[str]
    court: Optional[str]
    court_id: Optional[str]
    date_filed: Optional[datetime]
    date_decided: Optional[datetime]
    citation: Optional[str]
    docket_number: Optional[str]
    plain_text: Optional[str]
    html_text: Optional[str]
    summary: Optional[str]
    keywords: Optional[List[str]]
    entities: Optional[Dict[str, List[str]]]
    created_at: datetime


class SummarizeRequest(BaseModel):
    """AI总结请求"""
    max_length: int = Field(500, ge=100, le=2000, description="最大总结长度")


class SummarizeResponse(BaseModel):
    """AI总结响应"""
    case_id: int
    summary: str
    cached: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class EntitiesRequest(BaseModel):
    """实体提取请求"""
    entity_types: Optional[List[str]] = Field(
        None,
        description="实体类型列表，如 ['当事人', '法院', '法官']"
    )


class EntitiesResponse(BaseModel):
    """实体提取响应"""
    case_id: int
    entities: Dict[str, List[str]]
    cached: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class KeywordsRequest(BaseModel):
    """关键词提取请求"""
    top_n: int = Field(10, ge=3, le=50, description="提取关键词数量")


class KeywordsResponse(BaseModel):
    """关键词提取响应"""
    case_id: int
    keywords: List[str]
    cached: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class SimilarCasesRequest(BaseModel):
    """相似案例请求"""
    limit: int = Field(5, ge=1, le=20, description="返回相似案例数量")


class SimilarCaseItem(BaseModel):
    """相似案例项"""
    id: int
    case_name: str
    court: Optional[str]
    date_filed: Optional[datetime]
    similarity: float = Field(..., ge=0, le=1, description="相似度分数")


class SimilarCasesResponse(BaseModel):
    """相似案例响应"""
    case_id: int
    similar_cases: List[SimilarCaseItem]


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True


# ==================== Service Initialization ====================
# 全局服务实例（单例模式）
_courtlistener_client: Optional[CourtListenerClient] = None
_ai_router: Optional[AIRouter] = None
_cache_service: Optional[CacheService] = None


async def get_courtlistener() -> CourtListenerClient:
    """获取CourtListener客户端"""
    global _courtlistener_client
    if _courtlistener_client is None:
        _courtlistener_client = CourtListenerClient(settings.courtlistener_api_token)
        await _courtlistener_client.initialize()
    return _courtlistener_client


async def get_ai_router() -> AIRouter:
    """获取AI路由器 - 统一使用MiniMax"""
    global _ai_router
    if _ai_router is None:
        # 统一使用MiniMax（M2.7最新模型）
        minimax_service = MiniMaxService(
            api_key=settings.minimax_api_key,
            model=settings.minimax_model,
            base_url=settings.minimax_base_url
        )
        # 统一使用MiniMax（M2.7最新模型）
        _ai_router = AIRouter(minimax_service=minimax_service)
        await _ai_router.initialize_all()
    return _ai_router


async def get_cache() -> CacheService:
    """获取缓存服务"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
        await _cache_service.initialize()
    return _cache_service


# ==================== API Routes ====================

@router.get(
    "/search",
    response_model=SearchResponse,
    summary="搜索案例",
    description="从CourtListener搜索法律案例",
)
async def search_cases(
    q: str = Query(..., min_length=1, max_length=500, description="搜索关键词"),
    court: Optional[str] = Query(None, description="法院代码"),
    date_min: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_max: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    搜索法律案例

    从CourtListener API搜索案例，支持：
    - 关键词搜索
    - 法院过滤
    - 日期范围过滤
    - 分页

    需要JWT认证

    用量限制：
    - Free 用户每天 10 次搜索
    - Pro 用户无限制
    """
    # 用量限制检查
    if current_user:
        user_id = current_user["id"]
        # 获取用户订阅等级
        user_info = FAKE_USERS_DB.get(user_id)
        subscription_tier = user_info.get("subscription_tier", "free") if user_info else "free"

        # 检查搜索限制（仅记录，不阻止，因为中间件已经记录）
        # 实际限制由 check_search_access 抛出 429
        check_search_access(user_id, subscription_tier)

    try:
        client = await get_courtlistener()

        result = await client.search_opinions(
            query=q,
            court=court,
            date_min=date_min,
            date_max=date_max,
            page=page,
            page_size=page_size,
        )

        # 解析结果
        results = []
        for item in result.get("results", []):
            case_data = item.get("cluster", item)
            results.append(
                CaseSearchResult(
                    id=case_data.get("id"),
                    case_name=case_data.get("case_name", ""),
                    court=case_data.get("court"),
                    court_id=case_data.get("court_id"),
                    date_filed=case_data.get("date_filed"),
                    citation=case_data.get("citation"),
                    docket_number=case_data.get("docket_number"),
                )
            )

        # TODO: 保存搜索历史
        user_email = current_user['email'] if current_user else 'anonymous'
        logger.info(f"用户 {user_email} 搜索: {q}, 结果: {result.get('count', 0)}")

        return SearchResponse(
            total=result.get("count", 0),
            page=page,
            page_size=page_size,
            results=results,
        )

    except Exception as e:
        logger.error(f"案例搜索失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}",
        )


@router.get(
    "/{case_id}",
    response_model=CaseDetailResponse,
    summary="获取案例详情",
    description="获取指定案例的详细信息",
)
async def get_case_detail(
    case_id: int,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    获取案例详情

    根据ID获取案例详细信息，包括AI生成的内容（总结、关键词、实体）

    需要JWT认证
    """
    try:
        client = await get_courtlistener()

        # 从CourtListener获取案例详情
        case_data = await client.get_opinion_by_id(case_id)
        cluster = case_data.get("cluster", {})

        # 解析JSON字段
        keywords = None
        entities = None

        if cluster.get("keywords"):
            try:
                keywords = json.loads(cluster["keywords"])
            except json.JSONDecodeError:
                keywords = [cluster["keywords"]]

        if cluster.get("entities"):
            try:
                entities = json.loads(cluster["entities"])
            except json.JSONDecodeError:
                entities = {}

        return CaseDetailResponse(
            id=cluster.get("id", case_id),
            courtlistener_id=cluster.get("id", case_id),
            case_name=cluster.get("case_name", ""),
            case_name_full=cluster.get("case_name_full"),
            court=cluster.get("court"),
            court_id=cluster.get("court_id"),
            date_filed=cluster.get("date_filed"),
            date_decided=cluster.get("date_decided"),
            citation=cluster.get("citation"),
            docket_number=cluster.get("docket_number"),
            plain_text=case_data.get("plain_text"),
            html_text=case_data.get("html"),
            summary=cluster.get("summary"),
            keywords=keywords,
            entities=entities,
            created_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"获取案例详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"案例不存在: {str(e)}",
        )


@router.post(
    "/{case_id}/summarize",
    response_model=SummarizeResponse,
    summary="AI总结案例",
    description="使用AI生成案例总结",
)
async def summarize_case(
    case_id: int,
    request: SummarizeRequest = SummarizeRequest(),
    current_user: dict = Depends(get_current_user),
):
    """
    AI案例总结

    使用MiniMax AI生成案例总结，支持缓存

    需要JWT认证
    """
    try:
        client = await get_courtlistener()
        ai_router = await get_ai_router()
        cache = await get_cache()

        # 获取案例文本
        case_data = await client.get_opinion_by_id(case_id)
        plain_text = case_data.get("plain_text", "")

        if not plain_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="案例文本为空，无法生成总结",
            )

        # 检查缓存
        import hashlib
        text_hash = hashlib.md5(plain_text.encode()).hexdigest()[:16]
        ai_cache = AIServiceCache(cache)
        cached_summary = await ai_cache.get_cached_summary(text_hash)

        if cached_summary:
            logger.info(f"案例 {case_id} 总结命中缓存")
            return SummarizeResponse(
                case_id=case_id,
                summary=cached_summary,
                cached=True,
            )

        # 调用AI生成总结
        summary = await ai_router.summarize_case(
            text=plain_text,
            max_length=request.max_length,
        )

        # 缓存结果
        await ai_cache.cache_summary(text_hash, summary)

        logger.info(f"案例 {case_id} 总结生成完成")

        return SummarizeResponse(
            case_id=case_id,
            summary=summary,
            cached=False,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"案例总结失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务错误: {str(e)}",
        )


@router.post(
    "/{case_id}/entities",
    response_model=EntitiesResponse,
    summary="提取案例实体",
    description="使用AI从案例中提取关键实体",
)
async def extract_entities(
    case_id: int,
    request: EntitiesRequest = EntitiesRequest(),
    current_user: dict = Depends(get_current_user),
):
    """
    AI实体提取

    使用MiniMax AI从案例文本中提取关键实体（当事人、法院、法官等）

    需要JWT认证
    """
    try:
        client = await get_courtlistener()
        ai_router = await get_ai_router()
        cache = await get_cache()

        # 获取案例文本
        case_data = await client.get_opinion_by_id(case_id)
        plain_text = case_data.get("plain_text", "")

        if not plain_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="案例文本为空，无法提取实体",
            )

        # 检查缓存
        import hashlib
        text_hash = hashlib.md5(plain_text.encode()).hexdigest()[:16]
        ai_cache = AIServiceCache(cache)
        cached_entities = await ai_cache.get_cached_entities(text_hash)

        if cached_entities:
            logger.info(f"案例 {case_id} 实体提取命中缓存")
            return EntitiesResponse(
                case_id=case_id,
                entities=cached_entities,
                cached=True,
            )

        # 调用AI提取实体
        entities = await ai_router.extract_entities(
            text=plain_text,
            entity_types=request.entity_types,
        )

        # 缓存结果
        await ai_cache.cache_entities(text_hash, entities)

        logger.info(f"案例 {case_id} 实体提取完成")

        return EntitiesResponse(
            case_id=case_id,
            entities=entities,
            cached=False,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"实体提取失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务错误: {str(e)}",
        )


@router.post(
    "/{case_id}/keywords",
    response_model=KeywordsResponse,
    summary="提取案例关键词",
    description="使用AI从案例中提取关键词",
)
async def extract_keywords(
    case_id: int,
    request: KeywordsRequest = KeywordsRequest(),
    current_user: dict = Depends(get_current_user),
):
    """
    AI关键词提取

    使用MiniMax AI从案例文本中提取关键词

    需要JWT认证
    """
    try:
        client = await get_courtlistener()
        ai_router = await get_ai_router()
        cache = await get_cache()

        # 获取案例文本
        case_data = await client.get_opinion_by_id(case_id)
        plain_text = case_data.get("plain_text", "")

        if not plain_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="案例文本为空，无法提取关键词",
            )

        # 检查缓存
        import hashlib
        text_hash = hashlib.md5(plain_text.encode()).hexdigest()[:16]
        ai_cache = AIServiceCache(cache)
        cached_keywords = await ai_cache.get_cached_keywords(text_hash)

        if cached_keywords:
            logger.info(f"案例 {case_id} 关键词提取命中缓存")
            return KeywordsResponse(
                case_id=case_id,
                keywords=cached_keywords[:request.top_n],
                cached=True,
            )

        # 调用AI提取关键词
        keywords = await ai_router.extract_keywords(
            text=plain_text,
            top_n=request.top_n,
        )

        # 缓存结果
        await ai_cache.cache_keywords(text_hash, keywords)

        logger.info(f"案例 {case_id} 关键词提取完成")

        return KeywordsResponse(
            case_id=case_id,
            keywords=keywords[:request.top_n],
            cached=False,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"关键词提取失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务错误: {str(e)}",
        )


@router.get(
    "/{case_id}/similar",
    response_model=SimilarCasesResponse,
    summary="查找相似案例",
    description="基于案例内容查找相似的法律案例",
)
async def find_similar_cases(
    case_id: int,
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    查找相似案例

    基于向量相似度查找相似的法律案例

    需要JWT认证

    注意：当前实现为简化版本，实际需要：
    1. 生成案例文本的向量嵌入
    2. 存储到向量数据库
    3. 使用向量检索查找相似案例
    """
    try:
        client = await get_courtlistener()

        # 获取原案例
        case_data = await client.get_opinion_by_id(case_id)
        cluster = case_data.get("cluster", {})

        # TODO: 实现向量相似度搜索
        # 当前实现：基于引用关系查找相关案例
        citation_urn = f"cluster:{case_id}"

        try:
            cited_by = await client.get_citation_network("cited-by", citation_urn)
            similar_items = cited_by.get("results", [])[:limit]
        except Exception:
            # 如果引用网络不可用，返回空结果
            similar_items = []

        # 构建响应
        similar_cases = []
        for item in similar_items:
            similar_cluster = item.get("citing_cluster", item)
            similar_cases.append(
                SimilarCaseItem(
                    id=similar_cluster.get("id"),
                    case_name=similar_cluster.get("case_name", ""),
                    court=similar_cluster.get("court"),
                    date_filed=similar_cluster.get("date_filed"),
                    similarity=0.8,  # TODO: 实现真实相似度计算
                )
            )

        logger.info(f"案例 {case_id} 相似案例查询，返回 {len(similar_cases)} 条")

        return SimilarCasesResponse(
            case_id=case_id,
            similar_cases=similar_cases,
        )

    except Exception as e:
        logger.error(f"相似案例查询失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}",
        )
