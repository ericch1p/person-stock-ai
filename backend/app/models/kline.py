"""
日线行情模型
"""
from sqlalchemy import Column, String, Date, Float, Integer
from sqlalchemy.sql import func

from ..database import Base


class DailyKline(Base):
    """日线行情数据"""
    __tablename__ = "daily_kline"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # OHLCV
    open = Column(Float, nullable=False, comment="开盘价")
    high = Column(Float, nullable=False, comment="最高价")
    low = Column(Float, nullable=False, comment="最低价")
    close = Column(Float, nullable=False, comment="收盘价")
    volume = Column(Float, nullable=False, comment="成交量（手）")
    amount = Column(Float, nullable=True, comment="成交额（元）")
    
    # 涨跌
    change_pct = Column(Float, nullable=True, comment="涨跌幅（%）")
    
    # 复权标记
    adj_type = Column(String(10), default="qfq", comment="复权类型：qfq前复权 hf后复权 None不复权")
    
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # 联合唯一索引：每个股票每天只有一条K线数据
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<DailyKline {self.code} {self.date}>"
