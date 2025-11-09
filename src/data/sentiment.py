"""
Sentiment data provider

Aggregates sentiment from various sources
"""

from typing import Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp

from src.models import SentimentData
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentProvider:
    """
    Sentiment data aggregator

    Combines data from:
    - Fear & Greed Index
    - News sentiment
    - Social sentiment (future)
    """

    def __init__(self):
        self._cache: Optional[SentimentData] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        logger.info("SentimentProvider initialized")

    async def get_fear_greed_index(self) -> Optional[float]:
        """
        Get Fear & Greed Index from Alternative.me (crypto)

        Returns:
            Index value (0-100) or None
        """
        try:
            url = "https://api.alternative.me/fng/"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "data" in data and len(data["data"]) > 0:
                            value = float(data["data"][0]["value"])
                            logger.debug(f"Fear & Greed Index: {value}")
                            return value

            return None

        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
            return None

    async def get_sentiment(self) -> SentimentData:
        """
        Get aggregated sentiment data

        Returns:
            SentimentData object
        """
        # Check cache
        if self._cache and self._cache_timestamp:
            cache_age = datetime.utcnow() - self._cache_timestamp
            if cache_age < self._cache_ttl:
                logger.debug("Using cached sentiment data")
                return self._cache

        # Fetch fresh data
        try:
            # Get Fear & Greed Index
            fear_greed = await self.get_fear_greed_index()

            # Calculate overall sentiment
            # Convert Fear & Greed (0-100) to -1 to 1 scale
            overall_sentiment = None
            if fear_greed is not None:
                # 0 = extreme fear (-1), 50 = neutral (0), 100 = extreme greed (1)
                overall_sentiment = (fear_greed - 50) / 50

            sentiment_data = SentimentData(
                timestamp=datetime.utcnow(),
                fear_greed_index=fear_greed,
                news_sentiment=None,  # To be implemented
                social_sentiment=None,  # To be implemented
                vix=None,  # To be implemented
                overall_sentiment=overall_sentiment,
            )

            # Update cache
            self._cache = sentiment_data
            self._cache_timestamp = datetime.utcnow()

            logger.info(f"Sentiment fetched - F&G: {fear_greed}, Overall: {overall_sentiment:.2f}" if overall_sentiment else "Sentiment fetched - limited data")
            return sentiment_data

        except Exception as e:
            logger.error(f"Error getting sentiment data: {e}")

            # Return neutral sentiment on error
            return SentimentData(
                timestamp=datetime.utcnow(),
                overall_sentiment=0.0,
            )

    def clear_cache(self) -> None:
        """Clear sentiment cache"""
        self._cache = None
        self._cache_timestamp = None
        logger.info("Sentiment cache cleared")
