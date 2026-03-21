#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import engine, Base
from app.models import (
    Stock, DailyKline, Financial, MoneyFlow,
    Watchlist, Position, Trade, Strategy,
    BacktestResult, PushConfig
)


async def init_database():
    """初始化数据库表"""
    print("正在创建数据库表...")
    
    async with engine.begin() as conn:
        # 删除所有表（谨慎使用）
        # await conn.run_sync(Base.metadata.drop_all)
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    
    print("数据库表创建完成！")
    
    # 显示创建的表
    print("\n已创建的表：")
    for table in Base.metadata.tables:
        print(f"  - {table}")


async def init_default_data():
    """初始化默认数据"""
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 添加默认策略
        default_strategies = [
            {
                "name": "均线金叉策略",
                "description": "MA5上穿MA20，适合趋势行情",
                "type": "technical",
                "params": {"ma_short": 5, "ma_long": 20},
                "enabled": 1
            },
            {
                "name": "MACD金叉策略",
                "description": "MACD在零轴上方形成金叉",
                "type": "technical",
                "params": {"fast": 12, "slow": 26, "signal": 9},
                "enabled": 1
            },
            {
                "name": "价值投资策略",
                "description": "低估值、高ROE的价值投资",
                "type": "fundamental",
                "params": {"pe_max": 30, "pb_max": 3, "roe_min": 10},
                "enabled": 1
            },
            {
                "name": "成长股策略",
                "description": "高增长的成长型股票",
                "type": "fundamental",
                "params": {"revenue_growth_min": 20, "net_profit_growth_min": 20},
                "enabled": 1
            }
        ]
        
        for strategy_data in default_strategies:
            strategy = Strategy(**strategy_data)
            session.add(strategy)
        
        await session.commit()
        print("默认策略创建完成！")


if __name__ == "__main__":
    print("=" * 50)
    print("A股智能选股系统 - 数据库初始化")
    print("=" * 50)
    
    asyncio.run(init_database())
    
    response = input("\n是否初始化默认数据？(y/n): ")
    if response.lower() == "y":
        asyncio.run(init_default_data())
    
    print("\n初始化完成！")
