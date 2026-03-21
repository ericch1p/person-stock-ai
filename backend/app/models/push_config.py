"""
推送配置模型
"""
from sqlalchemy import Column, String, Integer, Text, JSON
from sqlalchemy.sql import func

from ..database import Base


class PushConfig(Base):
    """推送配置"""
    __tablename__ = "push_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="配置名称")
    
    # 推送渠道：dingtalk钉钉/email邮件
    channel = Column(String(50), nullable=False)
    
    # Webhook地址
    webhook_url = Column(String(500), nullable=True)
    
    # 密钥（钉钉签名用）
    secret = Column(String(200), nullable=True)
    
    # 推送规则（JSON格式）
    rules = Column(JSON, nullable=True, comment="推送规则")
    
    # 状态
    enabled = Column(Integer, default=1)
    
    # 备注
    notes = Column(Text, nullable=True)
    
    created_at = Column(String(50), server_default=func.now())
    updated_at = Column(String(50), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PushConfig {self.name} {self.channel}>"
