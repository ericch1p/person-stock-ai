"""
定时任务调度器
"""
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from ..services.data_service import DataService
from ..services.push_service import PushService
from ..services.selection_service import SelectionService


# 创建调度器
scheduler = AsyncIOScheduler()


def start_scheduler():
    """启动定时任务"""
    
    # 每日收盘后更新数据（15:30执行）
    scheduler.add_job(
        update_daily_data,
        CronTrigger(hour=16, minute=0),
        id="update_daily_data",
        name="每日更新行情数据",
        replace_existing=True
    )
    
    # 每日收盘后选股（16:30执行）
    scheduler.add_job(
        run_daily_selection,
        CronTrigger(hour=16, minute=30),
        id="run_daily_selection",
        name="每日选股",
        replace_existing=True
    )
    
    # 每周一早上推送持仓报告（09:00执行）
    scheduler.add_job(
        send_weekly_report,
        CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="send_weekly_report",
        name="每周持仓报告",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止定时任务"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")


async def update_daily_data():
    """每日更新行情数据"""
    logger.info(f"开始更新每日数据: {datetime.now()}")
    
    try:
        data_service = DataService()
        
        # 更新股票列表
        count = await data_service.update_stock_list()
        logger.info(f"更新股票列表: {count} 只")
        
        # 获取所有股票代码
        stock_list = await data_service.list_stocks(limit=5000)
        codes = [s["code"] for s in stock_list.get("items", [])]
        
        # 批量更新K线数据（可以限制数量避免超时）
        updated = 0
        for code in codes[:500]:  # 每次最多更新500只
            try:
                result = await data_service.update_daily_kline(code)
                if result:
                    updated += 1
            except Exception as e:
                logger.error(f"更新K线失败 {code}: {e}")
                continue
        
        logger.info(f"更新K线数据完成: {updated}/{len(codes)} 只")
        
    except Exception as e:
        logger.error(f"更新数据任务失败: {e}")


async def run_daily_selection():
    """每日选股并推送"""
    logger.info(f"开始每日选股: {datetime.now()}")
    
    try:
        selection_service = SelectionService()
        push_service = PushService()
        
        # 使用默认策略选股
        criteria = {
            "exclude_st": True,
            "ma_golden_cross": True,
        }
        
        results = await selection_service.select_stocks(criteria)
        logger.info(f"选股完成: {len(results)} 只符合条件")
        
        # 推送到钉钉
        configs = await push_service.list_configs()
        for config in configs:
            if config.get("channel") == "dingtalk":
                await push_service.push_selection_result(config["id"], results)
                logger.info(f"已推送选股结果到 {config['name']}")
        
    except Exception as e:
        logger.error(f"每日选股任务失败: {e}")


async def send_weekly_report():
    """发送每周持仓报告"""
    logger.info(f"开始发送每周报告: {datetime.now()}")
    
    try:
        push_service = PushService()
        
        # 构建报告数据
        report_data = {
            "positions": [],  # TODO: 从数据库获取持仓
            "watchlist": [],  # TODO: 从数据库获取自选股
        }
        
        # 推送到钉钉
        configs = await push_service.list_configs()
        for config in configs:
            if config.get("channel") == "dingtalk":
                await push_service.push_daily_report(config["id"], report_data)
                logger.info(f"已发送每周报告到 {config['name']}")
        
    except Exception as e:
        logger.error(f"发送每周报告失败: {e}")
