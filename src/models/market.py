"""
Market data models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Ticker(BaseModel):
    """Market ticker data model"""

    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, BTC-USD)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Price data
    price: float = Field(..., gt=0, description="Current/last price")
    bid: Optional[float] = Field(None, gt=0, description="Bid price")
    ask: Optional[float] = Field(None, gt=0, description="Ask price")

    # OHLC data
    open: Optional[float] = Field(None, gt=0, description="Open price")
    high: Optional[float] = Field(None, gt=0, description="High price")
    low: Optional[float] = Field(None, gt=0, description="Low price")
    close: Optional[float] = Field(None, gt=0, description="Close price")

    # Volume
    volume: Optional[float] = Field(None, ge=0, description="Trading volume")

    # Additional metrics
    day_change: Optional[float] = Field(None, description="Price change from previous close")
    day_change_percent: Optional[float] = Field(None, description="Percentage change")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "timestamp": "2025-11-09T10:30:00",
                "price": 175.50,
                "bid": 175.48,
                "ask": 175.52,
                "open": 174.00,
                "high": 176.00,
                "low": 173.50,
                "close": 175.50,
                "volume": 1500000,
                "day_change": 1.50,
                "day_change_percent": 0.86
            }
        }


class SentimentData(BaseModel):
    """Market sentiment data model"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Sentiment scores (normalized -1 to 1 or 0 to 100)
    fear_greed_index: Optional[float] = Field(None, ge=0, le=100, description="Fear & Greed Index (0-100)")
    news_sentiment: Optional[float] = Field(None, ge=-1, le=1, description="News sentiment (-1 to 1)")
    social_sentiment: Optional[float] = Field(None, ge=-1, le=1, description="Social media sentiment (-1 to 1)")

    # Volatility
    vix: Optional[float] = Field(None, ge=0, description="VIX volatility index")

    # Aggregated sentiment
    overall_sentiment: Optional[float] = Field(None, ge=-1, le=1, description="Weighted overall sentiment")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-09T10:30:00",
                "fear_greed_index": 65,
                "news_sentiment": 0.3,
                "social_sentiment": 0.1,
                "vix": 18.5,
                "overall_sentiment": 0.25
            }
        }


class OHLCV(BaseModel):
    """OHLCV candlestick data"""

    symbol: str
    timestamp: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float = Field(..., ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "timestamp": "2025-11-09T10:30:00",
                "open": 174.00,
                "high": 176.00,
                "low": 173.50,
                "close": 175.50,
                "volume": 1500000
            }
        }
