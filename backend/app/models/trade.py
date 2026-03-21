"""
交易日志模型
"""
from sqlalchemy import Column, String, Date, Float, Integer, Text
from sqlalchemy.sql import func

from ..database import Base


class Trade(Base):
    """交易日志"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    
    # 交易动作：buy买入/sell卖出/hold持仓/adjust调整
    action = Column(String(20), nullable=False, index=True)
    
    # 股票信息
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(50), nullable=True)
    
    # 交易详情
    price = Column(Float, nullable=True, comment="交易价格")
    quantity = Column(Integer, nullable=True, comment="交易数量")
    amount = Column(Float, nullable=True, comment="交易金额")
    
    # 持仓信息
    position_id = Column(Integer, nullable=True, comment="关联持仓ID")
    
    # 关联策略
    strategy_id = Column(Integer, nullable=True, comment="关联策略ID")
    
    # 买入/卖出理由
    reason = Column(Text, nullable=True)
    
    # 当时的行情快照
    price_snapshot = Column(Text, nullable=True, comment="价格快照JSON")
    
    created_at = Column(Date, server_default=func.now())

    def __repr__(self):
        return f"<Trade {self.action} {self.code} {self.date}>"
