from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os
from pathlib import Path

# 獲取專案根目錄路徑
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Wallet Tracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Telegram Settings
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str
    
    # TronScan Settings
    TRONSCAN_API_KEY: str
    TRONSCAN_API_BASE_URL: str = "https://apilist.tronscanapi.com/api"
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ROOT_DIR / ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    獲取設定實例，使用 lru_cache 來避免重複讀取 .env 文件
    """
    return Settings()