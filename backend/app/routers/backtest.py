"""
回测相关 API
"""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from ..services.backtest_service import BacktestService
from ..schemas.backtest import BacktestRequest, BacktestResponse

router = APIRouter(prefix="/api/backtest", tags=["回测"])
backtest_service = BacktestService()


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    运行回测
    
    根据策略和日期区间执行回测
    """
    try:
        result = await backtest_service.run_backtest(
            strategy_id=request.strategy_id,
            codes=request.codes,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            commission=request.commission
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results")
async def get_backtest_results(
    strategy_id: Optional[int] = Query(None),
    limit: int = Query(50, le=100)
):
    """获取回测结果列表"""
    results = await backtest_service.get_backtest_results(strategy_id, limit)
    return {"total": len(results), "items": results}


@router.get("/results/{result_id}")
async def get_backtest_result(result_id: int):
    """获取回测结果详情"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from ..models import BacktestResult
        
        result = await session.execute(select(BacktestResult).where(BacktestResult.id == result_id))
        db_result = result.scalar_one_or_none()
        if not db_result:
            raise HTTPException(status_code=404, detail="回测结果不存在")
        
        return db_result
