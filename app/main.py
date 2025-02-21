from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import Settings
from app.api.routes import telegram, health
import logging

# 初始化設定
settings = Settings()
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Wallet Tracker API",
    description="Telegram Bot for tracking wallet transactions",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由設定
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(telegram.router, prefix="/webhook", tags=["telegram"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    # 初始化各項服務
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")
    # 清理資源