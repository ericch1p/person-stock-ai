"""
策略相关 API
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from ..database import AsyncSessionLocal
from ..models import Strategy
from ..schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse, StrategyListResponse

router = APIRouter(prefix="/api/strategies", tags=["策略"])


@router.get("/", response_model=StrategyListResponse)
async def list_strategies(
    type: Optional[str] = Query(None, description="策略类型"),
    enabled_only: bool = Query(True),
    limit: int = Query(50, le=100)
):
    """获取策略列表"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        
        query = select(Strategy)
        if type:
            query = query.where(Strategy.type == type)
        if enabled_only:
            query = query.where(Strategy.enabled == 1)
        
        count_query = select(func.count()).select_from(Strategy)
        if type:
            count_query = count_query.where(Strategy.type == type)
        if enabled_only:
            count_query = count_query.where(Strategy.enabled == 1)
        
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        query = query.limit(limit)
        result = await session.execute(query)
        strategies = result.scalars().all()
        
        return {"total": total, "items": [StrategyResponse.model_validate(s) for s in strategies]}


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: int):
    """获取策略详情"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Strategy).where(Strategy.id == strategy_id))
        strategy = result.scalar_one_or_none()
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        return StrategyResponse.model_validate(strategy)


@router.post("/", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate):
    """创建策略"""
    async with AsyncSessionLocal() as session:
        db_strategy = Strategy(**strategy.model_dump())
        session.add(db_strategy)
        await session.commit()
        await session.refresh(db_strategy)
        return StrategyResponse.model_validate(db_strategy)


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: int, strategy: StrategyUpdate):
    """更新策略"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Strategy).where(Strategy.id == strategy_id))
        db_strategy = result.scalar_one_or_none()
        if not db_strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        update_data = strategy.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_strategy, key, value)
        
        await session.commit()
        await session.refresh(db_strategy)
        return StrategyResponse.model_validate(db_strategy)


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int):
    """删除策略"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Strategy).where(Strategy.id == strategy_id))
        db_strategy = result.scalar_one_or_none()
        if not db_strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        
        await session.delete(db_strategy)
        await session.commit()
        return {"success": True}
