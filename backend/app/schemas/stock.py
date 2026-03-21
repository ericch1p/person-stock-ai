"""
股票相关 Schema
"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class StockBase(BaseModel):
    code: str = Field(..., max_length=10, description="股票代码")
    name: str = Field(..., max_length=50, description="股票名称")
    industry: Optional[str] = Field(None, max_length=50, description="所属行业")
    market: Optional[str] = Field(None, max_length=20, description="市场")


class StockCreate(StockBase):
    list_date: Optional[date] = None


class StockUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None
    status: Optional[int] = None


class StockResponse(StockBase):
    id: Optional[int] = None
    list_date: Optional[date] = None
    status: int = 1
    total_shares: Optional[float] = None
    float_shares: Optional[float] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True


class StockListResponse(BaseModel):
    total: int
    items: List[StockResponse]


class StockSimple(BaseModel):
    """简化股票信息"""
    code: str
    name: str
    close: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[float] = None

    class Config:
        from_attributes = True
