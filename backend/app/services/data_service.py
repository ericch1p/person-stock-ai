"""
数据服务 - 负责数据获取、存储和管理
"""
import os
# 禁用代理以确保akshare可以正常访问
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)
os.environ.pop('all_proxy', None)

from datetime import date, timedelta, datetime
from typing import Optional, List, Dict, Any
import pandas as pd
from loguru import logger

from ..database import AsyncSessionLocal
from ..models import Stock, DailyKline, Financial, MoneyFlow
from ..schemas.watchlist import WatchlistItem


class DataService:
    """数据服务"""
    
    def __init__(self):
        self.akshare = None  # 延迟导入
    
    async def _get_akshare(self):
        """延迟获取 akshare"""
        if self.akshare is None:
            # 检查代理是否可用（通过实际HTTP请求测试）
            proxy_url = os.environ.get('http_proxy', '')
            if proxy_url:
                try:
                    import urllib.request
                    proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
                    opener = urllib.request.build_opener(proxy_handler)
                    # 测试代理连通性（使用百度）
                    opener.open('http://www.baidu.com', timeout=3)
                    logger.info("代理可用，继续使用代理")
                except Exception as e:
                    logger.warning(f"代理不可用({e})，清除代理设置")
                    for key in list(os.environ.keys()):
                        if 'proxy' in key.lower():
                            os.environ.pop(key, None)
            
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
    
    async def _fetch_kline_from_sina(self, code: str, limit: int = 365) -> Optional[List[Dict]]:
        """从新浪财经获取K线数据"""
        try:
            import requests
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            })
            
            # 确定市场前缀
            if code.startswith('6'):
                symbol = f'sh{code}'
            else:
                symbol = f'sz{code}'
            
            url = 'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
            params = {'symbol': symbol, 'scale': '240', 'datalen': str(limit)}
            
            r = session.get(url, params=params, timeout=10)
            if r.status_code != 200:
                return None
            
            import json
            data = json.loads(r.text)
            if not data:
                return None
            
            # 转换格式
            klines = []
            for item in data:
                klines.append({
                    'date': item['day'],
                    'open': float(item['open']),
                    'high': float(item['high']),
                    'low': float(item['low']),
                    'close': float(item['close']),
                    'volume': float(item['volume']),
                })
            return klines
        except Exception as e:
            logger.error(f"新浪K线获取失败 {code}: {e}")
            return None
    
    async def update_daily_kline(self, code: str, start_date: date = None, 
                                  end_date: date = None) -> bool:
        """更新日线数据"""
        # 优先使用akshare，失败则使用新浪API
        ak = await self._get_akshare()
        
        if start_date is None:
            start_date = date.today() - timedelta(days=365)
        if end_date is None:
            end_date = date.today()
        
        kline_data = None
        
        # 尝试akshare
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"
            )
            
            if df is not None and not df.empty:
                kline_data = df.to_dict('records')
                logger.info(f"akshare获取K线 {code}: {len(kline_data)} 条")
        except Exception as e:
            logger.warning(f"akshare获取K线失败 {code}: {e}")
        
        # 尝试新浪API
        if kline_data is None:
            try:
                kline_data = await self._fetch_kline_from_sina(code, limit=365)
                if kline_data:
                    logger.info(f"新浪API获取K线 {code}: {len(kline_data)} 条")
            except Exception as e:
                logger.warning(f"新浪API获取K线失败 {code}: {e}")
        
        if not kline_data:
            logger.warning(f"所有K线数据源获取失败 {code}")
            return False
        
        # 保存到数据库
        try:
            async with AsyncSessionLocal() as session:
                for row in kline_data:
                    # 处理akshare格式
                    if '日期' in row:
                        kline_date = pd.to_datetime(row['日期']).date()
                        kline = DailyKline(
                            code=code,
                            date=kline_date,
                            open=float(row['开盘']),
                            high=float(row['最高']),
                            low=float(row['最低']),
                            close=float(row['收盘']),
                            volume=float(row['成交量']),
                            amount=float(row.get('成交额', 0) or 0),
                            change_pct=float(row.get('涨跌幅', 0) or 0)
                        )
                    # 处理新浪格式
                    elif 'date' in row:
                        kline = DailyKline(
                            code=code,
                            date=date.fromisoformat(row['date']),
                            open=row['open'],
                            high=row['high'],
                            low=row['low'],
                            close=row['close'],
                            volume=row['volume'],
                            amount=0,
                            change_pct=0
                        )
                    else:
                        continue
                    
                    await session.merge(kline)
                
                await session.commit()
                logger.info(f"K线数据已保存 {code}: {len(kline_data)} 条")
                return True
        except Exception as e:
            logger.error(f"保存K线失败 {code}: {e}")
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
    
    # ========== 自选股管理 ==========
    
    async def get_watchlist(self, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> Dict:
        """获取自选股列表"""
        from sqlalchemy import select, func
        from ..models.watchlist import Watchlist
        
        async with AsyncSessionLocal() as session:
            # 构建查询
            query = select(Watchlist)
            count_query = select(func.count()).select_from(Watchlist)
            
            if status:
                query = query.where(Watchlist.status == status)
                count_query = count_query.where(Watchlist.status == status)
            
            # 获取总数
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0
            
            # 获取列表
            query = query.order_by(Watchlist.select_date.desc()).offset(offset).limit(limit)
            result = await session.execute(query)
            items = result.scalars().all()
            
            return {
                "total": total,
                "items": [
                    {
                        "id": w.id,
                        "code": w.code,
                        "name": w.name or w.code,
                        "status": w.status,
                        "strategy_id": w.strategy_id,
                        "select_date": w.select_date if w.select_date else None,
                        "notes": w.notes,
                        "tags": w.tags,
                        "created_at": w.created_at.isoformat() if w.created_at else None
                    }
                    for w in items
                ]
            }
    
    async def add_to_watchlist(self, item: WatchlistItem) -> Dict:
        """添加自选股"""
        from sqlalchemy import select
        from ..models.watchlist import Watchlist
        
        async with AsyncSessionLocal() as session:
            # 检查是否已存在
            result = await session.execute(
                select(Watchlist).where(Watchlist.code == item.code)
            )
            existing = result.scalar_one_or_none()
            if existing:
                return {"success": False, "message": "股票已在自选股池中"}
            
            # 获取股票名称（如果未提供）
            name = item.name or item.code
            if not item.name:
                result = await session.execute(
                    select(Stock).where(Stock.code == item.code)
                )
                stock = result.scalar_one_or_none()
                if stock:
                    name = stock.name
            
            watchlist_item = Watchlist(
                code=item.code,
                name=name,
                status=item.status or "watch",
                notes=item.notes,
                tags=item.tags,
                select_date=date.today().isoformat()
            )
            session.add(watchlist_item)
            await session.commit()
            await session.refresh(watchlist_item)
            
            return {"success": True, "id": watchlist_item.id}
    
    async def remove_from_watchlist(self, code: str) -> Dict:
        """删除自选股"""
        from sqlalchemy import delete
        from ..models.watchlist import Watchlist
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(Watchlist).where(Watchlist.code == code)
            )
            await session.commit()
            
            if result.rowcount > 0:
                return {"success": True}
            return {"success": False, "message": "股票不在自选股池中"}
    
    async def update_watchlist(self, code: str, item: Dict) -> Dict:
        """更新自选股"""
        from sqlalchemy import select, update
        from ..models.watchlist import Watchlist
        
        async with AsyncSessionLocal() as session:
            # 获取现有记录
            result = await session.execute(
                select(Watchlist).where(Watchlist.code == code)
            )
            watchlist_item = result.scalar_one_or_none()
            if not watchlist_item:
                return {"success": False, "message": "股票不在自选股池中"}
            
            if "status" in item:
                watchlist_item.status = item["status"]
            if "notes" in item:
                watchlist_item.notes = item["notes"]
            if "tags" in item:
                watchlist_item.tags = item["tags"]
            
            await session.commit()
            return {"success": True}
    
    async def sync_watchlist_data(self) -> Dict:
        """同步自选股数据（K线+实时行情）"""
        from sqlalchemy import select
        from ..models.watchlist import Watchlist
        
        async with AsyncSessionLocal() as session:
            # 获取所有自选股
            result = await session.execute(select(Watchlist))
            watchlist = result.scalars().all()
        
        if not watchlist:
            return {"success": False, "message": "自选股池为空"}
        
        results = {
            "total": len(watchlist),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for stock in watchlist:
            try:
                # 更新K线数据
                kline_result = await self.update_daily_kline(stock.code)
                
                # 获取实时行情
                realtime = await self.get_realtime_quote_single(stock.code)
                
                if kline_result:
                    results["success"] += 1
                    results["details"].append({
                        "code": stock.code,
                        "name": stock.name,
                        "status": "success",
                        "price": realtime.get("price") if realtime else None
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "code": stock.code,
                        "name": stock.name,
                        "status": "kline_failed",
                        "price": realtime.get("price") if realtime else None
                    })
            except Exception as e:
                logger.error(f"同步自选股 {stock.code} 失败: {e}")
                results["failed"] += 1
                results["details"].append({
                    "code": stock.code,
                    "name": stock.name,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
