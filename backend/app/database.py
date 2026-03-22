"""
数据库连接模块
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 同步引擎（用于初始化等场景）
sync_engine = create_engine(
    settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite"),
    echo=settings.DATABASE_ECHO
)

SyncSessionLocal = sessionmaker(bind=sync_engine)

Base = declarative_base()


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    # 导入所有模型以确保它们被注册到Base.metadata
    from .models import (
        Stock, DailyKline, Financial, MoneyFlow, 
        Watchlist, Position, Trade, Strategy, 
        BacktestResult, PushConfig
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
