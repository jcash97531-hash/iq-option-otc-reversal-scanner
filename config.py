import os
from dotenv import load_dotenv

load_dotenv()

# IQ Option Credentials
IQ_OPTION_EMAIL = os.getenv("IQ_OPTION_EMAIL")
IQ_OPTION_PASSWORD = os.getenv("IQ_OPTION_PASSWORD")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Scanner Configuration
ASSETS = os.getenv("ASSETS", "EURUSD,GBPUSD,USDJPY").split(",")
TIMEFRAME = int(os.getenv("TIMEFRAME", 1))  # minutes
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 10))  # seconds
REVERSAL_LENGTH = int(os.getenv("REVERSAL_LENGTH", 6))  # consecutive candles

# Validation
if not IQ_OPTION_EMAIL or not IQ_OPTION_PASSWORD:
    raise ValueError("Missing IQ Option credentials in .env file")
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Missing Telegram credentials in .env file")
