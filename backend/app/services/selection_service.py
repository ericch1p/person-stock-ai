"""
选股服务 - 实现各种选股策略
"""
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np

from .data_service import DataService


class SelectionService:
    """选股服务"""
    
    def __init__(self):
        self.data_service = DataService()
    
    async def select_stocks(self, criteria: Dict[str, Any]) -> List[Dict]:
        """
        根据条件选股
        
        Args:
            criteria: 选股条件
            
        Returns:
            选股结果列表
        """
        results = []
        
        # 1. 获取所有股票
        stock_list = await self.data_service.list_stocks(limit=5000)
        stocks = stock_list.get("items", [])
        
        # 2. 逐个筛选
        for stock in stocks:
            code = stock["code"]
            
            # 排除ST股票
            if criteria.get("exclude_st", True) and "ST" in (stock.get("name") or ""):
                continue
            
            try:
                # 获取K线数据
                klines = await self.data_service.get_kline(code, limit=60)
                if len(klines) < 30:
                    continue
                
                # 技术面筛选
                tech_result = self._check_technical(klines, criteria)
                if not tech_result["passed"]:
                    continue
                
                # 获取财务数据
                financial = await self.data_service.get_financial(code)
                
                # 基本面筛选
                fund_result = self._check_fundamental(financial, criteria)
                if not fund_result["passed"]:
                    continue
                
                # 资金面筛选（简化处理）
                money_result = self._check_money(klines, criteria)
                
                # 综合评分
                score = self._calculate_score(tech_result, fund_result, money_result)
                
                # 构建结果
                result = {
                    "code": code,
                    "name": stock["name"],
                    "industry": stock.get("industry"),
                    "close": klines[-1]["close"] if klines else None,
                    "change_pct": klines[-1]["change_pct"] if klines else None,
                    "volume": klines[-1]["volume"] if klines else None,
                    **tech_result,
                    **fund_result,
                    **money_result,
                    "match_score": score,
                    "match_reasons": self._get_match_reasons(tech_result, fund_result, money_result)
                }
                results.append(result)
                
            except Exception as e:
                print(f"筛选股票失败 {code}: {e}")
                continue
        
        # 按匹配度排序
        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return results[:100]  # 最多返回100只
    
    def _check_technical(self, klines: List[Dict], criteria: Dict) -> Dict:
        """技术面筛选"""
        result = {"passed": False, "tech_score": 0, "ma_status": None, "macd_status": None}
        
        if len(klines) < 30:
            return result
        
        df = pd.DataFrame(klines)
        
        # 计算均线
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma10"] = df["close"].rolling(10).mean()
        df["ma20"] = df["close"].rolling(20).mean()
        df["ma60"] = df["close"].rolling(60).mean()
        
        # 计算MACD
        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9, adjust=False).mean()
        macd = (dif - dea) * 2
        df["macd"] = macd
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        score = 0
        reasons = []
        
        # 均线多头排列
        if criteria.get("ma_bullish_arrangement"):
            if last["ma5"] > last["ma10"] > last["ma20"] > last["ma60"]:
                score += 30
                result["ma_status"] = "多头排列"
        
        # 均线金叉
        if criteria.get("ma_golden_cross"):
            if prev["ma5"] <= prev["ma10"] and last["ma5"] > last["ma10"]:
                score += 25
                result["ma_status"] = "金叉"
        
        # MACD金叉
        if criteria.get("macd_golden_cross"):
            if prev["macd"] <= 0 and last["macd"] > 0:
                score += 25
                result["macd_status"] = "金叉"
        
        # MACD水下金叉（在水下形成金叉更强）
        if criteria.get("macd_below_zero"):
            if dif.iloc[-2] < 0 and dif.iloc[-1] >= 0:
                score += 20
                result["macd_status"] = "水下金叉"
        
        # 放量突破
        if criteria.get("volume_breakout"):
            avg_vol = df["volume"].iloc[-20:-1].mean()
            if last["volume"] > avg_vol * 1.5:
                score += 20
        
        result["tech_score"] = score
        
        if score >= 20:  # 技术面得分门槛
            result["passed"] = True
        
        return result
    
    def _check_fundamental(self, financial: Optional[Dict], criteria: Dict) -> Dict:
        """基本面筛选"""
        result = {"passed": False, "fund_score": 0}
        
        if financial is None:
            return result
        
        score = 0
        
        # PE筛选
        pe = financial.get("pe")
        if pe:
            pe_min = criteria.get("pe_min")
            pe_max = criteria.get("pe_max")
            if pe_min and pe < pe_min:
                return result
            if pe_max and pe > pe_max:
                return result
            if 10 <= pe <= 30:  # 合理PE范围
                score += 15
        
        # PB筛选
        pb = financial.get("pb")
        if pb:
            pb_min = criteria.get("pb_min")
            pb_max = criteria.get("pb_max")
            if pb_min and pb < pb_min:
                return result
            if pb_max and pb > pb_max:
                return result
            if pb < 5:  # 低PB
                score += 10
        
        # ROE筛选
        roe = financial.get("roe")
        if roe and criteria.get("roe_min"):
            if roe >= criteria["roe_min"]:
                score += 20
            else:
                return result
        
        # 营收增长
        rev_growth = financial.get("revenue_growth")
        if rev_growth and criteria.get("revenue_growth_min"):
            if rev_growth >= criteria["revenue_growth_min"]:
                score += 15
        
        # 净利润增长
        profit_growth = financial.get("net_profit_growth")
        if profit_growth and criteria.get("net_profit_growth_min"):
            if profit_growth >= criteria["net_profit_growth_min"]:
                score += 15
        
        result["fund_score"] = score
        result["pe"] = pe
        result["pb"] = pb
        result["roe"] = roe
        
        if score >= 15:
            result["passed"] = True
        
        return result
    
    def _check_money(self, klines: List[Dict], criteria: Dict) -> Dict:
        """资金面筛选（简化版，基于成交量变化）"""
        result = {"passed": False, "money_score": 0}
        
        if len(klines) < 20:
            return result
        
        df = pd.DataFrame(klines)
        last = df.iloc[-1]
        
        # 换手率估算（成交量/流通股本）
        avg_vol = df["volume"].iloc[-20:-1].mean()
        score = 0
        
        # 放量
        if last["volume"] > avg_vol * 1.2:
            score += 30
        
        # 持续放量
        recent_vol = df["volume"].iloc[-5:].mean()
        if recent_vol > avg_vol:
            score += 20
        
        result["money_score"] = score
        result["volume"] = last["volume"]
        
        if score >= 20:
            result["passed"] = True
        
        return result
    
    def _calculate_score(self, tech: Dict, fund: Dict, money: Dict) -> float:
        """计算综合评分"""
        return (tech.get("tech_score", 0) * 0.4 + 
                fund.get("fund_score", 0) * 0.4 + 
                money.get("money_score", 0) * 0.2)
    
    def _get_match_reasons(self, tech: Dict, fund: Dict, money: Dict) -> List[str]:
        """获取匹配原因"""
        reasons = []
        
        if tech.get("ma_status"):
            reasons.append(f"均线{tech['ma_status']}")
        if tech.get("macd_status"):
            reasons.append(f"MACD{tech['macd_status']}")
        if tech.get("tech_score", 0) >= 30:
            reasons.append("技术面强势")
        
        if fund.get("roe"):
            reasons.append(f"ROE={fund['roe']:.1f}%")
        if fund.get("fund_score", 0) >= 20:
            reasons.append("基本面优良")
        
        if money.get("money_score", 0) >= 30:
            reasons.append("资金活跃")
        
        return reasons