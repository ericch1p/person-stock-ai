"""
回测结果模型
"""
from sqlalchemy import Column, String, Date, Float, Integer, Text
from sqlalchemy.sql import func

from ..database import Base


class BacktestResult(Base):
    """回测结果"""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联
    strategy_id = Column(Integer, nullable=False, index=True)
    
    # 回测股票
    code = Column(String(10), nullable=True, index=True)
    name = Column(String(50), nullable=True)
    
    # 回测区间
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # 收益指标
    return_rate = Column(Float, nullable=True, comment="收益率（%）")
    benchmark_return = Column(Float, nullable=True, comment="基准收益率（%）")
    excess_return = Column(Float, nullable=True, comment="超额收益（%）")
    
    # 风险指标
    max_drawdown = Column(Float, nullable=True, comment="最大回撤（%）")
    volatility = Column(Float, nullable=True, comment="波动率（%）")
    sharpe = Column(Float, nullable=True, comment="夏普比率")
    
    # 交易统计
    total_trades = Column(Integer, default=0, comment="总交易次数")
    win_trades = Column(Integer, default=0, comment="盈利次数")
    loss_trades = Column(Integer, default=0, comment="亏损次数")
    win_rate = Column(Float, nullable=True, comment="胜率（%）")
    
    # 平均持仓
    avg_holding_days = Column(Float, nullable=True, comment="平均持仓天数")
    
    # 收益曲线数据
    equity_curve = Column(Text, nullable=True, comment="收益曲线JSON")
    
    # 备注
    notes = Column(Text, nullable=True)
    
    created_at = Column(Date, server_default=func.now())

    def __repr__(self):
        return f"<BacktestResult strategy={self.strategy_id} {self.start_date}~{self.end_date}>"
