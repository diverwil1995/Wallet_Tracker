from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None

class TelegramChat(BaseModel):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None

class TelegramMessage(BaseModel):
    message_id: int
    from_user: TelegramUser
    chat: TelegramChat
    date: datetime
    text: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        
    @classmethod
    def from_webhook(cls, data: dict):
        """從 Telegram webhook 數據創建消息對象"""
        return cls(
            message_id=data["message_id"],
            from_user=TelegramUser(**data["from"]),
            chat=TelegramChat(**data["chat"]),
            date=datetime.fromtimestamp(data["date"]),
            text=data.get("text")
        )