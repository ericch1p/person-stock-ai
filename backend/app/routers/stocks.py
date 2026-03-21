"""
股票相关 API
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Query

from ..services.data_service import DataService
from ..schemas.stock import StockResponse, StockListResponse

router = APIRouter(prefix="/api/stocks", tags=["股票"])
data_service = DataService()


@router.get("/", response_model=StockListResponse)
async def list_stocks(
    market: Optional[str] = Query(None, description="市场：沪市/深市/北交所"),
    industry: Optional[str] = Query(None, description="行业"),
    status: Optional[int] = Query(1, description="状态：1正常 0停牌"),
    limit: int = Query(100, le=500),
    offset: int = Query(0)
):
    """获取股票列表"""
    return await data_service.list_stocks(market, industry, status, limit, offset)


@router.get("/{code}", response_model=StockResponse)
async def get_stock(code: str):
    """获取股票详情"""
    info = await data_service.get_stock_info(code)
    if not info:
        return {"error": "股票不存在"}
    return info


@router.get("/{code}/kline")
async def get_stock_kline(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: int = Query(100, le=500)
):
    """获取股票K线数据"""
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    return await data_service.get_kline(code, start, end, limit)


@router.get("/{code}/realtime")
async def get_stock_realtime(code: str):
    """获取股票实时行情"""
    return await data_service.get_realtime_quote(code)


@router.post("/{code}/update")
async def update_stock_data(code: str):
    """更新股票数据"""
    result = await data_service.update_daily_kline(code)
    return {"success": result, "code": code}


@router.post("/update-all")
async def update_all_stocks():
    """更新所有股票列表"""
    count = await data_service.update_stock_list()
    return {"success": True, "count": count}


@router.post("/realtime")
async def get_realtime_quotes(codes: list[str]):
    """批量获取实时行情"""
    return await data_service.get_realtime_quote(codes)
