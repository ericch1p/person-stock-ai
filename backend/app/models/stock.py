"""
股票基础信息模型
"""
from sqlalchemy import Column, String, Date, Integer, Float
from sqlalchemy.sql import func

from ..database import Base


class Stock(Base):
    """股票基础信息"""
    __tablename__ = "stocks"

    code = Column(String(10), primary_key=True, index=True, comment="股票代码")
    name = Column(String(50), nullable=False, index=True, comment="股票名称")
    industry = Column(String(50), nullable=True, index=True, comment="所属行业")
    market = Column(String(20), nullable=True, comment="市场（沪市/深市/北交所）")
    list_date = Column(Date, nullable=True, comment="上市日期")
    status = Column(Integer, default=1, comment="状态：1正常 0停牌 9退市")
    
    # 扩展字段
    total_shares = Column(Float, nullable=True, comment="总股本（万股）")
    float_shares = Column(Float, nullable=True, comment="流通股本（万股）")
    
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Stock {self.code} {self.name}>"
