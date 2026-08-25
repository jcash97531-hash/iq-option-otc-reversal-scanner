import logging
import time
from typing import Optional, Dict, List
from iqoptionapi.stable_api import IQOptionAPI

logger = logging.getLogger(__name__)


class IQOptionClient:
    """
    Wrapper around IQ Option API for efficient candle fetching.
    Uses the iqoptionapi library which offers the best performance.
    """

    def __init__(self, email: str, password: str):
        self.api = IQOptionAPI(email=email, password=password, host="iqoption.com")
        self.connected = False

    def connect(self) -> bool:
        """Connect to IQ Option servers."""
        try:
            check_result = self.api.check_connect()
            if check_result:
                self.connected = True
                logger.info("Connected to IQ Option")
                return True
            else:
                logger.error("Failed to connect to IQ Option")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from IQ Option."""
        try:
            self.api.logout()
            self.connected = False
            logger.info("Disconnected from IQ Option")
        except Exception as e:
            logger.warning(f"Disconnect error: {e}")

    def get_candle(
        self, asset: str, timeframe: int
    ) -> Optional[Dict]:
        """
        Get the latest candle for an asset.
        
        Args:
            asset: Currency pair (e.g., 'EURUSD')
            timeframe: Candle timeframe in minutes (1, 5, 15, 30, 60)
        
        Returns:
            Dict with keys: open, close, high, low, time
            or None if failed
        """
        try:
            # IQ Option candle format
            candles = self.api.get_candles(asset, timeframe, 2, time.time())
            
            if candles and len(candles) > 0:
                # Get the most recent completed candle (not the current one)
                candle = candles[-2] if len(candles) >= 2 else candles[-1]
                
                return {
                    "open": candle["open"],
                    "close": candle["close"],
                    "high": candle["max"],
                    "low": candle["min"],
                    "time": candle["from"]
                }
            else:
                logger.warning(f"No candles returned for {asset}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching candle for {asset}: {e}")
            return None

    def get_multiple_candles(
        self, asset: str, timeframe: int, count: int = 10
    ) -> Optional[List[Dict]]:
        """
        Get multiple historical candles for an asset.
        
        Args:
            asset: Currency pair
            timeframe: Candle timeframe in minutes
            count: Number of candles to retrieve
        
        Returns:
            List of candle dicts or None if failed
        """
        try:
            candles = self.api.get_candles(asset, timeframe, count + 1, time.time())
            
            if candles:
                result = []
                for candle in candles[:-1]:  # Exclude current incomplete candle
                    result.append({
                        "open": candle["open"],
                        "close": candle["close"],
                        "high": candle["max"],
                        "low": candle["min"],
                        "time": candle["from"]
                    })
                return result
            else:
                logger.warning(f"No historical candles for {asset}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching historical candles for {asset}: {e}")
            return None

    def get_asset_price(self, asset: str) -> Optional[float]:
        """Get current spot price for an asset."""
        try:
            result = self.api.get_digital_spot_profit_margin(asset)
            if result:
                return result["bid"]
            return None
        except Exception as e:
            logger.error(f"Error getting price for {asset}: {e}")
            return None

    def is_connected(self) -> bool:
        """Check if still connected."""
        return self.connected and self.api.check_connect()
