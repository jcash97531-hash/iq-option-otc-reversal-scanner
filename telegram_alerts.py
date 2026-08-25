import logging
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class TelegramAlerter:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    async def send_reversal_alert(
        self, asset: str, direction: str, candle_count: int, current_price: float
    ):
        """
        Send Telegram alert for detected reversal pattern.
        
        Args:
            asset: Currency pair (e.g., EURUSD)
            direction: Direction of the 6 candles (UP or DOWN)
            candle_count: Number of consecutive candles
            current_price: Current price at detection time
        """
        try:
            message = (
                f"🚨 <b>Reversal Pattern Detected</b>\n\n"
                f"<b>Asset:</b> {asset}\n"
                f"<b>Direction:</b> {direction}\n"
                f"<b>Candles:</b> {candle_count} consecutive\n"
                f"<b>Price:</b> {current_price:.5f}\n"
                f"<b>Time:</b> <i>Check now!</i>"
            )
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="HTML"
            )
            logger.info(f"Alert sent for {asset}: {direction} reversal")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    async def send_connection_status(self, status: str, message: str):
        """Send connection status update."""
        try:
            text = f"<b>{status}</b>\n{message}"
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode="HTML"
            )
        except TelegramError as e:
            logger.error(f"Failed to send status message: {e}")
