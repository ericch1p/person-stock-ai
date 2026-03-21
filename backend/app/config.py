"""
配置管理模块
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "A股智能选股系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR}/stock.db"
    DATABASE_ECHO: bool = False
    
    # 数据源配置
    AKSHARE_CACHE_DIR: str = str(DATA_DIR / "cache")
    DATA_UPDATE_HOUR: int = 16  # 收盘后更新数据
    
    # 钉钉推送配置
    DINGTALK_WEBHOOK_URL: str = ""
    DINGTALK_SECRET: str = ""
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "logs").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "cache" / "daily").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "cache" / "financial").mkdir(parents=True, exist_ok=True)
