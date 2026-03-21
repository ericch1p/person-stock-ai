"""
推送相关 API
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from ..database import AsyncSessionLocal
from ..services.push_service import PushService
from ..schemas.push import PushConfigCreate, PushConfigUpdate, PushConfigResponse

router = APIRouter(prefix="/api/push", tags=["推送"])
push_service = PushService()


@router.get("/configs")
async def list_configs(enabled_only: bool = Query(True)):
    """获取推送配置列表"""
    configs = await push_service.list_configs(enabled_only)
    return {"total": len(configs), "items": configs}


@router.post("/configs", response_model=PushConfigResponse)
async def create_config(config: PushConfigCreate):
    """创建推送配置"""
    db_config = await push_service.save_config(config.model_dump())
    return PushConfigResponse.model_validate(db_config)


@router.put("/configs/{config_id}", response_model=PushConfigResponse)
async def update_config(config_id: int, config: PushConfigUpdate):
    """更新推送配置"""
    config_dict = config.model_dump(exclude_unset=True)
    config_dict["id"] = config_id
    db_config = await push_service.save_config(config_dict)
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return PushConfigResponse.model_validate(db_config)


@router.delete("/configs/{config_id}")
async def delete_config(config_id: int):
    """删除推送配置"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from ..models import PushConfig
        
        result = await session.execute(select(PushConfig).where(PushConfig.id == config_id))
        config = result.scalar_one_or_none()
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        await session.delete(config)
        await session.commit()
        return {"success": True}


