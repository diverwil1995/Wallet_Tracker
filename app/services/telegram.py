from typing import Optional, Union, Dict
import aiohttp
import logging
from app.core.config import get_settings
from app.models.telegram import TelegramMessage

logger = logging.getLogger(__name__)
settings = get_settings()

class TelegramBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.api_base = f"https://api.telegram.org/bot{self.token}"

    async def _make_request(self, method: str, data: Dict) -> Dict:
        """發送請求到 Telegram API"""
        url = f"{self.api_base}/{method}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status != 200:
                        logger.error(f"Telegram API error: {response.status} - {await response.text()}")
                        return {"ok": False, "error": f"API request failed with status {response.status}"}
                    return await response.json()
        except Exception as e:
            logger.error(f"Error making request to Telegram API: {str(e)}")
            return {"ok": False, "error": str(e)}

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = "HTML",
        reply_to_message_id: Optional[int] = None
    ) -> Dict:
        """發送文本消息"""
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
            
        return await self._make_request("sendMessage", data)

    async def send_sticker(
        self,
        chat_id: Union[int, str],
        sticker: str,
        reply_to_message_id: Optional[int] = None
    ) -> Dict:
        """發送貼圖"""
        data = {
            "chat_id": chat_id,
            "sticker": sticker
        }
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
            
        return await self._make_request("sendSticker", data)

    def parse_wallet_query(self, message_text: str) -> Optional[Dict[str, str]]:
        """解析查詢錢包的消息"""
        try:
            lines = message_text.strip().split('\n')
            if len(lines) < 2 or "查收" not in lines[0]:
                return None

            wallet_address = lines[1].strip()
            amount = float(lines[2].strip()) if len(lines) > 2 else None

            return {
                "wallet_address": wallet_address,
                "amount": amount
            }
        except Exception as e:
            logger.error(f"Error parsing wallet query: {str(e)}")
            return None

    async def handle_message(self, message: TelegramMessage) -> None:
        """處理接收到的消息"""
        if not message.text:
            return
            
        # 解析錢包查詢
        query = self.parse_wallet_query(message.text)
        if query:
            # TODO: 實現錢包查詢邏輯
            response = "收到查詢請求，正在處理..."
            await self.send_message(message.chat.id, response)
            
        # TODO: 實現其他消息處理邏輯

telegram_bot = TelegramBot()