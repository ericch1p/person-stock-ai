"""
K线数据 Schema
"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class KlineBase(BaseModel):
    code: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None


class KlineResponse(KlineBase):
    id: Optional[int] = None
    change_pct: Optional[float] = None
    adj_type: Optional[str] = "qfq"

    class Config:
        from_attributes = True


class KlineListResponse(BaseModel):
    total: int
    items: List[KlineResponse]


class KlineWithMa(KlineResponse):
    """带均线的K线"""
    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    ma120: Optional[float] = None
    ma250: Optional[float] = None


class KlineQuery(BaseModel):
    """K线查询参数"""
    code: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    adj_type: str = "qfq"
