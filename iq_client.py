import logging
import time
from typing import Optional, Dict, List
from iqoptionapi.api import IQOptionAPI

logger = logging.getLogger(__name__)


class IQOptionClient:
    """
    Wrapper around IQ Option API for efficient candle fetching.
    Uses the iqoptionapi library which offers the best performance.
    """

    def __init__(self, email: str, password: str):
        self.api = IQOptionAPI(username=email, password=password)
        self.connected = False

    def connect(self) -> bool:
        """Connect to IQ Option servers."""
        try:
            check_result = self.api.connect()
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
            self.api.close()
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
            # IQ Option candle format - get last 2 candles, return the older one
            candles = self.api.get_candles(asset, timeframe, 2)
            
            if candles and len(candles) > 0:
                # Get the most recent completed candle (not the current one)
                candle = candles[-2] if len(candles) >= 2 else candles[-1]
                
                return {
                    "open": candle.get("open") or candle.get("o"),
                    "close": candle.get("close") or candle.get("c"),
                    "high": candle.get("high") or candle.get("max") or candle.get("h"),
                    "low": candle.get("low") or candle.get("min") or candle.get("l"),
                    "time": candle.get("time") or candle.get("from")
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
            candles = self.api.get_candles(asset, timeframe, count + 1)
            
            if candles:
                result = []
                for candle in candles[:-1]:  # Exclude current incomplete candle
                    result.append({
                        "open": candle.get("open") or candle.get("o"),
                        "close": candle.get("close") or candle.get("c"),
                        "high": candle.get("high") or candle.get("max") or candle.get("h"),
                        "low": candle.get("low") or candle.get("min") or candle.get("l"),
                        "time": candle.get("time") or candle.get("from")
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
            # For v0.5, we can get the latest candle and use close price
            candle = self.get_candle(asset, 1)
            if candle:
                return candle["close"]
            return None
        except Exception as e:
            logger.error(f"Error getting price for {asset}: {e}")
            return None

    def is_connected(self) -> bool:
        """Check if still connected."""
        try:
            return self.connected and self.api.check_connect()
        except:
            return False
