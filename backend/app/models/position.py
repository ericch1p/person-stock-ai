"""
持仓记录模型
"""
from sqlalchemy import Column, String, Date, Float, Integer, Text
from sqlalchemy.sql import func

from ..database import Base


class Position(Base):
    """持仓记录"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(50), nullable=True)
    
    # 交易信息
    buy_date = Column(Date, nullable=False, comment="买入日期")
    buy_price = Column(Float, nullable=False, comment="买入价格")
    quantity = Column(Integer, nullable=False, comment="买入数量（股）")
    buy_amount = Column(Float, nullable=True, comment="买入金额")
    
    # 卖出信息
    sell_date = Column(Date, nullable=True, comment="卖出日期")
    sell_price = Column(Float, nullable=True, comment="卖出价格")
    sell_amount = Column(Float, nullable=True, comment="卖出金额")
    
    # 持仓状态：open持仓/closed已平仓
    status = Column(String(20), default="open", index=True)
    
    # 关联
    watchlist_id = Column(Integer, nullable=True, comment="关联的跟踪记录ID")
    strategy_id = Column(Integer, nullable=True, comment="触发买入的策略ID")
    
    # 备注
    notes = Column(Text, nullable=True)
    
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Position {self.code} {self.status}>"
