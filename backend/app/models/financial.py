"""
财务数据模型
"""
from sqlalchemy import Column, String, Date, Float, Integer
from sqlalchemy.sql import func

from ..database import Base


class Financial(Base):
    """财务指标数据"""
    __tablename__ = "financial"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True, comment="报告期")
    
    # 估值指标
    pe = Column(Float, nullable=True, comment="市盈率PE")
    pb = Column(Float, nullable=True, comment="市净率PB")
    ps = Column(Float, nullable=True, comment="市销率PS")
    
    # 盈利能力
    roe = Column(Float, nullable=True, comment="净资产收益率ROE（%）")
    gross_margin = Column(Float, nullable=True, comment="毛利率（%）")
    net_margin = Column(Float, nullable=True, comment="净利率（%）")
    
    # 成长能力
    revenue = Column(Float, nullable=True, comment="营业收入（万元）")
    revenue_growth = Column(Float, nullable=True, comment="营收增长率（%）")
    net_profit = Column(Float, nullable=True, comment="净利润（万元）")
    net_profit_growth = Column(Float, nullable=True, comment="净利润增长率（%）")
    
    # 运营能力
    total_asset = Column(Float, nullable=True, comment="总资产（万元）")
    total_asset_turnover = Column(Float, nullable=True, comment="资产周转率")
    
    # 财务风险
    debt_ratio = Column(Float, nullable=True, comment="资产负债率（%）")
    current_ratio = Column(Float, nullable=True, comment="流动比率")
    
    # 每股指标
    eps = Column(Float, nullable=True, comment="每股收益")
    bps = Column(Float, nullable=True, comment="每股净资产")
    
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Financial {self.code} {self.date}>"
