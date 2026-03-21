"""
Search API Routes

搜索历史、收藏夹相关API
"""

import json
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.api.auth import get_current_user
from app.api.cases import CaseSearchResult

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== Database Model Simulation ====================
# TODO: 后续集成真实数据库
# 这里使用模拟数据，实际项目中需要替换为数据库操作

FAKE_SEARCH_HISTORY = {}
FAKE_FAVORITES = {}


# ==================== Pydantic Models ====================

class SearchHistoryItem(BaseModel):
    """搜索历史项"""
    id: int
    query: str
    filters: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class SearchHistoryListResponse(BaseModel):
    """搜索历史列表响应"""
    total: int
    items: List[SearchHistoryItem]


class FavoriteCaseItem(BaseModel):
    """收藏案例项"""
    id: int
    case_id: int
    case_name: str
    court: Optional[str]
    date_filed: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    """收藏列表响应"""
    total: int
    items: List[FavoriteCaseItem]


class AddFavoriteRequest(BaseModel):
    """添加收藏请求"""
    case_id: int = Field(..., description="案例ID")
    case_name: str = Field(..., description="案例名称")
    court: Optional[str] = Field(None, description="法院")
    date_filed: Optional[datetime] = Field(None, description="立案日期")


class FavoriteResponse(BaseModel):
    """收藏响应"""
    id: int
    case_id: int
    message: str = "收藏成功"


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True


# ==================== API Routes ====================

@router.get(
    "/history",
    response_model=SearchHistoryListResponse,
    summary="获取搜索历史",
    description="获取当前用户的搜索历史记录",
)
async def get_search_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
):
    """
    获取搜索历史

    返回当前用户的搜索历史记录列表，按时间倒序排列

    需要JWT认证
    """
    user_id = current_user["id"]

    # TODO: 替换为数据库查询
    # 获取用户搜索历史
    user_history = [
        item for item in FAKE_SEARCH_HISTORY.values()
        if item.get("user_id") == user_id
    ]

    # 分页处理
    total = len(user_history)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_history = user_history[start:end]

    items = [
        SearchHistoryItem(
            id=item["id"],
            query=item["query"],
            filters=json.loads(item["filters"]) if item.get("filters") else None,
            created_at=item["created_at"],
        )
        for item in paginated_history
    ]

    logger.info(f"用户 {current_user['email']} 获取搜索历史: {total} 条")

    return SearchHistoryListResponse(total=total, items=items)


@router.delete(
    "/history/{history_id}",
    response_model=MessageResponse,
    summary="删除搜索历史",
    description="删除指定的搜索历史记录",
)
async def delete_search_history(
    history_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    删除搜索历史

    删除指定ID的搜索历史记录

    需要JWT认证
    """
    user_id = current_user["id"]

    # TODO: 替换为数据库操作
    if history_id not in FAKE_SEARCH_HISTORY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="搜索历史记录不存在",
        )

    history_item = FAKE_SEARCH_HISTORY[history_id]
    if history_item.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此记录",
        )

    del FAKE_SEARCH_HISTORY[history_id]

    logger.info(f"用户 {current_user['email']} 删除搜索历史: {history_id}")

    return MessageResponse(message="删除成功")


@router.delete(
    "/history",
    response_model=MessageResponse,
    summary="清空搜索历史",
    description="清空当前用户的所有搜索历史",
)
async def clear_search_history(
    current_user: dict = Depends(get_current_user),
):
    """
    清空搜索历史

    删除当前用户的所有搜索历史记录

    需要JWT认证
    """
    user_id = current_user["id"]

    # TODO: 替换为数据库操作
    to_delete = [
        item["id"] for item in FAKE_SEARCH_HISTORY.values()
        if item.get("user_id") == user_id
    ]

    for item_id in to_delete:
        if item_id in FAKE_SEARCH_HISTORY:
            del FAKE_SEARCH_HISTORY[item_id]

    logger.info(f"用户 {current_user['email']} 清空搜索历史: {len(to_delete)} 条")

    return MessageResponse(message=f"已清空 {len(to_delete)} 条搜索历史")


@router.get(
    "/favorites",
    response_model=FavoriteListResponse,
    summary="获取收藏列表",
    description="获取当前用户的收藏案例列表",
)
async def get_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
):
    """
    获取收藏列表

    返回当前用户收藏的案例列表

    需要JWT认证
    """
    user_id = current_user["id"]

    # TODO: 替换为数据库查询
    # 获取用户收藏
    user_favorites = [
        item for item in FAKE_FAVORITES.values()
        if item.get("user_id") == user_id
    ]

    # 分页处理
    total = len(user_favorites)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_favorites = user_favorites[start:end]

    items = [
        FavoriteCaseItem(
            id=item["id"],
            case_id=item["case_id"],
            case_name=item["case_name"],
            court=item.get("court"),
            date_filed=item.get("date_filed"),
            created_at=item["created_at"],
        )
        for item in paginated_favorites
    ]

    logger.info(f"用户 {current_user['email']} 获取收藏列表: {total} 条")

    return FavoriteListResponse(total=total, items=items)


@router.post(
    "/favorites",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="添加收藏",
    description="添加案例到收藏夹",
)
async def add_favorite(
    request: AddFavoriteRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    添加收藏

    将案例添加到用户收藏夹

    需要JWT认证
    """
    user_id = current_user["id"]

    # TODO: 替换为数据库操作
    # 检查是否已收藏
    for item in FAKE_FAVORITES.values():
        if item.get("user_id") == user_id and item.get("case_id") == request.case_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该案例已在收藏夹中",
            )

    # 创建收藏记录
    favorite_id = len(FAKE_FAVORITES) + 1
    new_favorite = {
        "id": favorite_id,
        "user_id": user_id,
        "case_id": request.case_id,
        "case_name": request.case_name,
        "court": request.court,
        "date_filed": request.date_filed,
        "created_at": datetime.utcnow(),
    }

    FAKE_FAVORITES[favorite_id] = new_favorite

    logger.info(f"用户 {current_user['email']} 添加收藏: 案例 {request.case_id}")

    return FavoriteResponse(
        id=favorite_id,
        case_id=request.case_id,
        message="收藏成功",
    )


@router.delete(
    "/favorites/{favorite_id}",
    response_model=MessageResponse,
    summary="删除收藏",
    description="从收藏夹删除指定案例",
)
async def delete_favorite(
    favorite_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    删除收藏

    从收藏夹中删除指定案例

    需要JWT认证
    """
    user_id = current_user["id"]

    # TODO: 替换为数据库操作
    if favorite_id not in FAKE_FAVORITES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏记录不存在",
        )

    favorite_item = FAKE_FAVORITES[favorite_id]
    if favorite_item.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此收藏",
        )

    del FAKE_FAVORITES[favorite_id]

    logger.info(f"用户 {current_user['email']} 删除收藏: {favorite_id}")

    return MessageResponse(message="删除成功")


@router.delete(
    "/favorites",
    response_model=MessageResponse,
    summary="清空收藏夹",
    description="清空当前用户的所有收藏",
)
async def clear_favorites(
    current_user: dict = Depends(get_current_user),
):
    """
    清空收藏夹

    删除当前用户的所有收藏记录

    需要JWT认证
    """
    user_id = current_user["id"]

    # TODO: 替换为数据库操作
    to_delete = [
        item["id"] for item in FAKE_FAVORITES.values()
        if item.get("user_id") == user_id
    ]

    for item_id in to_delete:
        if item_id in FAKE_FAVORITES:
            del FAKE_FAVORITES[item_id]

    logger.info(f"用户 {current_user['email']} 清空收藏夹: {len(to_delete)} 条")

    return MessageResponse(message=f"已清空 {len(to_delete)} 条收藏")


@router.get(
    "/favorites/check/{case_id}",
    summary="检查收藏状态",
    description="检查指定案例是否已收藏",
)
async def check_favorite(
    case_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    检查收藏状态

    检查指定案例是否在用户收藏夹中

    需要JWT认证
    """
    user_id = current_user["id"]

    # TODO: 替换为数据库查询
    is_favorited = any(
        item.get("user_id") == user_id and item.get("case_id") == case_id
        for item in FAKE_FAVORITES.values()
    )

    favorite_id = None
    if is_favorited:
        for item in FAKE_FAVORITES.values():
            if item.get("user_id") == user_id and item.get("case_id") == case_id:
                favorite_id = item["id"]
                break

    return {
        "case_id": case_id,
        "is_favorited": is_favorited,
        "favorite_id": favorite_id,
    }
