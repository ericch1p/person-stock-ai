"""
推送服务 - 负责消息推送
"""
import time
import hmac
import hashlib
import base64
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

import requests

from ..database import AsyncSessionLocal
from ..models import PushConfig


class PushService:
    """推送服务"""
    
    @staticmethod
    def generate_dingtalk_sign(secret: str) -> tuple:
        """
        生成钉钉签名
        
        Args:
            secret: 密钥
            
        Returns:
            (timestamp, sign)
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return timestamp, sign
    
    async def get_config(self, config_id: int) -> Optional[PushConfig]:
        """获取推送配置"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(PushConfig).where(PushConfig.id == config_id)
            )
            return result.scalar_one_or_none()
    
    async def list_configs(self, enabled_only: bool = True) -> List[Dict]:
        """获取推送配置列表"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            query = select(PushConfig)
            if enabled_only:
                query = query.where(PushConfig.enabled == 1)
            result = await session.execute(query)
            configs = result.scalars().all()
            
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "channel": c.channel,
                    "webhook_url": c.webhook_url,
                    "rules": c.rules,
                    "enabled": c.enabled
                }
                for c in configs
            ]
    
    async def save_config(self, config_data: Dict) -> PushConfig:
        """保存推送配置"""
        async with AsyncSessionLocal() as session:
            if config_data.get("id"):
                # 更新
                from sqlalchemy import select
                result = await session.execute(
                    select(PushConfig).where(PushConfig.id == config_data["id"])
                )
                config = result.scalar_one_or_none()
                if config:
                    for key, value in config_data.items():
                        if key != "id":
                            setattr(config, key, value)
            else:
                # 新建
                config = PushConfig(**config_data)
                session.add(config)
            
            await session.commit()
            await session.refresh(config)
            return config
    
    async def send_dingtalk(
        self, 
        webhook_url: str, 
        content: str,
        title: Optional[str] = None,
        secret: Optional[str] = None,
        at_mobiles: Optional[List[str]] = None
    ) -> bool:
        """
        发送钉钉消息
        
        Args:
            webhook_url: Webhook地址
            content: 消息内容
            title: 标题
            secret: 签名密钥
            at_mobiles: @的手机号列表
        """
        try:
            # 如果有签名密钥，添加到URL
            if secret:
                timestamp, sign = self.generate_dingtalk_sign(secret)
                webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
            
            # 构建消息
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title or "股票提醒",
                    "text": content
                }
            }
            
            # 添加@功能
            if at_mobiles:
                message["at"] = {
                    "atMobiles": at_mobiles,
                    "isAtAll": False
                }
            
            # 发送请求
            response = requests.post(webhook_url, json=message, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                return True
            else:
                print(f"钉钉推送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            print(f"钉钉推送异常: {e}")
            return False
    
    async def push_selection_result(
        self, 
        config_id: int,
        selection_results: List[Dict]
    ) -> bool:
        """推送选股结果"""
        config = await self.get_config(config_id)
        if not config or not config.enabled:
            return False
        
        if config.channel != "dingtalk":
            return False
        
        # 构建消息
        title = "📈 今日选股结果"
        
        content = f"### {title}\n\n"
        content += f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        content += f"**符合条件股票**: {len(selection_results)} 只\n\n"
        
        content += "---\n\n"
        
        # 显示前10只
        for i, stock in enumerate(selection_results[:10], 1):
            name = stock.get("name", "")
            code = stock.get("code", "")
            close = stock.get("close", 0)
            change = stock.get("change_pct", 0)
            change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
            
            reasons = stock.get("match_reasons", [])
            reasons_str = " | ".join(reasons[:3]) if reasons else ""
            
            content += f"**{i}. {name}({code})**\n"
            content += f"> 现价: {close:.2f} | 涨跌: {change_str}\n"
            if reasons_str:
                content += f"> {reasons_str}\n"
            content += "\n"
        
        # 发送
        return await self.send_dingtalk(
            webhook_url=config.webhook_url,
            content=content,
            title=title,
            secret=config.secret
        )
    
    async def push_alert(
        self,
        config_id: int,
        title: str,
        content: str,
        alert_type: str = "info"
    ) -> bool:
        """推送告警/提醒"""
        config = await self.get_config(config_id)
        if not config or not config.enabled:
            return False
        
        if config.channel != "dingtalk":
            return False
        
        # 添加emoji
        emoji = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }.get(alert_type, "ℹ️")
        
        full_title = f"{emoji} {title}"
        full_content = f"### {full_title}\n\n{content}"
        
        return await self.send_dingtalk(
            webhook_url=config.webhook_url,
            content=full_content,
            title=full_title,
            secret=config.secret
        )
    
    async def push_daily_report(
        self,
        config_id: int,
        report_data: Dict
    ) -> bool:
        """推送每日报告"""
        config = await self.get_config(config_id)
        if not config or not config.enabled:
            return False
        
        title = f"📊 每日股票跟踪报告"
        
        content = f"### {title}\n\n"
        content += f"**日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # 持仓情况
        positions = report_data.get("positions", [])
        if positions:
            content += "---\n\n"
            content += "#### 📦 持仓情况\n\n"
            for pos in positions[:5]:
                name = pos.get("name", "")
                code = pos.get("code", "")
                profit = pos.get("profit_loss_pct", 0)
                profit_str = f"+{profit:.2f}%" if profit >= 0 else f"{profit:.2f}%"
                
                content += f"- {name}({code}): {profit_str}\n"
        
        # 自选股
        watchlist = report_data.get("watchlist", [])
        if watchlist:
            content += "\n---\n\n"
            content += "#### 👀 自选股\n\n"
            for stock in watchlist[:5]:
                name = stock.get("name", "")
                code = stock.get("code", "")
                change = stock.get("change_pct", 0)
                change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
                
                content += f"- {name}({code}): {change_str}\n"
        
        return await self.send_dingtalk(
            webhook_url=config.webhook_url,
            content=content,
            title=title,
            secret=config.secret
        )
