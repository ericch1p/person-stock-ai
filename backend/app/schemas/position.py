"""
持仓相关 Schema
"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class PositionBase(BaseModel):
    code: str = Field(..., max_length=10)
    name: Optional[str] = None


class PositionCreate(PositionBase):
    buy_date: date
    buy_price: float
    quantity: int
    notes: Optional[str] = None


class PositionUpdate(BaseModel):
    """更新持仓（卖出或调整）"""
    sell_date: Optional[date] = None
    sell_price: Optional[float] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class PositionResponse(PositionBase):
    id: int
    buy_date: date
    buy_price: float
    quantity: int
    buy_amount: Optional[float] = None
    sell_date: Optional[date] = None
    sell_price: Optional[float] = None
    sell_amount: Optional[float] = None
    status: str
    watchlist_id: Optional[int] = None
    strategy_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # 计算字段
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None

    class Config:
        from_attributes = True


class PositionListResponse(BaseModel):
    total: int
    items: List[PositionResponse]


class TradeLogBase(BaseModel):
    date: date
    action: str
    code: str
    name: Optional[str] = None


class TradeLogCreate(TradeLogBase):
    price: Optional[float] = None
    quantity: Optional[int] = None
    amount: Optional[float] = None
    position_id: Optional[int] = None
    strategy_id: Optional[int] = None
    reason: Optional[str] = None


class TradeLogResponse(TradeLogBase):
    id: int
    price: Optional[float] = None
    quantity: Optional[int] = None
    amount: Optional[float] = None
    position_id: Optional[int] = None
    strategy_id: Optional[int] = None
    reason: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class TradeLogListResponse(BaseModel):
    total: int
    items: List[TradeLogResponse]
