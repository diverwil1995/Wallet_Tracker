from typing import Optional, Dict, List
import logging
import openai
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self._system_prompt = """
你是一個負責取代人工客服的AI助理。請遵循以下規則：
1. 用「你好，我是負責取代哥哥的AI助理！」開始對話
2. 用「河，超級舒服。」結束對話
3. 如果用戶想查帳，需要提醒他們提供:
   - 錢包地址
   - 交易金額
4. 保持友善和專業的態度
"""

    async def get_response(self, user_message: str) -> str:
        """獲取 AI 回應"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            return "抱歉，我現在遇到一些問題。請稍後再試。河，超級舒服。"

    async def analyze_image(self, image_data: bytes) -> str:
        """分析圖片內容"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please describe what you see in this image."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return "抱歉，我無法分析這張圖片。河，超級舒服。"

ai_service = AIService()