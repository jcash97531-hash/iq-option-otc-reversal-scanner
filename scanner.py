import asyncio
import logging
import time
from typing import Set
from iq_client import IQOptionClient
from reversal_detector import ReversalDetector
from telegram_alerts import TelegramAlerter
from config import (
    IQ_OPTION_EMAIL,
    IQ_OPTION_PASSWORD,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    ASSETS,
    TIMEFRAME,
    CHECK_INTERVAL,
    REVERSAL_LENGTH,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scanner.log")
    ]
)
logger = logging.getLogger(__name__)


class OTCReversalScanner:
    """Main scanner orchestrator."""

    def __init__(self):
        self.iq_client = IQOptionClient(IQ_OPTION_EMAIL, IQ_OPTION_PASSWORD)
        self.detector = ReversalDetector(reversal_length=REVERSAL_LENGTH)
        self.alerter = TelegramAlerter(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.detected_reversals: Set[str] = set()  # Track detected reversals to avoid duplicates
        self.running = False

    async def initialize(self) -> bool:
        """Initialize the scanner."""
        logger.info("Initializing OTC Reversal Scanner...")
        
        # Connect to IQ Option
        if not self.iq_client.connect():
            logger.error("Failed to connect to IQ Option")
            return False
        
        # Load initial candles for all assets
        logger.info(f"Loading initial candles for {len(ASSETS)} assets...")
        for asset in ASSETS:
            candles = self.iq_client.get_multiple_candles(
                asset, TIMEFRAME, count=REVERSAL_LENGTH + 5
            )
            
            if candles:
                for candle in candles:
                    self.detector.update_candle(
                        asset,
                        candle["open"],
                        candle["close"],
                        candle["high"],
                        candle["low"]
                    )
                logger.info(f"Loaded {len(candles)} candles for {asset}")
            else:
                logger.warning(f"Failed to load candles for {asset}")
        
        await self.alerter.send_connection_status(
            "✅ Scanner Started",
            f"Monitoring {len(ASSETS)} assets\nTimeframe: {TIMEFRAME}m\nCheck interval: {CHECK_INTERVAL}s"
        )
        
        logger.info("Scanner initialized successfully")
        return True

    async def check_asset(self, asset: str):
        """Check a single asset for reversals."""
        try:
            candle = self.iq_client.get_candle(asset, TIMEFRAME)
            
            if candle:
                # Update detector with new candle
                self.detector.update_candle(
                    asset,
                    candle["open"],
                    candle["close"],
                    candle["high"],
                    candle["low"]
                )
                
                # Check for reversal
                result = self.detector.detect_reversal(asset)
                
                if result:
                    direction, candle_count = result
                    reversal_key = f"{asset}_{direction}"
                    
                    # Only alert once per reversal pattern
                    if reversal_key not in self.detected_reversals:
                        current_price = self.detector.get_current_price(asset)
                        
                        logger.info(
                            f"🚨 Reversal detected: {asset} {direction} "
                            f"({candle_count} candles) @ {current_price:.5f}"
                        )
                        
                        await self.alerter.send_reversal_alert(
                            asset, direction, candle_count, current_price
                        )
                        
                        self.detected_reversals.add(reversal_key)
                        
                        # Remove opposite direction from detected set (it's no longer valid)
                        opposite = "DOWN" if direction == "UP" else "UP"
                        self.detected_reversals.discard(f"{asset}_{opposite}")
                
                # Log stats for debugging
                stats = self.detector.get_stats(asset)
                if stats:
                    logger.debug(f"Stats {asset}: {stats}")
                    
        except Exception as e:
            logger.error(f"Error checking asset {asset}: {e}")

    async def scan_loop(self):
        """Main scanning loop."""
        self.running = True
        logger.info("Starting scan loop...")
        
        while self.running:
            try:
                # Check if still connected
                if not self.iq_client.is_connected():
                    logger.warning("Connection lost, attempting reconnect...")
                    if not self.iq_client.connect():
                        await self.alerter.send_connection_status(
                            "⚠️ Connection Lost",
                            "Scanner will continue attempting to reconnect..."
                        )
                        await asyncio.sleep(10)
                        continue
                
                # Check all assets concurrently
                tasks = [self.check_asset(asset) for asset in ASSETS]
                await asyncio.gather(*tasks)
                
                # Wait before next check
                await asyncio.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Scan loop interrupted")
                break
            except Exception as e:
                logger.error(f"Error in scan loop: {e}")
                await asyncio.sleep(CHECK_INTERVAL)
        
        self.running = False

    async def shutdown(self):
        """Gracefully shutdown the scanner."""
        logger.info("Shutting down scanner...")
        self.running = False
        self.iq_client.disconnect()
        await self.alerter.send_connection_status(
            "⛔ Scanner Stopped",
            "Monitoring ended"
        )
        logger.info("Scanner shutdown complete")


async def main():
    """Main entry point."""
    scanner = OTCReversalScanner()
    
    try:
        # Initialize
        if not await scanner.initialize():
            logger.error("Failed to initialize scanner")
            return
        
        # Run scanner
        await scanner.scan_loop()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        await scanner.alerter.send_connection_status(
            "❌ Scanner Error",
            f"Critical error occurred: {str(e)}"
        )
    finally:
        await scanner.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
