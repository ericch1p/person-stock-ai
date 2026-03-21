"""
选股相关 API
"""
from datetime import date
from fastapi import APIRouter, HTTPException

from ..services.selection_service import SelectionService
from ..schemas.selection import SelectionCriteria, SelectionResult

router = APIRouter(prefix="/api/selection", tags=["选股"])
selection_service = SelectionService()


@router.post("/run")
async def run_selection(criteria: SelectionCriteria):
    """
    执行选股
    
    根据设定的条件筛选股票
    """
    try:
        # 转换 criteria 为 dict
        criteria_dict = criteria.model_dump(exclude_none=True)
        
        # 执行选股
        results = await selection_service.select_stocks(criteria_dict)
        
        return {
            "total": len(results),
            "date": date.today(),
            "criteria": criteria_dict,
            "items": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_selection_strategies():
    """
    获取预设选股策略
    
    返回常用的选股策略模板
    """
    return {
        "items": [
            {
                "id": "ma_golden",
                "name": "均线金叉策略",
                "description": "筛选MA5上穿MA20的股票",
                "criteria": {
                    "ma_golden_cross": True,
                    "exclude_st": True
                }
            },
            {
                "id": "value_stock",
                "name": "价值投资策略",
                "description": "筛选低估值、高ROE的优质股票",
                "criteria": {
                    "pe_min": 5,
                    "pe_max": 30,
                    "pb_max": 3,
                    "roe_min": 10,
                    "exclude_st": True
                }
            },
            {
                "id": "growth_stock",
                "name": "成长股策略",
                "description": "筛选高增长的成长型股票",
                "criteria": {
                    "revenue_growth_min": 20,
                    "net_profit_growth_min": 20,
                    "roe_min": 10,
                    "exclude_st": True
                }
            },
            {
                "id": "momentum",
                "name": "动量策略",
                "description": "筛选近期表现强势的股票",
                "criteria": {
                    "volume_breakout": True,
                    "ma_bullish_arrangement": True,
                    "exclude_st": True
                }
            }
        ]
    }
