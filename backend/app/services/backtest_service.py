"""
回测服务 - 实现策略回测功能
"""
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
import json

from ..database import AsyncSessionLocal
from ..models import BacktestResult, Strategy, DailyKline
from .data_service import DataService


class BacktestService:
    """回测服务"""
    
    def __init__(self):
        self.data_service = DataService()
    
    async def run_backtest(
        self, 
        strategy_id: int,
        codes: Optional[List[str]] = None,
        start_date: date = None,
        end_date: date = None,
        initial_capital: float = 100000,
        commission: float = 0.0003
    ) -> Dict:
        """
        运行回测
        
        Args:
            strategy_id: 策略ID
            codes: 回测股票列表，None表示所有
            start_date: 回测开始日期
            end_date: 回测结束日期
            initial_capital: 初始资金
            commission: 手续费率
        """
        # 默认回测区间：最近一年
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        # 获取策略
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Strategy).where(Strategy.id == strategy_id)
            )
            strategy = result.scalar_one_or_none()
            if not strategy:
                return {"error": "策略不存在"}
        
        # 获取回测股票
        if not codes:
            stock_list = await self.data_service.list_stocks(limit=500)
            codes = [s["code"] for s in stock_list.get("items", [])]
        
        # 逐个股票回测
        results = []
        total_return = 0
        total_win = 0
        total_loss = 0
        equity_curve = []
        
        for code in codes[:100]:  # 限制数量
            try:
                result = await self._backtest_single(
                    code, start_date, end_date, initial_capital / len(codes), commission
                )
                if result:
                    results.append(result)
                    total_return += result["return_rate"]
                    total_win += result["win_trades"]
                    total_loss += result["loss_trades"]
            except Exception as e:
                print(f"回测失败 {code}: {e}")
                continue
        
        # 计算总体指标
        if results:
            avg_return = total_return / len(results)
            win_rate = total_win / (total_win + total_loss) * 100 if (total_win + total_loss) > 0 else 0
            
            # 保存回测结果
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select
                result = BacktestResult(
                    strategy_id=strategy_id,
                    start_date=start_date,
                    end_date=end_date,
                    total_return=avg_return,
                    max_drawdown=max(r.get("max_drawdown", 0) for r in results),
                    total_trades=total_win + total_loss,
                    win_trades=total_win,
                    loss_trades=total_loss,
                    win_rate=win_rate,
                    notes=json.dumps(results[:10])
                )
                session.add(result)
                await session.commit()
            
            return {
                "strategy_id": strategy_id,
                "start_date": start_date,
                "end_date": end_date,
                "total_return": avg_return,
                "max_drawdown": max(r.get("max_drawdown", 0) for r in results),
                "sharpe": self._calculate_sharpe(results),
                "total_trades": total_win + total_loss,
                "win_trades": total_win,
                "loss_trades": total_loss,
                "win_rate": win_rate,
                "details": results[:20]
            }
        
        return {"error": "无有效回测结果"}
    
    async def _backtest_single(
        self, 
        code: str, 
        start_date: date, 
        end_date: date,
        capital: float,
        commission: float
    ) -> Optional[Dict]:
        """单只股票回测"""
        klines = await self.data_service.get_kline(code, start_date, end_date, limit=500)
        
        if len(klines) < 30:
            return None
        
        df = pd.DataFrame(klines)
        
        # 简单的双均线策略
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma20"] = df["close"].rolling(20).mean()
        
        # 模拟交易
        position = 0
        buy_price = 0
        trades = []
        equity = [capital]
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i-1]
            
            # 买入信号：MA5上穿MA20
            if prev["ma5"] <= prev["ma20"] and row["ma5"] > row["ma20"] and position == 0:
                # 买入
                shares = int(capital * 0.95 / row["close"] / 100) * 100
                if shares > 0:
                    position = shares
                    buy_price = row["close"]
                    cost = position * buy_price * (1 + commission)
                    trades.append({"action": "buy", "date": row["date"], "price": buy_price})
            
            # 卖出信号：MA5下穿MA20
            elif prev["ma5"] >= prev["ma20"] and row["ma5"] < row["ma20"] and position > 0:
                # 卖出
                proceeds = position * row["close"] * (1 - commission)
                trades.append({"action": "sell", "date": row["date"], "price": row["close"]})
                position = 0
            
            # 更新权益
            if position > 0:
                equity.append(position * row["close"])
            else:
                equity.append(equity[-1])
        
        # 计算收益率
        if trades:
            final_value = equity[-1]
            return_rate = (final_value - capital) / capital * 100
            
            # 计算最大回撤
            equity_series = pd.Series(equity)
            max_drawdown = ((equity_series.cummax() - equity_series) / equity_series.cummax()).max() * 100
            
            # 统计交易
            buy_trades = [t for t in trades if t["action"] == "buy"]
            sell_trades = [t for t in trades if t["action"] == "sell"]
            
            wins = 0
            losses = 0
            for i, sell in enumerate(sell_trades):
                if i < len(buy_trades):
                    if sell["price"] > buy_trades[i]["price"]:
                        wins += 1
                    else:
                        losses += 1
            
            return {
                "code": code,
                "return_rate": return_rate,
                "max_drawdown": max_drawdown,
                "total_trades": len(buy_trades),
                "win_trades": wins,
                "loss_trades": losses,
                "win_rate": wins / len(buy_trades) * 100 if buy_trades else 0
            }
        
        return None
    
    def _calculate_sharpe(self, results: List[Dict]) -> float:
        """计算夏普比率（简化版）"""
        if not results:
            return 0
        
        returns = [r.get("return_rate", 0) for r in results]
        if len(returns) < 2:
            return 0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        return mean_return / std_return * np.sqrt(252)
    
    async def get_backtest_results(self, strategy_id: Optional[int] = None, 
                                    limit: int = 50) -> List[Dict]:
        """获取回测结果列表"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            query = select(BacktestResult).order_by(BacktestResult.created_at.desc())
            
            if strategy_id:
                query = query.where(BacktestResult.strategy_id == strategy_id)
            
            query = query.limit(limit)
            result = await session.execute(query)
            results = result.scalars().all()
            
            return [
                {
                    "id": r.id,
                    "strategy_id": r.strategy_id,
                    "start_date": r.start_date,
                    "end_date": r.end_date,
                    "total_return": r.return_rate,
                    "max_drawdown": r.max_drawdown,
                    "sharpe": r.sharpe,
                    "total_trades": r.total_trades,
                    "win_trades": r.win_trades,
                    "loss_trades": r.loss_trades,
                    "win_rate": r.win_rate,
                    "created_at": r.created_at
                }
                for r in results
            ]
