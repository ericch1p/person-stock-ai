"""
资金流向模型
"""
from sqlalchemy import Column, String, Date, Float, Integer
from sqlalchemy.sql import func

from ..database import Base


class MoneyFlow(Base):
    """资金流向数据"""
    __tablename__ = "money_flow"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # 资金流向
    north_money = Column(Float, nullable=True, comment="北向资金（万元）")
    south_money = Column(Float, nullable=True, comment="南向资金（万元）")
    
    # 主力资金
    main_net_inflow = Column(Float, nullable=True, comment="主力净流入（万元）")
    main_inflow = Column(Float, nullable=True, comment="主力流入（万元）")
    main_outflow = Column(Float, nullable=True, comment="主力流出（万元）")
    
    # 超大单
    big_net_inflow = Column(Float, nullable=True, comment="超大单净流入（万元）")
    big_inflow = Column(Float, nullable=True, comment="超大单流入（万元）")
    big_outflow = Column(Float, nullable=True, comment="超大单流出（万元）")
    
    # 大单
    large_net_inflow = Column(Float, nullable=True, comment="大单净流入（万元）")
    large_inflow = Column(Float, nullable=True, comment="大单流入（万元）")
    large_outflow = Column(Float, nullable=True, comment="大单流出（万元）")
    
    # 中单
    mid_net_inflow = Column(Float, nullable=True, comment="中单净流入（万元）")
    
    # 小单
    small_net_inflow = Column(Float, nullable=True, comment="小单净流入（万元）")
    
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<MoneyFlow {self.code} {self.date}>"
