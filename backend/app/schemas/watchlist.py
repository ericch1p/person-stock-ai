"""
自选股 Schema
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import date


class WatchlistItem(BaseModel):
    """自选股项"""
    code: str
    name: Optional[str] = None
    status: str = "watch"  # watch/hold/sell/abandon
    strategy_id: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    
    class Config:
        from_attributes = True


class WatchlistResponse(BaseModel):
    """自选股列表响应"""
    total: int
    items: List[dict]
