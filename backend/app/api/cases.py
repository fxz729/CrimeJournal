"""
Cases API Routes

案例搜索、详情、AI分析相关API
"""

import asyncio
import hashlib
import json
import logging
import math
from typing import Optional, List, Dict, Any

from app.services.slug import build_slug_url, parse_slug
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from pydantic import BaseModel, Field

from app.api.auth import get_current_user, get_optional_user
from app.middleware.usage import check_search_access
from app.config import settings
from app.services import CourtListenerClient, AIRouter, AIServiceCache, CacheService
from app.services.ai import MiniMaxService, DeepSeekService, TaskType

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_user_subscription_tier(user_id: int) -> str:
    """
    从 SQLite 读取用户的订阅等级（同步函数，用于 async 端点中 via asyncio.to_thread）。
    """
    from app.api.auth import get_session_local, DBUser
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user is None:
            return "free"
        return user.subscription_tier or "free"
    finally:
        db.close()


def _check_subscription_feature(user_id: int, feature_name: str) -> bool:
    """
    检查用户订阅等级是否具有指定功能。
    如果用户未登录（user_id 为 None）返回 False。
    如果订阅信息无法读取，返回 False（降级为无权限）。
    """
    if user_id is None:
        return False
    from app.api.auth import get_session_local, DBUser
    from app.api.subscriptions import SUBSCRIPTION_PLANS
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        tier = user.subscription_tier or "free" if user else "free"
        plan = SUBSCRIPTION_PLANS.get(tier, SUBSCRIPTION_PLANS["free"])
        return bool(plan.get(feature_name, False))
    except Exception:
        return False
    finally:
        db.close()


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
    slug: Optional[str] = None
    slug_url: Optional[str] = None
    has_text: bool = False


class SearchResponse(BaseModel):
    """搜索响应"""
    total: int
    page: int
    page_size: int
    total_pages: int = 1
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
    plain_text_formatted: Optional[str] = None
    html_text: Optional[str]
    summary: Optional[str]
    keywords: Optional[List[str]]
    entities: Optional[Dict[str, List[str]]]
    created_at: datetime
    source_url: Optional[str] = None
    slug: Optional[str] = None
    slug_url: Optional[str] = None


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


class TranslateRequest(BaseModel):
    """翻译请求"""
    target_language: str = Field("English", description="目标语言")
    source_language: str = Field("auto", description="源语言，auto表示自动检测")


class TranslateResponse(BaseModel):
    """翻译响应"""
    case_id: int
    translated_text: str
    source_language: str
    target_language: str


class FormatTextResponse(BaseModel):
    """整理后的文本响应"""
    case_id: int
    plain_text_formatted: str
    cached: bool = False


class ShareLinkResponse(BaseModel):
    """分享链接响应"""
    share_url: str
    token: str
    expires_in: int = 86400


class SharedCaseResponse(BaseModel):
    """分享案例响应（公开，无需登录）"""
    case_name: str
    court: Optional[str]
    date_filed: Optional[datetime]
    citation: Optional[str]
    summary: Optional[str]


# ==================== Service Dependencies ====================
# 使用 FastAPI 依赖注入，实例存储在 app.state 中


async def get_courtlistener(request: Request) -> CourtListenerClient:
    """获取CourtListener客户端（依赖注入，app.state 缓存）"""
    if not hasattr(request.app.state, "_courtlistener_client") or request.app.state._courtlistener_client is None:
        client = CourtListenerClient(settings.courtlistener_api_token)
        await client.initialize()
        request.app.state._courtlistener_client = client
    return request.app.state._courtlistener_client


async def get_ai_router(request: Request) -> AIRouter:
    """获取AI路由器（从 app.state 复用已在 lifespan 中初始化的实例）"""
    if not hasattr(request.app.state, "_ai_router") or request.app.state._ai_router is None:
        # Fallback: 如果 lifespan 未初始化（直接运行单个端点等场景），按需创建
        minimax_service = MiniMaxService(
            api_key=settings.minimax_api_key,
            model=settings.minimax_model,
            base_url=settings.minimax_base_url
        )
        deepseek_service = DeepSeekService(
            api_key=settings.deepseek_api_key,
            model="deepseek-chat",
            base_url=settings.deepseek_base_url
        )
        router = AIRouter(
            minimax_service=minimax_service,
            deepseek_service=deepseek_service
        )
        await router.initialize_all()
        request.app.state._ai_router = router
    return request.app.state._ai_router


async def get_cache(request: Request) -> CacheService:
    """获取缓存服务（依赖注入，app.state 缓存）"""
    if not hasattr(request.app.state, "_cache_service") or request.app.state._cache_service is None:
        cache = CacheService()
        await cache.initialize()
        request.app.state._cache_service = cache
    return request.app.state._cache_service


# ==================== API Routes ====================

@router.get(
    "/search",
    response_model=SearchResponse,
    summary="搜索案例",
    description="从CourtListener搜索法律案例",
)
async def search_cases(
    request: Request,
    q: str = Query(..., min_length=1, max_length=500, description="搜索关键词"),
    court: Optional[str] = Query(None, description="法院代码"),
    date_min: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_max: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    has_text: Optional[bool] = Query(None, description="筛选有全文(True)或无全文(False)的案例"),
    current_user: Optional[dict] = Depends(get_optional_user),
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
):
    """
    搜索法律案例

    从CourtListener API搜索案例，支持：
    - 关键词搜索
    - 法院过滤
    - 日期范围过滤
    - 分页
    - has_text: 筛选有全文或无全文的案例（有 sub_opinions 则有全文）

    需要JWT认证

    用量限制：
    - Free 用户每天 10 次搜索
    - Pro 用户无限制
    """
    # 用量限制检查 - 从 SQLite 读取订阅等级
    if current_user:
        user_id = current_user["id"]
        subscription_tier = await asyncio.to_thread(_get_user_subscription_tier, user_id)
        check_search_access(user_id, subscription_tier)

    try:
        # has_text 筛选时多抓取一些结果（因为本地过滤会减少条目）
        fetch_size = page_size * 3 if has_text is not None else page_size
        result = await courtlistener.search_opinions(
            query=q,
            court=court,
            date_min=date_min,
            date_max=date_max,
            page=page,
            page_size=fetch_size,
        )

        # 解析结果
        results = []
        for item in result.get("results", []):
            # v4 搜索结果: caseName, court_id, dateFiled, docketNumber (驼峰), 无 id 有 cluster_id
            # v3 搜索结果: case_name, court_id, date_filed, docket_number (蛇形), 有 id
            # 兼容两种格式
            item_id = item.get("cluster_id") or item.get("id")
            case_name = item.get("caseName") or item.get("case_name") or ""
            court_val = item.get("court") or item.get("court_id") or ""
            court_id_val = item.get("court_id") or ""
            date_filed_val = item.get("dateFiled") or item.get("date_filed") or None
            docket_number_val = item.get("docketNumber") or item.get("docket_number") or ""
            # v4 citation 是数组，v3 citation 是字符串
            raw_citation = item.get("citation", [])
            if isinstance(raw_citation, list):
                citation_str = ", ".join(raw_citation) if raw_citation else ""
            else:
                citation_str = raw_citation or ""
            # has_text: v4 有 sub_opinions 字段（意见URL列表），v3 有 opinions 字段
            sub_opinions = item.get("sub_opinions", [])
            opinions = item.get("opinions", [])
            result_has_text = bool(sub_opinions or opinions)
            # has_text 筛选：None=不过筛，True=只看有文本的，False=只看无文本的
            if has_text is not None and has_text != result_has_text:
                continue
            slug_url = build_slug_url(
                case_id=item_id,
                case_name=case_name,
                court_id=court_id_val,
                citation=citation_str,
            )
            results.append(
                CaseSearchResult(
                    id=item_id,
                    case_name=case_name,
                    court=court_val,
                    court_id=court_id_val,
                    date_filed=date_filed_val,
                    citation=citation_str or None,
                    docket_number=docket_number_val or None,
                    slug=slug_url.lstrip("/cases/"),
                    slug_url=slug_url,
                    has_text=result_has_text,
                )
            )

        # has_text 筛选时，total 反映过滤后的实际数量
        if has_text is not None:
            total = len(results)
            total_pages = 1
            results = results[:page_size]
        else:
            total = result.get("count", 0)
            total_pages = math.ceil(total / page_size) if page_size > 0 else 1

        # TODO: 保存搜索历史
        user_email = current_user['email'] if current_user else 'anonymous'
        filter_info = f" [has_text={has_text}]" if has_text is not None else ""
        logger.info(f"用户 {user_email} 搜索: {q}, 结果: {result.get('count', 0)}{filter_info}")

        return SearchResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            results=results,
        )

    except Exception as e:
        logger.error(f"案例搜索失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}",
        )


@router.post(
    "/{case_id}/summarize",
    response_model=SummarizeResponse,
    summary="AI总结案例",
    description="使用AI生成案例总结",
)
async def summarize_case(
    request: Request,
    case_id: int,
    request_body: SummarizeRequest = SummarizeRequest(),
    current_user: dict = Depends(get_current_user),
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
    ai_router: AIRouter = Depends(get_ai_router),
    cache: CacheService = Depends(get_cache),
):
    """
    AI案例总结

    使用MiniMax AI生成案例总结，支持缓存

    需要JWT认证，且订阅等级需要支持 ai_summaries
    """
    # 订阅等级检查
    if not _check_subscription_feature(current_user["id"], "ai_summaries"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI摘要功能需要 Pro 或以上订阅计划",
        )
    try:
        # 服务已通过 Depends 注入
        case_data = await courtlistener.get_opinion_by_id(case_id)
        plain_text = case_data.get("plain_text", "")

        if not plain_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="案例文本为空，无法生成总结",
            )

        # 检查缓存
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
            max_length=request_body.max_length,
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
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
    ai_router: AIRouter = Depends(get_ai_router),
    cache: CacheService = Depends(get_cache),
):
    """
    AI实体提取

    使用MiniMax AI从案例文本中提取关键实体（当事人、法院、法官等）

    需要JWT认证，且订阅等级需要支持 entity_extraction
    """
    # 订阅等级检查
    if not _check_subscription_feature(current_user["id"], "entity_extraction"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="实体提取功能需要 Pro 或以上订阅计划",
        )
    try:
        # 服务已通过 Depends 注入
        case_data = await courtlistener.get_opinion_by_id(case_id)
        plain_text = case_data.get("plain_text", "")

        if not plain_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="案例文本为空，无法提取实体",
            )

        # 检查缓存
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
    request: Request,
    case_id: int,
    request_body: KeywordsRequest = KeywordsRequest(),
    current_user: dict = Depends(get_current_user),
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
    ai_router: AIRouter = Depends(get_ai_router),
    cache: CacheService = Depends(get_cache),
):
    """
    AI关键词提取

    使用MiniMax AI从案例文本中提取关键词

    需要JWT认证，且订阅等级需要支持 ai_summaries
    """
    # 订阅等级检查
    if not _check_subscription_feature(current_user["id"], "ai_summaries"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="关键词提取功能需要 Pro 或以上订阅计划",
        )
    try:
        # 服务已通过 Depends 注入
        case_data = await courtlistener.get_opinion_by_id(case_id)
        plain_text = case_data.get("plain_text", "")

        if not plain_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="案例文本为空，无法提取关键词",
            )

        # 检查缓存
        text_hash = hashlib.md5(plain_text.encode()).hexdigest()[:16]
        ai_cache = AIServiceCache(cache)
        cached_keywords = await ai_cache.get_cached_keywords(text_hash)

        if cached_keywords:
            logger.info(f"案例 {case_id} 关键词提取命中缓存")
            return KeywordsResponse(
                case_id=case_id,
                keywords=cached_keywords[:request_body.top_n],
                cached=True,
            )

        # 调用AI提取关键词
        keywords = await ai_router.extract_keywords(
            text=plain_text,
            top_n=request_body.top_n,
        )

        # 缓存结果
        await ai_cache.cache_keywords(text_hash, keywords)

        logger.info(f"案例 {case_id} 关键词提取完成")

        return KeywordsResponse(
            case_id=case_id,
            keywords=keywords[:request_body.top_n],
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
    request: Request,
    case_id: int,
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    current_user: dict = Depends(get_current_user),
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
):
    """
    查找相似案例

    基于向量相似度查找相似的法律案例

    需要JWT认证，且订阅等级需要支持 similar_cases
    """
    # 订阅等级检查
    if not _check_subscription_feature(current_user["id"], "similar_cases"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="相似案例功能需要 Pro 或以上订阅计划",
        )
    try:
        # 获取原案例信息用于构建查询
        cluster_data = await courtlistener.get_cluster_by_id(case_id)
        docket = cluster_data.get("docket", {})

        # 从案例名提取关键词（取前5个实词）
        case_name = cluster_data.get("case_name", "")
        import re
        words = re.findall(r'[A-Z][a-z]+|[A-Z]{2,}|[a-z]{4,}', case_name)
        # 过滤停用词，构建搜索查询
        stop_words = {"the", "and", "for", "with", "from", "that", "this", "v", "vs", "versus", "of", "in", "on", "at", "to", "by"}
        keywords = [w.lower() for w in words if len(w) > 2 and w.lower() not in stop_words][:5]

        if not keywords:
            keywords = [case_name[:20]] if case_name else ["legal case"]

        # 搜索相关案例（用 case name 的关键词 + 法院类型）
        query = " ".join(keywords)
        search_result = await courtlistener.search_opinions(
            query=query,
            court=cluster_data.get("court_id") or docket.get("court_id"),
            page_size=limit * 3,  # 多抓一些用于过滤
        )
        raw_results = search_result.get("results", [])

        # 构建结果并计算相似度分数
        similar_cases = []
        # 策略：CourtListener 搜索返回的结果本身就是相关的（按相关性排序）
        # 我们基于以下因素计算相似度：
        # 1. 搜索排名分数（如果有）
        # 2. 关键词重叠（放宽：支持 Unicode 字符、分词更宽泛）
        # 3. 法院匹配加成
        # 4. 搜索返回即有最低 0.4 分
        target_court = cluster_data.get("court_id") or docket.get("court_id")
        target_court_lower = (target_court or "").lower().replace(" ", "")

        for item in raw_results:
            # 跳过自身
            item_id = item.get("cluster_id") or item.get("id")
            if item_id == case_id:
                continue

            item_name = item.get("caseName") or item.get("case_name", "")
            item_court = item.get("court") or item.get("court_id") or ""
            item_court_lower = item_court.lower().replace(" ", "")

            # 基础分数：搜索返回即 0.4
            score = 0.4

            # 法院匹配加成
            if target_court_lower and item_court_lower:
                if target_court_lower in item_court_lower or item_court_lower in target_court_lower:
                    score += 0.15

            # 搜索排名加成（排在前面的更相似）
            rank = raw_results.index(item)
            score += max(0.15 - rank * 0.03, 0.0)

            # 案件名关键词重叠（用更宽泛的匹配）
            # 提取字母数字序列，支持 Unicode（支持重音字母等）
            item_words = set(re.findall(r"[\w\u00C0-\u024F]+", item_name, re.UNICODE))
            item_words_lower = {w.lower() for w in item_words if len(w) > 2}
            keyword_set = set(kw.lower() for kw in keywords)
            overlap = len(item_words_lower & keyword_set)
            if overlap > 0:
                # 重叠越多分数越高
                score += min(overlap * 0.1, 0.25)

            score = min(max(score, 0.0), 0.99)

            similar_cases.append(
                SimilarCaseItem(
                    id=item_id,
                    case_name=item_name or "Unknown Case",
                    court=item.get("court") or item.get("court_id"),
                    date_filed=item.get("dateFiled") or item.get("date_filed"),
                    similarity=round(score, 2),
                )
            )
            if len(similar_cases) >= limit:
                break

        # 如果搜索结果不够，用引用网络补充
        if len(similar_cases) < limit:
            citation_urn = f"cluster:{case_id}"
            try:
                cited_by = await courtlistener.get_citation_network("cited-by", citation_urn)
                for item in cited_by.get("results", []):
                    if len(similar_cases) >= limit:
                        break
                    citing_cluster = item.get("citing_cluster", item)
                    citing_id = citing_cluster.get("id")
                    if citing_id == case_id or any(sc.id == citing_id for sc in similar_cases):
                        continue
                    similar_cases.append(
                        SimilarCaseItem(
                            id=citing_id,
                            case_name=citing_cluster.get("case_name", "Unknown Case"),
                            court=citing_cluster.get("court"),
                            date_filed=citing_cluster.get("date_filed"),
                            similarity=0.75,
                        )
                    )
            except Exception:
                pass  # 引用网络不可用时继续使用搜索结果

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


@router.get(
    "/{case_id}",
    response_model=CaseDetailResponse,
    summary="获取案例详情",
    description="获取指定案例的详细信息",
)
async def get_case_detail(
    request: Request,
    case_id: int,
    current_user: Optional[dict] = Depends(get_optional_user),
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
):
    """获取案例详情"""
    # 验证 case_id
    if case_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="无效的案例ID",
        )
    try:
        # 服务已通过 Depends 注入
        # v4: 使用 cluster_id 获取案件详情，而不是 opinion_id
        cluster_data = await courtlistener.get_cluster_by_id(case_id)
        docket = cluster_data.get("docket", {})
        first_opinion = cluster_data.get("_first_opinion", {})

        # v4 citation: cluster 有 citations 字段，opinion 有 citation 字段
        # citations 格式: [{"volume": "31", "reporter": "F.4th", "page": "560"}]
        raw_citation = cluster_data.get("citations", []) or []
        if not raw_citation:
            raw_citation = first_opinion.get("citation", []) or []
        if isinstance(raw_citation, list) and len(raw_citation) > 0:
            if isinstance(raw_citation[0], dict):
                citation_parts = []
                for c in raw_citation:
                    vol = c.get("volume", "")
                    rep = c.get("reporter", "")
                    pg = c.get("page", "")
                    if vol and rep and pg:
                        citation_parts.append(f"{vol} {rep} {pg}")
                    elif rep and pg:
                        citation_parts.append(f"{rep} {pg}")
                citation_str = ", ".join(citation_parts)
            else:
                citation_str = ", ".join(str(c) for c in raw_citation if c)
        else:
            citation_str = ""

        # 解析JSON字段
        keywords = None
        entities = None

        if cluster_data.get("keywords"):
            try:
                keywords = json.loads(cluster_data["keywords"])
            except json.JSONDecodeError:
                keywords = [cluster_data["keywords"]]

        if cluster_data.get("entities"):
            try:
                entities = json.loads(cluster_data["entities"])
            except json.JSONDecodeError:
                entities = {}

        slug_url = build_slug_url(
            case_id=case_id,
            case_name=cluster_data.get("case_name", ""),
            court_id=cluster_data.get("court_id") or docket.get("court_id"),
            citation=citation_str,
        )
        return CaseDetailResponse(
            id=case_id,
            courtlistener_id=case_id,
            case_name=cluster_data.get("case_name", ""),
            case_name_full=cluster_data.get("case_name_full"),
            court=cluster_data.get("court") or docket.get("court_id", ""),
            court_id=cluster_data.get("court_id") or docket.get("court_id"),
            date_filed=cluster_data.get("date_filed"),
            date_decided=cluster_data.get("date_filed"),
            citation=citation_str or None,
            docket_number=cluster_data.get("docket_number") or docket.get("docket_number"),
            plain_text=first_opinion.get("plain_text"),
            html_text=first_opinion.get("html"),
            summary=cluster_data.get("summary"),
            keywords=keywords,
            entities=entities,
            created_at=datetime.utcnow(),
            source_url=f"https://www.courtlistener.com/case/{case_id}/",
            slug=slug_url.lstrip("/cases/"),
            slug_url=slug_url,
        )

    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        logger.error(f"CourtListener HTTP错误: {status_code} - {str(e)}")
        if status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="案例不存在",
            )
        elif status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试",
            )
        elif 400 <= status_code < 500:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"无法获取案例信息 (客户端错误: {status_code})",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="外部数据源暂时不可用，请稍后再试",
            )
    except Exception as e:
        logger.error(f"获取案例详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="外部数据源暂时不可用，请稍后再试",
        )


# ==================== 语义化URL端点 ====================
@router.get(
    "/by-slug/{slug:path}",
    response_model=CaseDetailResponse,
    summary="通过语义化URL获取案例",
    description="使用语义化URL获取案例详情",
)
async def get_case_by_slug(
    request: Request,
    slug: str,
    current_user: Optional[dict] = Depends(get_optional_user),
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
):
    """
    通过语义化URL获取案例详情

    slug格式: {country}/{type}/{slug_name}_{case_id}/
    示例: us/criminal/people-v-smith-123456789/

    注意：slug 主要用于SEO和用户友好URL，实际案例ID从slug末尾提取
    """
    slug_name, case_id = parse_slug(slug)

    if case_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无效的案例URL",
        )

    if case_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="无效的案例ID",
        )

    try:
        # v4: 使用 cluster_id 获取案件详情
        cluster_data = await courtlistener.get_cluster_by_id(case_id)
        docket = cluster_data.get("docket", {})
        first_opinion = cluster_data.get("_first_opinion", {})

        # v4 citation 是数组，优先从 cluster 的 citations 字段获取，其次从第一个意见获取
        # citations 格式: [{"volume": "31", "reporter": "F.4th", "page": "560"}]
        raw_citation = cluster_data.get("citations", []) or []
        if not raw_citation:
            raw_citation = first_opinion.get("citation", []) or []
        if isinstance(raw_citation, list) and len(raw_citation) > 0:
            # citations 是对象数组，转换为字符串
            if isinstance(raw_citation[0], dict):
                citation_parts = []
                for c in raw_citation:
                    vol = c.get("volume", "")
                    rep = c.get("reporter", "")
                    pg = c.get("page", "")
                    if vol and rep and pg:
                        citation_parts.append(f"{vol} {rep} {pg}")
                    elif rep and pg:
                        citation_parts.append(f"{rep} {pg}")
                citation_str = ", ".join(citation_parts)
            else:
                citation_str = ", ".join(str(c) for c in raw_citation if c)
        else:
            citation_str = ""

        keywords = None
        entities = None

        if cluster_data.get("keywords"):
            try:
                keywords = json.loads(cluster_data["keywords"])
            except json.JSONDecodeError:
                keywords = [cluster_data["keywords"]]

        if cluster_data.get("entities"):
            try:
                entities = json.loads(cluster_data["entities"])
            except json.JSONDecodeError:
                entities = {}

        slug_url = build_slug_url(
            case_id=case_id,
            case_name=cluster_data.get("case_name", ""),
            court_id=cluster_data.get("court_id") or docket.get("court_id"),
            citation=citation_str,
        )

        return CaseDetailResponse(
            id=case_id,
            courtlistener_id=case_id,
            case_name=cluster_data.get("case_name", ""),
            case_name_full=cluster_data.get("case_name_full"),
            court=cluster_data.get("court") or docket.get("court_id", ""),
            court_id=cluster_data.get("court_id") or docket.get("court_id"),
            date_filed=cluster_data.get("date_filed"),
            date_decided=cluster_data.get("date_filed"),
            citation=citation_str or None,
            docket_number=cluster_data.get("docket_number") or docket.get("docket_number"),
            plain_text=first_opinion.get("plain_text"),
            html_text=first_opinion.get("html"),
            summary=cluster_data.get("summary"),
            keywords=keywords,
            entities=entities,
            created_at=datetime.utcnow(),
            source_url=f"https://www.courtlistener.com/case/{case_id}/",
            slug=slug,
            slug_url=slug_url,
        )

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        logger.error(f"CourtListener HTTP错误: {status_code} - {str(e)}")
        if status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="案例不存在",
            )
        elif status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试",
            )
        elif 400 <= status_code < 500:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"无法获取案例信息 (客户端错误: {status_code})",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="外部数据源暂时不可用，请稍后再试",
            )
    except Exception as e:
        logger.error(f"获取案例详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="外部数据源暂时不可用，请稍后再试",
        )


# ==================== 翻译端点 ====================
@router.post(
    "/{case_id}/translate",
    response_model=TranslateResponse,
    summary="翻译案例",
    description="使用AI将案例文本翻译为目标语言",
)
async def translate_case(
    request: Request,
    case_id: int,
    request_body: TranslateRequest = TranslateRequest(),
    current_user: dict = Depends(get_current_user),
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
    ai_router: AIRouter = Depends(get_ai_router),
):
    """
    AI案例翻译

    使用MiniMax AI将案例文本翻译为目标语言

    需要JWT认证，且订阅等级需要支持 ai_summaries
    """
    # 订阅等级检查
    if not _check_subscription_feature(current_user["id"], "ai_summaries"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="翻译功能需要 Pro 或以上订阅计划",
        )
    try:
        # 服务已通过 Depends 注入
        # 获取案例文本
        case_data = await courtlistener.get_opinion_by_id(case_id)
        plain_text = case_data.get("plain_text", "")

        if not plain_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="案例文本为空，无法翻译",
            )

        # 调用AI翻译
        translated_text = await ai_router.translate_case(
            text=plain_text,
            target_language=request_body.target_language,
            source_language=request_body.source_language,
        )

        detected_source = request_body.source_language if request_body.source_language != "auto" else "detected"

        logger.info(f"案例 {case_id} 翻译完成 -> {request_body.target_language}")

        return TranslateResponse(
            case_id=case_id,
            translated_text=translated_text,
            source_language=detected_source,
            target_language=request_body.target_language,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"案例翻译失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"翻译服务错误: {str(e)}",
        )


# ==================== 文本整理端点 ====================
@router.post(
    "/{case_id}/format-text",
    response_model=FormatTextResponse,
    summary="整理案例文本格式",
    description="使用AI整理优化法律案例文本的格式，提高可读性（自动缓存）",
)
async def format_case_text(
    request: Request,
    case_id: int,
    current_user: Optional[dict] = Depends(get_optional_user),
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
    ai_router: AIRouter = Depends(get_ai_router),
    cache: CacheService = Depends(get_cache),
):
    """
    AI案例文本格式整理

    自动整理文本格式（换行、段落、章节标记、标点等），不改变原文内容。
    结果会被缓存，重复调用直接返回缓存。

    需要JWT认证，且订阅等级需要支持 ai_summaries
    """
    # 订阅等级检查
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录后才能使用文本整理功能",
        )
    if not _check_subscription_feature(current_user["id"], "ai_summaries"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="文本整理功能需要 Pro 或以上订阅计划",
        )
    try:
        # 获取案例文本
        cluster_data = await courtlistener.get_cluster_by_id(case_id)
        first_opinion = cluster_data.get("_first_opinion", {})
        plain_text = first_opinion.get("plain_text", "")

        if not plain_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="案例文本为空，无法整理",
            )

        # 检查缓存
        text_hash = hashlib.md5(plain_text.encode()).hexdigest()[:16]
        ai_cache = AIServiceCache(cache)
        cached_formatted = await ai_cache.get_cached_formatted_text(text_hash)

        if cached_formatted:
            logger.info(f"案例 {case_id} 文本整理命中缓存")
            return FormatTextResponse(
                case_id=case_id,
                plain_text_formatted=cached_formatted,
                cached=True,
            )

        # 调用AI整理文本
        formatted_text = await ai_router.format_text_case(text=plain_text)

        # 缓存结果
        await ai_cache.cache_formatted_text(text_hash, formatted_text)

        logger.info(f"案例 {case_id} 文本整理完成，长度: {len(formatted_text)}")

        return FormatTextResponse(
            case_id=case_id,
            plain_text_formatted=formatted_text,
            cached=False,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"案例文本整理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务错误: {str(e)}",
        )


# ==================== 分享链接端点 ====================
# 内存存储分享令牌（生产环境应使用 Redis/数据库）
_share_tokens: Dict[str, Dict[str, Any]] = {}
_SHARE_TOKEN_TTL = 86400  # 24 hours in seconds


def _cleanup_expired_share_tokens() -> int:
    """清理过期的分享令牌，返回清理数量"""
    import time
    now = time.time()
    expired = [token for token, data in _share_tokens.items()
               if now - data.get("created_at", 0) > _SHARE_TOKEN_TTL]
    for token in expired:
        del _share_tokens[token]
    return len(expired)


@router.post(
    "/share/create",
    response_model=ShareLinkResponse,
    summary="创建分享链接",
    description="为案例创建一次性公开分享链接",
)
async def create_share_link(
    case_id: int,
    current_user: dict = Depends(get_current_user),
):
    """创建分享链接"""
    import secrets

    # 创建前先清理过期令牌
    _cleanup_expired_share_tokens()

    token = secrets.token_urlsafe(24)
    _share_tokens[token] = {
        "case_id": case_id,
        "user_id": current_user["id"],
        "created_at": datetime.utcnow().timestamp(),
    }

    logger.info(f"用户 {current_user['id']} 为案例 {case_id} 创建分享链接")

    return ShareLinkResponse(
        share_url=f"/shared/{token}",
        token=token,
        expires_in=86400,
    )


@router.get(
    "/shared/{token}",
    response_model=SharedCaseResponse,
    summary="获取分享案例",
    description="通过分享令牌获取案例基本信息（公开访问）",
)
async def get_shared_case(
    request: Request,
    token: str,
    courtlistener: CourtListenerClient = Depends(get_courtlistener),
):
    """获取分享案例（无需登录）"""
    # 自动清理过期令牌
    _cleanup_expired_share_tokens()
    token_data = _share_tokens.get(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享链接无效或已过期",
        )

    # 检查令牌是否过期
    created_at = token_data.get("created_at", 0)
    import time
    if time.time() - created_at > _SHARE_TOKEN_TTL:
        # 清理过期令牌
        _share_tokens.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享链接已过期",
        )

    case_id = token_data["case_id"]

    try:
        # v4: 使用 cluster_id 获取案例信息
        cluster_data = await courtlistener.get_cluster_by_id(case_id)
        first_opinion = cluster_data.get("_first_opinion", {})
        # v4 citation 是数组，优先从 cluster 的 citations 字段获取，其次从第一个意见获取
        # citations 格式: [{"volume": "31", "reporter": "F.4th", "page": "560"}]
        raw_citation = cluster_data.get("citations", []) or []
        if not raw_citation:
            raw_citation = first_opinion.get("citation", []) or []
        if isinstance(raw_citation, list) and len(raw_citation) > 0:
            # citations 是对象数组，转换为字符串
            if isinstance(raw_citation[0], dict):
                citation_parts = []
                for c in raw_citation:
                    vol = c.get("volume", "")
                    rep = c.get("reporter", "")
                    pg = c.get("page", "")
                    if vol and rep and pg:
                        citation_parts.append(f"{vol} {rep} {pg}")
                    elif rep and pg:
                        citation_parts.append(f"{rep} {pg}")
                citation_str = ", ".join(citation_parts)
            else:
                citation_str = ", ".join(str(c) for c in raw_citation if c)
        else:
            citation_str = ""

        return SharedCaseResponse(
            case_name=cluster_data.get("case_name", ""),
            court=cluster_data.get("court"),
            date_filed=cluster_data.get("date_filed"),
            citation=citation_str or None,
            summary=cluster_data.get("summary"),
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分享链接无效或案例已不存在",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="外部数据源暂时不可用",
        )
    except Exception as e:
        logger.error(f"获取分享案例失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="外部数据源暂时不可用",
        )

