"""
策略定义模型
"""
from sqlalchemy import Column, String, Date, Integer, Text, JSON, Float
from sqlalchemy.sql import func

from ..database import Base


class Strategy(Base):
    """选股策略定义"""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # 策略类型：technical技术面/fundamental基本面/money资金面/composite组合
    type = Column(String(50), nullable=False, index=True)
    
    # 策略参数（JSON格式）
    params = Column(JSON, nullable=True, comment="策略参数")
    
    # 状态：enabled启用/disabled禁用
    enabled = Column(Integer, default=1)
    
    # 策略代码（可选，用于存储策略表达式）
    code = Column(Text, nullable=True)
    
    # 评分
    score = Column(Float, nullable=True, comment="策略评分")
    win_rate = Column(Float, nullable=True, comment="历史胜率")
    total_trades = Column(Integer, default=0, comment="历史交易次数")
    
    # 有效期分析
    valid_period = Column(String(50), nullable=True, comment="有效周期")
    last_valid_date = Column(Date, nullable=True, comment="最近有效日期")
    
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Strategy {self.name}>"
