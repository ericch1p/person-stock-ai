"""
数据服务 - 负责数据获取、存储和管理
"""
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd

from ..database import AsyncSessionLocal
from ..models import Stock, DailyKline, Financial, MoneyFlow


class DataService:
    """数据服务"""
    
    def __init__(self):
        self.akshare = None  # 延迟导入
    
    async def _get_akshare(self):
        """延迟获取 akshare"""
        if self.akshare is None:
            import akshare as ak
            self.akshare = ak
        return self.akshare
    
    # ========== 股票基础信息 ==========
    
    async def update_stock_list(self) -> int:
        """更新股票列表，返回更新数量"""
        ak = await self._get_akshare()
        async with AsyncSessionLocal() as session:
            df = ak.stock_info_a_code_name()
            
            count = 0
            for _, row in df.iterrows():
                code = str(row['code'])
                if code.startswith('6'):
                    market = '沪市'
                elif code.startswith('0') or code.startswith('3'):
                    market = '深市'
                elif code.startswith('8') or code.startswith('4'):
                    market = '北交所'
                else:
                    market = '其他'
                
                stock = Stock(code=code, name=row['name'], market=market)
                session.merge(stock)
                count += 1
            
            await session.commit()
            return count
    
    async def get_stock_info(self, code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(Stock).where(Stock.code == code))
            stock = result.scalar_one_or_none()
            if stock:
                return {"code": stock.code, "name": stock.name, "industry": stock.industry, 
                        "market": stock.market, "status": stock.status}
            return None
    
    async def list_stocks(self, market: Optional[str] = None, industry: Optional[str] = None,
                          status: int = 1, limit: int = 100, offset: int = 0) -> Dict:
        """获取股票列表"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select, func
            
            query = select(Stock)
            if market:
                query = query.where(Stock.market == market)
            if industry:
                query = query.where(Stock.industry == industry)
            if status is not None:
                query = query.where(Stock.status == status)
            
            count_query = select(func.count())
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            stocks = result.scalars().all()
            
            return {
                "total": total,
                "items": [{"code": s.code, "name": s.name, "industry": s.industry, 
                          "market": s.market, "status": s.status} for s in stocks]
            }
    
    # ========== K线数据 ==========
    
    async def update_daily_kline(self, code: str, start_date: date = None, 
                                  end_date: date = None) -> bool:
        """更新日线数据"""
        ak = await self._get_akshare()
        
        if start_date is None:
            start_date = date.today() - timedelta(days=365)
        if end_date is None:
            end_date = date.today()
        
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"
            )
            
            if df is None or df.empty:
                return False
            
            async with AsyncSessionLocal() as session:
                for _, row in df.iterrows():
                    kline = DailyKline(
                        code=code,
                        date=pd.to_datetime(row['日期']).date(),
                        open=float(row['开盘']),
                        high=float(row['最高']),
                        low=float(row['最低']),
                        close=float(row['收盘']),
                        volume=float(row['成交量']),
                        amount=float(row['成交额']) if '成交额' in row else None,
                        change_pct=float(row['涨跌幅']) if '涨跌幅' in row else None
                    )
                    session.merge(kline)
                
                await session.commit()
                return True
        except Exception as e:
            print(f"更新K线失败 {code}: {e}")
            return False
    
    async def get_kline(self, code: str, start_date: Optional[date] = None,
                        end_date: Optional[date] = None, limit: int = 100) -> List[Dict]:
        """获取K线数据"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            
            query = select(DailyKline).where(DailyKline.code == code)
            if start_date:
                query = query.where(DailyKline.date >= start_date)
            if end_date:
                query = query.where(DailyKline.date <= end_date)
            
            query = query.order_by(DailyKline.date.desc()).limit(limit)
            result = await session.execute(query)
            klines = list(reversed(result.scalars().all()))
            
            return [{"code": k.code, "date": k.date, "open": k.open, "high": k.high,
                    "low": k.low, "close": k.close, "volume": k.volume,
                    "amount": k.amount, "change_pct": k.change_pct} for k in klines]
    
    async def get_realtime_quote(self, code: str) -> Optional[Dict]:
        """获取实时行情（通过 pytdx）"""
        try:
            from pytdx.hq import TdxHq_API
            api = TdxHq_API()
            
            # 尝试沪市
            async with api.connect():
                data = api.get_security_bars(0, 0, code, 0, 1)
                if data and len(data) > 0:
                    return data[0]
            
            # 尝试深市
            async with api.connect():
                data = api.get_security_bars(1, 0, code, 0, 1)
                if data and len(data) > 0:
                    return data[0]
                    
            return None
        except Exception as e:
            print(f"获取实时行情失败 {code}: {e}")
            return None
    
    # ========== 财务数据 ==========
    
    async def update_financial_data(self, code: str) -> bool:
        """更新财务数据"""
        ak = await self._get_akshare()
        
        try:
            df = ak.stock_financial_analysis_indicator(
                symbol=code,
                start_date="20200101",
                end_date=date.today().strftime("%Y%m%d")
            )
            
            if df is None or df.empty:
                return False
            
            async with AsyncSessionLocal() as session:
                for _, row in df.iterrows():
                    try:
                        financial = Financial(
                            code=code,
                            date=pd.to_datetime(row['日期']).date() if pd.notna(row.get('日期')) else None,
                            pe=float(row['市盈率']) if pd.notna(row.get('市盈率')) else None,
                            pb=float(row['市净率']) if pd.notna(row.get('市净率')) else None,
                            roe=float(row['净资产收益率']) if pd.notna(row.get('净资产收益率')) else None,
                            gross_margin=float(row['毛利率']) if pd.notna(row.get('毛利率')) else None,
                            net_margin=float(row['净利率']) if pd.notna(row.get('净利率')) else None,
                            revenue=float(row['营业收入']) if pd.notna(row.get('营业收入')) else None,
                            net_profit=float(row['净利润']) if pd.notna(row.get('净利润')) else None,
                        )
                        session.merge(financial)
                    except Exception:
                        continue
                
                await session.commit()
                return True
        except Exception as e:
            print(f"更新财务数据失败 {code}: {e}")
            return False
    
    async def get_financial(self, code: str) -> Optional[Dict]:
        """获取最新财务数据"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Financial).where(Financial.code == code).order_by(Financial.date.desc()).limit(1)
            )
            f = result.scalar_one_or_none()
            if f:
                return {"code": f.code, "date": f.date, "pe": f.pe, "pb": f.pb, 
                        "roe": f.roe, "revenue_growth": f.revenue_growth,
                        "net_profit_growth": f.net_profit_growth}
            return None
    
    # ========== 资金流向 ==========
    
    async def update_money_flow(self, code: str) -> bool:
        """更新资金流向数据"""
        ak = await self._get_akshare()
        
        try:
            df = ak.stock_individual_fund_flow(stock=code, market='sh')
            if df is None or df.empty:
                df = ak.stock_individual_fund_flow(stock=code, market='sz')
            if df is None or df.empty:
                return False
            
            async with AsyncSessionLocal() as session:
                for _, row in df.iterrows():
                    try:
                        flow = MoneyFlow(
                            code=code,
                            date=pd.to_datetime(row.get('日期')).date() if row.get('日期') else None,
                            close_price=float(row.get('收盘价', 0)) if pd.notna(row.get('收盘价')) else None,
                            turnover_rate=float(row.get('换手率', 0)) if pd.notna(row.get('换手率')) else None,
                            net_amount=float(row.get('净流入', 0)) if pd.notna(row.get('净流入')) else None,
                            buy_amount=float(row.get('买入', 0)) if pd.notna(row.get('买入')) else None,
                            sell_amount=float(row.get('卖出', 0)) if pd.notna(row.get('卖出')) else None,
                        )
                        session.add(flow)
                    except Exception:
                        continue
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"更新资金流向失败 {code}: {e}")
            return False

    # ========== 实时行情 ==========
    
    async def get_realtime_quote(self, codes: List[str]) -> List[Dict]:
        """获取实时行情"""
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            if df is None or df.empty:
                return []
            
            # 筛选指定股票
            codes_set = set(codes)
            df = df[df['代码'].isin(codes_set)]
            
            results = []
            for _, row in df.iterrows():
                results.append({
                    "code": row.get('代码'),
                    "name": row.get('名称'),
                    "price": float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else 0,
                    "change_pct": float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0,
                    "volume": float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else 0,
                    "amount": float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else 0,
                    "high": float(row.get('最高', 0)) if pd.notna(row.get('最高')) else 0,
                    "low": float(row.get('最低', 0)) if pd.notna(row.get('最低')) else 0,
                    "open": float(row.get('今开', 0)) if pd.notna(row.get('今开')) else 0,
                    "prev_close": float(row.get('昨收', 0)) if pd.notna(row.get('昨收')) else 0,
                    "turnover": float(row.get('换手率', 0)) if pd.notna(row.get('换手率')) else 0,
                })
            return results
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return []
    
    async def get_realtime_quote_single(self, code: str) -> Optional[Dict]:
        """获取单只股票实时行情"""
        quotes = await self.get_realtime_quote([code])
        return quotes[0] if quotes else None
