import logging
from typing import List, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class ReversalDetector:
    """
    Detects reversal patterns based on consecutive candles in one direction.
    
    A reversal is detected when 6 consecutive candles move in the same direction
    (all up or all down).
    """

    def __init__(self, reversal_length: int = 6):
        self.reversal_length = reversal_length
        self.candle_history = {}  # asset -> list of (open, close, high, low)

    def update_candle(
        self, asset: str, open_price: float, close_price: float, 
        high_price: float, low_price: float
    ):
        """Record a new candle for an asset."""
        if asset not in self.candle_history:
            self.candle_history[asset] = []
        
        self.candle_history[asset].append({
            "open": open_price,
            "close": close_price,
            "high": high_price,
            "low": low_price
        })
        
        # Keep only last 20 candles to save memory
        if len(self.candle_history[asset]) > 20:
            self.candle_history[asset] = self.candle_history[asset][-20:]

    def detect_reversal(self, asset: str) -> Optional[Tuple[str, int]]:
        """
        Detect if an asset has a reversal pattern.
        
        Returns:
            Tuple of (direction, candle_count) where direction is 'UP' or 'DOWN'
            Returns None if no reversal detected
        """
        if asset not in self.candle_history:
            return None
        
        candles = self.candle_history[asset]
        if len(candles) < self.reversal_length:
            return None
        
        # Check the last N candles
        recent = candles[-self.reversal_length:]
        
        # Determine direction: UP if close > open, DOWN if close < open
        directions = []
        for candle in recent:
            if candle["close"] > candle["open"]:
                directions.append("UP")
            elif candle["close"] < candle["open"]:
                directions.append("DOWN")
            else:
                # Doji/neutral candle, consider it continuation of trend
                if directions:
                    directions.append(directions[-1])
                else:
                    return None
        
        # Check if all directions are the same
        if all(d == directions[0] for d in directions):
            return (directions[0], len(recent))
        
        return None

    def get_candle_direction(self, asset: str, index: int = -1) -> Optional[str]:
        """Get direction of a specific candle (UP or DOWN)."""
        if asset not in self.candle_history:
            return None
        
        if index >= len(self.candle_history[asset]):
            return None
        
        candle = self.candle_history[asset][index]
        if candle["close"] > candle["open"]:
            return "UP"
        elif candle["close"] < candle["open"]:
            return "DOWN"
        else:
            return "DOJI"

    def get_current_price(self, asset: str) -> Optional[float]:
        """Get the current (close) price of the latest candle."""
        if asset not in self.candle_history or not self.candle_history[asset]:
            return None
        
        return self.candle_history[asset][-1]["close"]

    def clear_history(self, asset: str):
        """Clear candle history for an asset."""
        if asset in self.candle_history:
            self.candle_history[asset] = []

    def get_stats(self, asset: str) -> dict:
        """Get statistics about candle history for debugging."""
        if asset not in self.candle_history:
            return {}
        
        candles = self.candle_history[asset]
        if not candles:
            return {}
        
        latest = candles[-1]
        return {
            "asset": asset,
            "candles_stored": len(candles),
            "latest_close": latest["close"],
            "latest_open": latest["open"],
            "latest_direction": "UP" if latest["close"] > latest["open"] else "DOWN"
        }
