"""
自选股管理 API
"""
from typing import Optional
from fastapi import APIRouter, Query

from ..services.data_service import DataService
from ..schemas.watchlist import WatchlistItem, WatchlistResponse

router = APIRouter(prefix="/api/watchlist", tags=["自选股"])
data_service = DataService()


@router.get("/", response_model=WatchlistResponse)
async def get_watchlist(
    status: Optional[str] = Query(None, description="状态筛选"),
    limit: int = Query(100, le=500),
    offset: int = Query(0)
):
    """获取自选股列表"""
    return await data_service.get_watchlist(status, limit, offset)


@router.post("/")
async def add_to_watchlist(item: WatchlistItem):
    """添加自选股"""
    return await data_service.add_to_watchlist(item)


@router.post("/sync")
async def sync_watchlist_data():
    """同步自选股数据（K线+实时行情）"""
    return await data_service.sync_watchlist_data()


@router.delete("/{code}")
async def remove_from_watchlist(code: str):
    """删除自选股"""
    return await data_service.remove_from_watchlist(code)


@router.put("/{code}")
async def update_watchlist(code: str, item: WatchlistItem):
    """更新自选股"""
    return await data_service.update_watchlist(code, item)
