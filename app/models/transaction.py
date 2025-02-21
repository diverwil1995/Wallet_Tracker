from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TokenInfo(BaseModel):
    tokenId: str
    tokenName: str
    tokenAbbr: str
    tokenDecimal: int
    tokenType: str

class Transaction(BaseModel):
    block_ts: int
    from_address: str
    to_address: str
    quant: str
    confirmed: bool
    transaction_id: str
    tokenInfo: TokenInfo
    finalResult: str

class TransactionResponse(BaseModel):
    total: int
    token_transfers: List[Transaction]
    error: Optional[dict] = None

    def format_message(self) -> str:
        """格式化交易信息為消息文本"""
        if self.error:
            return f"🚨 Error: {self.error.get('message', 'Unknown error')}"
        
        if self.total == 0:
            return "📭 No transactions found in the specified timeframe."
            
        messages = []
        for idx, tx in enumerate(self.token_transfers, 1):
            amount = float(tx.quant) / (10 ** tx.tokenInfo.tokenDecimal)
            messages.append(
                f"📝 Transaction #{idx}\n"
                f"💰 Amount: {amount:.2f}\n"
                f"📅 Time: {datetime.fromtimestamp(tx.block_ts/1000).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"🏦 Token: {tx.tokenInfo.tokenName} ({tx.tokenInfo.tokenAbbr})\n"
                f"📤 From: {tx.from_address}\n"
                f"📥 To: {tx.to_address}\n"
                f"📊 Status: {'✅ Confirmed' if tx.confirmed else '⏳ Pending'}\n"
                f"🔗 View: https://tronscan.org/#/transaction/{tx.transaction_id}\n"
            )
        
        return "\n".join(messages)