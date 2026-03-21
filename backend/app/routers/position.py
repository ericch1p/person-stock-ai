"""
持仓/跟踪相关 API
"""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from ..database import AsyncSessionLocal
from ..models import Position, Watchlist, Trade
from ..schemas.position import (
    PositionCreate, PositionUpdate, PositionResponse, PositionListResponse,
    TradeLogCreate, TradeLogResponse, TradeLogListResponse
)

router = APIRouter(prefix="/api/positions", tags=["持仓"])


@router.get("/", response_model=PositionListResponse)
async def list_positions(
    status: Optional[str] = Query(None, description="持仓状态：open/closed"),
    limit: int = Query(100),
    offset: int = Query(0)
):
    """获取持仓列表"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        
        query = select(Position)
        if status:
            query = query.where(Position.status == status)
        
        count_query = select(func.count())
        if status:
            count_query = count_query.where(Position.status == status)
        
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        positions = result.scalars().all()
        
        return {"total": total, "items": [PositionResponse.model_validate(p) for p in positions]}


@router.post("/", response_model=PositionResponse)
async def create_position(position: PositionCreate):
    """创建持仓（买入）"""
    async with AsyncSessionLocal() as session:
        db_position = Position(
            code=position.code,
            name=position.name,
            buy_date=position.buy_date,
            buy_price=position.buy_price,
            quantity=position.quantity,
            buy_amount=position.buy_price * position.quantity,
            status="open",
            notes=position.notes
        )
        session.add(db_position)
        await session.commit()
        await session.refresh(db_position)
        
        # 创建交易日志
        trade = Trade(
            date=position.buy_date,
            action="buy",
            code=position.code,
            name=position.name,
            price=position.buy_price,
            quantity=position.quantity,
            amount=position.buy_price * position.quantity,
            position_id=db_position.id,
            reason=position.notes
        )
        session.add(trade)
        await session.commit()
        
        return PositionResponse.model_validate(db_position)


@router.put("/{position_id}", response_model=PositionResponse)
async def update_position(position_id: int, update: PositionUpdate):
    """更新持仓（卖出/调整）"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Position).where(Position.id == position_id))
        db_position = result.scalar_one_or_none()
        if not db_position:
            raise HTTPException(status_code=404, detail="持仓不存在")
        
        update_data = update.model_dump(exclude_unset=True)
        
        # 如果是卖出
        if update_data.get("sell_price") and update_data.get("sell_date"):
            db_position.sell_price = update_data["sell_price"]
            db_position.sell_date = update_data["sell_date"]
            db_position.sell_amount = db_position.quantity * update_data["sell_price"]
            db_position.status = "closed"
            
            # 创建卖出交易日志
            trade = Trade(
                date=update_data["sell_date"],
                action="sell",
                code=db_position.code,
                name=db_position.name,
                price=update_data["sell_price"],
                quantity=db_position.quantity,
                amount=db_position.quantity * update_data["sell_price"],
                position_id=db_position.id,
                reason=update_data.get("notes")
            )
            session.add(trade)
        
        # 其他更新
        for key, value in update_data.items():
            if key not in ["sell_price", "sell_date"]:
                setattr(db_position, key, value)
        
        await session.commit()
        await session.refresh(db_position)
        return PositionResponse.model_validate(db_position)


# ========== 自选股/跟踪池 ==========

watchlist_router = APIRouter(prefix="/api/watchlist", tags=["自选股"])


@watchlist_router.get("/", response_model=dict)
async def list_watchlist(
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0)
):
    """获取自选股列表"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        
        query = select(Watchlist)
        if status:
            query = query.where(Watchlist.status == status)
        
        count_query = select(func.count())
        if status:
            count_query = count_query.where(Watchlist.status == status)
        
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        items = result.scalars().all()
        
        return {"total": total, "items": [
            {"id": w.id, "code": w.code, "name": w.name, "status": w.status,
             "select_date": w.select_date, "notes": w.notes, "tags": w.tags}
            for w in items
        ]}


@watchlist_router.post("/")
async def add_to_watchlist(data: dict):
    """添加自选股"""
    async with AsyncSessionLocal() as session:
        watchlist = Watchlist(
            code=data["code"],
            name=data.get("name"),
            status=data.get("status", "watch"),
            strategy_id=data.get("strategy_id"),
            select_date=data.get("select_date"),
            notes=data.get("notes"),
            tags=data.get("tags")
        )
        session.add(watchlist)
        await session.commit()
        await session.refresh(watchlist)
        return {"id": watchlist.id, "success": True}


# ========== 交易日志 ==========

trades_router = APIRouter(prefix="/api/trades", tags=["交易日志"])


@trades_router.get("/", response_model=TradeLogListResponse)
async def list_trades(
    code: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(100),
    offset: int = Query(0)
):
    """获取交易日志"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        
        query = select(Trade)
        if code:
            query = query.where(Trade.code == code)
        if action:
            query = query.where(Trade.action == action)
        
        count_query = select(func.count())
        if code:
            count_query = count_query.where(Trade.code == code)
        if action:
            count_query = count_query.where(Trade.action == action)
        
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(Trade.date.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        trades = result.scalars().all()
        
        return {"total": total, "items": [TradeLogResponse.model_validate(t) for t in trades]}
