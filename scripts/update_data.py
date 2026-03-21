#!/usr/bin/env python3
"""
手动更新数据脚本
"""
import asyncio
import sys
from pathlib import Path
from datetime import date

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.data_service import DataService


async def update_all_data():
    """更新所有数据"""
    print("开始更新数据...")
    data_service = DataService()
    
    # 1. 更新股票列表
    print("\n[1/3] 更新股票列表...")
    count = await data_service.update_stock_list()
    print(f"  完成：{count} 只股票")
    
    # 2. 更新K线数据（限制数量避免超时）
    print("\n[2/3] 更新K线数据...")
    stock_list = await data_service.list_stocks(limit=5000)
    codes = [s["code"] for s in stock_list.get("items", [])]
    
    updated = 0
    failed = 0
    for i, code in enumerate(codes):
        try:
            result = await data_service.update_daily_kline(code)
            if result:
                updated += 1
        except Exception as e:
            failed += 1
            if failed <= 5:
                print(f"  失败：{code} - {e}")
        
        if (i + 1) % 100 == 0:
            print(f"  进度：{i + 1}/{len(codes)}")
    
    print(f"  完成：{updated} 只成功，{failed} 只失败")
    
    # 3. 更新财务数据（抽样）
    print("\n[3/3] 更新财务数据（抽样100只）...")
    financial_updated = 0
    for code in codes[:100]:
        try:
            result = await data_service.update_financial_data(code)
            if result:
                financial_updated += 1
        except Exception as e:
            pass
    
    print(f"  完成：{financial_updated} 只")
    
    print("\n数据更新完成！")


async def update_single_stock(code: str):
    """更新单个股票"""
    print(f"更新股票 {code} 的数据...")
    data_service = DataService()
    
    # 更新K线
    result1 = await data_service.update_daily_kline(code)
    print(f"  K线数据：{'成功' if result1 else '失败'}")
    
    # 更新财务
    result2 = await data_service.update_financial_data(code)
    print(f"  财务数据：{'成功' if result2 else '失败'}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = sys.argv[1]
        asyncio.run(update_single_stock(code))
    else:
        response = input("将更新大量数据，可能需要较长时间。是否继续？(y/n): ")
        if response.lower() == "y":
            asyncio.run(update_all_data())
