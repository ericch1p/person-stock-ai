#!/usr/bin/env python
from app.database import init_db
import asyncio
import os

# 删除旧数据库
if os.path.exists('data.db'):
    os.remove('data.db')
    print("已删除旧数据库")

# 初始化
asyncio.run(init_db())
print("数据库初始化完成")

# 检查表
from app.database import engine
from sqlalchemy import text
async def check_tables():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"已创建的表: {tables}")
asyncio.run(check_tables())
