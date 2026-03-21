"""
选股服务 - 实现各种选股策略
"""
from typing import Optional, List, Dict, Any
import pandas as pd

from .data_service import DataService


class SelectionService:
    """选股服务"""
    
    def __init__(self):
        self.data_service = DataService()
    
    async def select_stocks(self, criteria: Dict[str, Any]) -> List[Dict]:
        """根据条件选股"""
        results = []
        stock_list = await self.data_service.list_stocks(limit=5000)
        stocks = stock_list.get("items", [])
        
        for stock in stocks:
            code = stock["code"]
            if criteria.get("exclude_st", True) and "ST" in (stock.get("name") or ""):
                continue
            
            try:
                klines = await self.data_service.get_kline(code, limit=120)
                if len(klines) < 30:
                    continue
                
                tech_result = self._check_technical(klines, criteria)
                financial = await self.data_service.get_financial(code)
                fund_result = self._check_fundamental(financial, criteria)
                money_result = self._check_money(klines, criteria)
                score = self._calculate_score(tech_result, fund_result, money_result)
                
                if score > 0 or criteria.get("show_all"):
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
        
        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return results[:100]

    def _check_technical(self, klines: List[Dict], criteria: Dict) -> Dict:
        """技术面筛选"""
        result = {"passed": True, "tech_score": 0, "tech_signals": [], "indicators": {}}
        
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
        df["macd"] = (dif - dea) * 2
        df["dif"] = dif
        
        # 计算KDJ
        low14 = df["low"].rolling(9).min()
        high14 = df["high"].rolling(9).max()
        rsv = (df["close"] - low14) / (high14 - low14) * 100
        df["kdj_k"] = rsv.ewm(com=2, adjust=False).mean()
        df["kdj_d"] = df["kdj_k"].ewm(com=2, adjust=False).mean()
        
        # 计算RSI
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        # 计算布林带
        df["bb_mid"] = df["close"].rolling(20).mean()
        df["bb_std"] = df["close"].rolling(20).std()
        df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
        df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]
        
        # 计算成交量均线
        df["vol_ma5"] = df["volume"].rolling(5).mean()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        score = 0
        signals = []
        
        # 策略1: 均线多头排列
        if criteria.get("ma_bullish_arrangement"):
            if last["ma5"] > last["ma10"] > last["ma20"] > last["ma60"]:
                score += 30
                signals.append("均线多头")
        
        # 策略2: 均线金叉
        if criteria.get("ma_golden_cross"):
            if prev["ma5"] <= prev["ma10"] and last["ma5"] > last["ma10"]:
                score += 25
                signals.append("MA5上穿MA10")
        
        # 策略3: MACD金叉
        if criteria.get("macd_golden_cross"):
            if prev["macd"] <= 0 and last["macd"] > 0:
                score += 25
                signals.append("MACD金叉")
        
        # 策略4: MACD水下金叉
        if criteria.get("macd_below_zero"):
            if len(df) >= 3 and df.iloc[-3]["dif"] < 0 and df.iloc[-2]["dif"] < 0 and last["dif"] >= 0:
                score += 20
                signals.append("MACD水上金叉")
        
        # 策略5: KDJ金叉
        if criteria.get("kdj_golden_cross"):
            if prev["kdj_k"] <= prev["kdj_d"] and last["kdj_k"] > last["kdj_d"]:
                score += 20
                signals.append(f"KDJ金叉(K={last['kdj_k']:.0f})")
        
        # 策略6: KDJ超卖反弹
        if criteria.get("kdj_oversold"):
            if last["kdj_k"] < 25 and prev["kdj_k"] < last["kdj_k"]:
                score += 25
                signals.append("KDJ超卖反弹")
        
        # 策略7: RSI超卖
        if criteria.get("rsi_oversold") and pd.notna(last["rsi"]):
            if last["rsi"] < 30:
                score += 25
                signals.append("RSI超卖")
        
        # 策略8: 布林带策略
        if criteria.get("bollinger_band"):
            if pd.notna(last["bb_upper"]):
                bb_pos = (last["close"] - last["bb_lower"]) / (last["bb_upper"] - last["bb_lower"])
                if bb_pos > 0.8:
                    score += 15
                    signals.append("布林带上轨")
                elif bb_pos < 0.2:
                    score += 20
                    signals.append("布林带下轨")
        
        # 策略9: 放量突破
        if criteria.get("volume_breakout"):
            if last["volume"] > last["vol_ma5"] * 1.5:
                score += 15
                signals.append("成交量放大")
        
        result["tech_score"] = score
        result["tech_signals"] = signals
        result["indicators"] = {
            "ma5": round(last["ma5"], 2) if pd.notna(last["ma5"]) else None,
            "ma10": round(last["ma10"], 2) if pd.notna(last["ma10"]) else None,
            "ma20": round(last["ma20"], 2) if pd.notna(last["ma20"]) else None,
            "kdj_k": round(last["kdj_k"], 1) if pd.notna(last["kdj_k"]) else None,
            "kdj_d": round(last["kdj_d"], 1) if pd.notna(last["kdj_d"]) else None,
            "rsi": round(last["rsi"], 1) if pd.notna(last["rsi"]) else None,
            "macd": round(last["macd"], 3) if pd.notna(last["macd"]) else None
        }
        
        return result

    def _check_fundamental(self, financial: Optional[Dict], criteria: Dict) -> Dict:
        """基本面筛选"""
        result = {"passed": True, "fund_score": 0, "fund_signals": []}
        
        if not financial:
            return result
        
        score = 0
        signals = []
        pe = financial.get("pe")
        pb = financial.get("pb")
        roe = financial.get("roe")
        
        # PE筛选
        if pe and criteria.get("pe_max"):
            if pe < criteria["pe_max"]:
                score += 10
                signals.append(f"PE={pe:.1f}")
        
        # PB筛选
        if pb and criteria.get("pb_max"):
            if pb < criteria["pb_max"]:
                score += 10
                signals.append(f"PB={pb:.1f}")
        
        # ROE筛选
        if roe and criteria.get("roe_min"):
            if roe >= criteria["roe_min"]:
                score += 15
                signals.append(f"ROE={roe:.1f}%")
        
        result["fund_score"] = score
        result["fund_signals"] = signals
        
        return result
    
    def _check_money(self, klines: List[Dict], criteria: Dict) -> Dict:
        """资金面筛选"""
        result = {"passed": True, "money_score": 0, "money_signals": []}
        
        if len(klines) < 5:
            return result
        
        df = pd.DataFrame(klines)
        df["vol_ma5"] = df["volume"].rolling(5).mean()
        df["vol_ma20"] = df["volume"].rolling(20).mean()
        
        last = df.iloc[-1]
        score = 0
        signals = []
        
        # 放量
        if criteria.get("volume_breakout"):
            if last["volume"] > last["vol_ma5"] * 2:
                score += 15
                signals.append("大幅放量")
            elif last["volume"] > last["vol_ma5"] * 1.5:
                score += 10
                signals.append("温和放量")
        
        # 缩量
        if criteria.get("volume_shrink"):
            if last["volume"] < last["vol_ma5"] * 0.5:
                score += 10
                signals.append("成交量萎缩")
        
        result["money_score"] = score
        result["money_signals"] = signals
        
        return result
    
    def _calculate_score(self, tech_result: Dict, fund_result: Dict, money_result: Dict) -> int:
        """计算综合评分"""
        return (
            tech_result.get("tech_score", 0) +
            fund_result.get("fund_score", 0) +
            money_result.get("money_score", 0)
        )
    
    def _get_match_reasons(self, tech_result: Dict, fund_result: Dict, money_result: Dict) -> List[str]:
        """获取匹配原因"""
        reasons = []
        reasons.extend(tech_result.get("tech_signals", []))
        reasons.extend(fund_result.get("fund_signals", []))
        reasons.extend(money_result.get("money_signals", []))
        return reasons[:5]  # 最多返回5个原因
