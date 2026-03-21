"""
推送相关 Schema
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PushConfigBase(BaseModel):
    name: str = Field(..., max_length=100)
    channel: str = Field(..., description="推送渠道：dingtalk/email")


class PushConfigCreate(PushConfigBase):
    webhook_url: Optional[str] = None
    secret: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class PushConfigUpdate(BaseModel):
    name: Optional[str] = None
    webhook_url: Optional[str] = None
    secret: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    enabled: Optional[int] = None
    notes: Optional[str] = None


class PushConfigResponse(PushConfigBase):
    id: int
    webhook_url: Optional[str] = None
    secret: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    enabled: int = 1
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class PushMessage(BaseModel):
    """推送消息"""
    title: str
    content: str
    type: Optional[str] = "info"  # info/success/warning/error
    url: Optional[str] = None  # 点击跳转链接
    at_mobiles: Optional[List[str]] = None  # @手机号


class PushHistory(BaseModel):
    """推送历史"""
    id: int
    config_id: int
    title: str
    content: str
    status: str  # success/failed
    error_msg: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
