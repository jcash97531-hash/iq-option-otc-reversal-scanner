import logging
import asyncio
import json
import time
from typing import Optional, Dict, List
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class IQOptionClient:
    """
    IQ Option HTTP API client for real candle data.
    Uses REST API endpoints to fetch real historical and current candles.
    """

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.connected = False
        self.session_id = None
        self.base_url = "https://iqoption.com/api"
        self.session = requests.Session()
        logger.info(f"IQ Option HTTP client initialized for {email}")

    def connect(self) -> bool:
        """Authenticate with IQ Option."""
        try:
            # Login endpoint
            login_url = f"{self.base_url}/login"
            
            payload = {
                "email": self.email,
                "password": self.password
            }
            
            response = self.session.post(login_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("isSuccessful"):
                    self.session_id = data.get("session_id")
                    self.connected = True
                    logger.info(f"Authenticated to IQ Option, session: {self.session_id}")
                    return True
                else:
                    logger.error(f"Login failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                logger.error(f"Login HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Logout from IQ Option."""
        try:
            if self.session_id:
                logout_url = f"{self.base_url}/logout"
                self.session.post(logout_url, json={"session_id": self.session_id})
            self.connected = False
            logger.info("Disconnected from IQ Option")
        except Exception as e:
            logger.warning(f"Disconnect error: {e}")

    def get_candle(
        self, asset: str, timeframe: int
    ) -> Optional[Dict]:
        """
        Get the latest candle for an asset via HTTP API.
        
        Args:
            asset: Currency pair (e.g., 'EURUSD-OTC')
            timeframe: Candle timeframe in minutes (1, 5, 15, 30, 60)
        
        Returns:
            Dict with keys: open, close, high, low, time
            or None if failed
        """
        try:
            if not self.connected:
                return None
            
            # Get candles endpoint
            candles_url = f"{self.base_url}/getcandles"
            
            current_time = int(time.time())
            
            params = {
                "session_id": self.session_id,
                "asset": asset,
                "size": timeframe,  # timeframe in minutes
                "count": 2,  # Get last 2 candles
                "end_time": current_time
            }
            
            response = self.session.get(candles_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("isSuccessful") and data.get("candles"):
                    candles = data["candles"]
                    # Get the most recent completed candle
                    candle = candles[-2] if len(candles) >= 2 else candles[-1]
                    
                    return {
                        "open": candle.get("o"),
                        "close": candle.get("c"),
                        "high": candle.get("h"),
                        "low": candle.get("l"),
                        "time": candle.get("t")
                    }
                else:
                    logger.warning(f"No candles returned for {asset}: {data.get('message', 'Unknown error')}")
                    return None
            else:
                logger.error(f"Candles HTTP error {response.status_code}: {response.text}")
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
            if not self.connected:
                return None
            
            candles_url = f"{self.base_url}/getcandles"
            
            current_time = int(time.time())
            
            params = {
                "session_id": self.session_id,
                "asset": asset,
                "size": timeframe,
                "count": count + 1,
                "end_time": current_time
            }
            
            response = self.session.get(candles_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("isSuccessful") and data.get("candles"):
                    result = []
                    for candle in data["candles"][:-1]:  # Exclude current incomplete candle
                        result.append({
                            "open": candle.get("o"),
                            "close": candle.get("c"),
                            "high": candle.get("h"),
                            "low": candle.get("l"),
                            "time": candle.get("t")
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
            candle = self.get_candle(asset, 1)
            if candle:
                return candle["close"]
            return None
        except Exception as e:
            logger.error(f"Error getting price for {asset}: {e}")
            return None

    def is_connected(self) -> bool:
        """Check if still connected."""
        return self.connected and self.session_id is not None
