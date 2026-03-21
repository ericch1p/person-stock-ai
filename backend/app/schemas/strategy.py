"""
策略相关 Schema
"""
from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StrategyBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    type: str = Field(..., description="策略类型：technical/fundamental/money/composite")


class StrategyCreate(StrategyBase):
    params: Optional[Dict[str, Any]] = None
    code: Optional[str] = None


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    enabled: Optional[int] = None


class StrategyResponse(StrategyBase):
    id: int
    params: Optional[Dict[str, Any]] = None
    enabled: int = 1
    code: Optional[str] = None
    score: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: int = 0
    valid_period: Optional[str] = None
    last_valid_date: Optional[date] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class StrategyListResponse(BaseModel):
    total: int
    items: List[StrategyResponse]
