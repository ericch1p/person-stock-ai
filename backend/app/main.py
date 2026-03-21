"""
FastAPI 主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .config import settings
from .database import init_db
from .routers import (
    stocks_router,
    selection_router,
    strategy_router,
    backtest_router,
    position_router,
    watchlist_router,
    trades_router,
    push_router,
)
from .tasks.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("启动A股智能选股系统...")
    
    # 初始化数据库
    await init_db()
    logger.info("数据库初始化完成")
    
    # 启动定时任务
    start_scheduler()
    logger.info("定时任务已启动")
    
    yield
    
    # 关闭时
    logger.info("关闭定时任务...")
    stop_scheduler()
    logger.info("系统已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A股股票筛选、跟踪、回测、优化的本地化系统",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stocks_router)
app.include_router(selection_router)
app.include_router(strategy_router)
app.include_router(backtest_router)
app.include_router(position_router)
app.include_router(watchlist_router)
app.include_router(trades_router)
app.include_router(push_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
