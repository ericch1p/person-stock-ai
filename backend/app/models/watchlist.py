"""
自选股/跟踪池模型
"""
from sqlalchemy import Column, String, Date, Integer, Text
from sqlalchemy.sql import func

from ..database import Base


class Watchlist(Base):
    """自选股/跟踪池"""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(50), nullable=True)
    
    # 状态：watch观察/hold持仓/sell已卖出/abandon放弃
    status = Column(String(20), default="watch", index=True)
    
    # 关联信息
    strategy_id = Column(Integer, nullable=True, comment="触发选股的策略ID")
    select_date = Column(Date, nullable=True, comment="选入日期")
    
    # 备注
    notes = Column(Text, nullable=True)
    
    # 标签
    tags = Column(String(200), nullable=True, comment="标签，逗号分隔")
    
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Watchlist {self.code} {self.status}>"
