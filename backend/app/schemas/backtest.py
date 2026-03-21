"""
回测相关 Schema
"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    """回测请求"""
    strategy_id: int
    codes: Optional[List[str]] = Field(None, description="回测股票列表，None表示全市场")
    start_date: date
    end_date: date
    initial_capital: float = Field(100000, description="初始资金")
    commission: float = Field(0.0003, description="手续费率")


class BacktestResultItem(BaseModel):
    """回测结果项"""
    code: str
    name: Optional[str] = None
    return_rate: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    sharpe: Optional[float] = None
    
    class Config:
        from_attributes = True


class BacktestResponse(BaseModel):
    """回测响应"""
    id: Optional[int] = None
    strategy_id: int
    start_date: date
    end_date: date
    
    # 总体收益
    total_return: float = Field(..., description="总收益率（%）")
    benchmark_return: float = Field(..., description="基准收益率（%）")
    excess_return: float = Field(..., description="超额收益率（%）")
    
    # 风险指标
    max_drawdown: float = Field(..., description="最大回撤（%）")
    sharpe: Optional[float] = Field(None, description="夏普比率")
    volatility: Optional[float] = Field(None, description="波动率（%）")
    
    # 交易统计
    total_trades: int
    win_trades: int
    loss_trades: int
    win_rate: float
    
    # 个股结果
    details: Optional[List[BacktestResultItem]] = None


class BacktestListResponse(BaseModel):
    total: int
    items: List[BacktestResponse]
