from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from app.core.config import get_settings
from app.services.telegram import telegram_bot
from app.services.tronscan import tronscan_api
from app.services.ai import ai_service
from app.models.telegram import TelegramMessage
import logging
import base64

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

async def handle_wallet_query(message: TelegramMessage, query: dict):
    """處理錢包查詢邏輯"""
    try:
        # 發送處理中的提示
        await telegram_bot.send_message(
            message.chat.id,
            "🔍 正在查詢交易記錄，請稍候..."
        )

        # 查詢交易
        result = await tronscan_api.verify_transaction(
            query["wallet_address"],
            query.get("amount", 0)
        )

        # 處理錯誤情況
        if "error" in result:
            error_msg = f"❌ 查詢出錯: {result['error']['message']}"
            await telegram_bot.send_message(message.chat.id, error_msg)
            return

        # 發送查詢結果
        if result["verified"]:
            tx = result["transaction"]
            response = (
                f"✅ 已找到符合的交易！\n\n"
                f"💰 金額: {result['formatted_amount']:.2f} USDT\n"
                f"📱 發送地址: {tx['from_address']}\n"
                f"📥 接收地址: {tx['to_address']}\n"
                f"⏰ 交易時間: {tx['block_ts']}\n"
                f"📊 狀態: {'已確認' if tx['confirmed'] else '待確認'}\n"
                f"🔗 查看交易: https://tronscan.org/#/transaction/{tx['transaction_id']}"
            )
        else:
            response = (
                f"❌ {result.get('reason', '未找到符合的交易')}\n\n"
                f"請確認：\n"
                f"1. 錢包地址是否正確\n"
                f"2. 交易是否在過去 96 小時內\n"
                f"3. 交易金額是否正確（允許 ±2 USDT 誤差）"
            )

        await telegram_bot.send_message(message.chat.id, response)

    except Exception as e:
        logger.error(f"Error handling wallet query: {str(e)}")
        await telegram_bot.send_message(
            message.chat.id,
            "🚨 處理查詢時發生錯誤，請稍後重試。"
        )

async def handle_image_message(message: TelegramMessage, file_id: str):
    """處理圖片消息"""
    try:
        # 獲取圖片數據
        image_info = await telegram_bot.get_file(file_id)
        if not image_info.get("ok"):
            raise ValueError("Failed to get image file info")

        # 下載圖片
        image_data = await telegram_bot.download_file(image_info["result"]["file_path"])
        
        # 將圖片數據轉換為base64
        image_base64 = base64.b64encode(image_data).decode()

        # 使用AI分析圖片
        analysis = await ai_service.analyze_image(image_base64)
        
        # 發送分析結果
        await telegram_bot.send_message(message.chat.id, analysis)

    except Exception as e:
        logger.error(f"Error handling image message: {str(e)}")
        await telegram_bot.send_message(
            message.chat.id,
            "🚨 處理圖片時發生錯誤，請稍後重試。"
        )

@router.post("/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """處理 Telegram webhook 請求"""
    try:
        data = await request.json()
        
        # 驗證 webhook 請求
        if "message" not in data:
            return {"ok": True}

        message = TelegramMessage.from_webhook(data["message"])

        # 處理圖片消息
        if "photo" in data["message"]:
            # 獲取最高質量的圖片
            file_id = data["message"]["photo"][-1]["file_id"]
            background_tasks.add_task(handle_image_message, message, file_id)
            return {"ok": True}

        # 處理文本消息
        if not message.text:
            return {"ok": True}

        # 檢查是否是查帳請求
        if "查收" in message.text:
            query = telegram_bot.parse_wallet_query(message.text)
            if not query:
                await telegram_bot.send_message(
                    message.chat.id,
                    "⚠️ 格式錯誤！請按照以下格式輸入：\n\n"
                    "查收\n"
                    "錢包地址\n"
                    "金額"
                )
                return {"ok": True}

            # 在背景處理錢包查詢
            background_tasks.add_task(handle_wallet_query, message, query)
            return {"ok": True}

        # 使用 AI 處理其他消息
        ai_response = await ai_service.get_response(message.text)
        await telegram_bot.send_message(message.chat.id, ai_response)

        # 如果消息中包含特定關鍵字，發送對應的貼圖
        stickers = {
            "查收": "CAACAgUAAxkBAAM3Z6BCS_8OxFi3hPqLGSbXA_DGe88AAhQOAAJIVcFWGeRHkOJd6382BA",
            "錯誤": "CAACAgUAAxkBAAICnGe1kMxEm_Yb8sqoLdBrh4wzqacBAAKEDwACp3ugVg-wZAirnX4uNgQ",
            "成功": "CAACAgUAAxkBAAIBx2e1T865MArKuXWmO6v2fI7N3c-DAALSDwACRKowVx4O9BSYF3_zNgQ"
        }

        for keyword, sticker_id in stickers.items():
            if keyword in message.text:
                await telegram_bot.send_sticker(message.chat.id, sticker_id)
                break

        return {"ok": True}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # 在生產環境中，我們不應該暴露具體錯誤信息
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "ok", "service": "telegram-webhook"}