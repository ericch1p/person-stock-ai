"""
选股相关 Schema
"""
from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SelectionCriteria(BaseModel):
    """选股条件"""
    
    # 基础筛选
    market: Optional[List[str]] = Field(None, description="市场：沪市/深市/北交所")
    
    # 技术面条件
    ma_golden_cross: Optional[bool] = Field(None, description="均线金叉")
    ma_death_cross: Optional[bool] = Field(None, description="均线死叉")
    ma_bullish_arrangement: Optional[bool] = Field(None, description="均线多头排列")
    macd_golden_cross: Optional[bool] = Field(None, description="MACD金叉")
    macd_below_zero: Optional[bool] = Field(None, description="MACD水下金叉")
    volume_breakout: Optional[bool] = Field(None, description="放量突破")
    bollinger_breakout: Optional[bool] = Field(None, description="布林带突破")
    
    # 基本面条件
    pe_min: Optional[float] = Field(None, description="市盈率下限")
    pe_max: Optional[float] = Field(None, description="市盈率上限")
    pb_min: Optional[float] = Field(None, description="市净率下限")
    pb_max: Optional[float] = Field(None, description="市净率上限")
    roe_min: Optional[float] = Field(None, description="ROE下限（%）")
    revenue_growth_min: Optional[float] = Field(None, description="营收增速下限（%）")
    net_profit_growth_min: Optional[float] = Field(None, description="净利润增速下限（%）")
    
    # 资金面条件
    north_money_positive: Optional[bool] = Field(None, description="北向资金净流入")
    main_net_inflow_positive: Optional[bool] = Field(None, description="主力资金净流入")
    turnover_rate_min: Optional[float] = Field(None, description="换手率下限（%）")
    
    # 其他条件
    exclude_st: Optional[bool] = Field(True, description="排除ST股票")
    exclude_new_stock: Optional[bool] = Field(None, description="排除新股（上市不满一年）")


class SelectionResult(BaseModel):
    """选股结果"""
    code: str
    name: str
    industry: Optional[str] = None
    close: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[float] = None
    
    # 技术指标
    ma_status: Optional[str] = None
    macd_status: Optional[str] = None
    
    # 基本面
    pe: Optional[float] = None
    pb: Optional[float] = None
    roe: Optional[float] = None
    
    # 资金面
    north_money: Optional[float] = None
    main_net_inflow: Optional[float] = None
    
    # 匹配度
    match_score: Optional[float] = None
    match_reasons: Optional[List[str]] = None


class SelectionResponse(BaseModel):
    """选股响应"""
    total: int
    date: date
    criteria: SelectionCriteria