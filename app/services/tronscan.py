from typing import Optional, Dict, Any
import aiohttp
import logging
from datetime import datetime, timedelta
from app.core.config import get_settings
from app.models.transaction import TransactionResponse

logger = logging.getLogger(__name__)
settings = get_settings()

class TronScanAPI:
    def __init__(self):
        self.base_url = settings.TRONSCAN_API_BASE_URL
        self.api_key = settings.TRONSCAN_API_KEY
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/122.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://tronscan.org",
            "DNT": "1",
            "Connection": "keep-alive",
            "Referer": "https://tronscan.org/",
            "TRON-PRO-API-KEY": self.api_key,
            "Cache-Control": "no-cache"
        }

    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        """發送 HTTP 請求到 TronScan API"""
        url = f"{self.base_url}/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"TronScan API error: {response.status} - {await response.text()}")
                        return {"error": {"message": f"API request failed with status {response.status}"}}
                    return await response.json()
        except Exception as e:
            logger.error(f"Error making request to TronScan API: {str(e)}")
            return {"error": {"message": f"API request failed: {str(e)}"}}

    async def get_trc20_transfers(
        self,
        wallet_address: str,
        limit: int = 20,
        hours_ago: int = 96
    ) -> TransactionResponse:
        """獲取指定錢包的 TRC20 代幣轉帳記錄"""
        start_timestamp = int((datetime.now() - timedelta(hours=hours_ago)).timestamp() * 1000)
        end_timestamp = int(datetime.now().timestamp() * 1000)

        params = {
            "limit": limit,
            "start": 0,
            "sort": "-timestamp",
            "count": True,
            "relatedAddress": wallet_address,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp
        }

        result = await self._make_request("filter/trc20/transfers", params)
        return TransactionResponse(**result)

    async def verify_transaction(
        self,
        wallet_address: str,
        expected_amount: float,
        token_decimals: int = 6,  # USDT 默認小數位數
        hours_ago: int = 96
    ) -> Optional[Dict]:
        """驗證特定金額的交易是否存在"""
        transfers = await self.get_trc20_transfers(wallet_address, hours_ago=hours_ago)
        
        if transfers.error:
            return {"verified": False, "error": transfers.error}
            
        if transfers.total == 0:
            return {"verified": False, "reason": "No transactions found"}

        # 轉換期望金額為代幣數量（考慮小數位數）
        expected_quantity = expected_amount * (10 ** token_decimals)
        
        # 檢查交易
        for tx in transfers.token_transfers:
            tx_amount = float(tx.quant) / (10 ** tx.tokenInfo.tokenDecimal)
            if abs(tx_amount - expected_amount) <= 2:  # 允許 2 個單位的誤差
                return {
                    "verified": True,
                    "transaction": tx.dict(),
                    "formatted_amount": tx_amount
                }

        return {"verified": False, "reason": "No matching transaction found"}

tronscan_api = TronScanAPI()