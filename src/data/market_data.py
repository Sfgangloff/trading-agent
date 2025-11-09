"""
Market data ingestion layer

Supports multiple data sources (yfinance, polygon, alpaca)
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from abc import ABC, abstractmethod

from src.models import Ticker, OHLCV
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MarketDataProvider(ABC):
    """Abstract base class for market data providers"""

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """Get current ticker data for a symbol"""
        pass

    @abstractmethod
    async def get_historical(
        self, symbol: str, start_date: datetime, end_date: datetime, interval: str = "1d"
    ) -> List[OHLCV]:
        """Get historical OHLCV data"""
        pass

    @abstractmethod
    async def get_multiple_tickers(self, symbols: List[str]) -> Dict[str, Ticker]:
        """Get ticker data for multiple symbols"""
        pass


class YFinanceProvider(MarketDataProvider):
    """Yahoo Finance data provider"""

    def __init__(self):
        logger.info("YFinance provider initialized")

    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """
        Get current ticker data from Yahoo Finance

        Args:
            symbol: Trading symbol (e.g., AAPL, BTC-USD)

        Returns:
            Ticker object or None if error
        """
        try:
            # Run in executor since yfinance is synchronous
            loop = asyncio.get_event_loop()
            ticker_data = await loop.run_in_executor(None, self._fetch_ticker_sync, symbol)
            return ticker_data

        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None

    def _fetch_ticker_sync(self, symbol: str) -> Optional[Ticker]:
        """Synchronous ticker fetch"""
        try:
            ticker = yf.Ticker(symbol)

            # Use faster method - just get current info
            fast_info = ticker.fast_info

            # Get recent history for OHLC data
            history = ticker.history(period="2d")

            if history.empty:
                logger.warning(f"No data available for {symbol}")
                return None

            latest = history.iloc[-1]
            current_price = float(latest["Close"])

            # Get previous close for day change calculation
            if len(history) > 1:
                previous_close = float(history.iloc[-2]["Close"])
            else:
                previous_close = current_price

            # Calculate day change
            day_change = current_price - previous_close
            day_change_percent = (day_change / previous_close * 100) if previous_close > 0 else 0

            return Ticker(
                symbol=symbol,
                timestamp=datetime.utcnow(),
                price=current_price,
                bid=None,  # fast_info doesn't have bid/ask
                ask=None,
                open=float(latest["Open"]) if not pd.isna(latest["Open"]) else None,
                high=float(latest["High"]) if not pd.isna(latest["High"]) else None,
                low=float(latest["Low"]) if not pd.isna(latest["Low"]) else None,
                close=current_price,
                volume=float(latest["Volume"]) if not pd.isna(latest["Volume"]) else None,
                day_change=day_change,
                day_change_percent=day_change_percent,
            )

        except Exception as e:
            logger.error(f"Error in _fetch_ticker_sync for {symbol}: {e}")
            return None

    async def get_historical(
        self, symbol: str, start_date: datetime, end_date: datetime, interval: str = "1d"
    ) -> List[OHLCV]:
        """
        Get historical OHLCV data

        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            interval: Data interval (1m, 5m, 1h, 1d, etc.)

        Returns:
            List of OHLCV data
        """
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                self._fetch_historical_sync,
                symbol,
                start_date,
                end_date,
                interval,
            )
            return data

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []

    def _fetch_historical_sync(
        self, symbol: str, start_date: datetime, end_date: datetime, interval: str
    ) -> List[OHLCV]:
        """Synchronous historical data fetch"""
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(start=start_date, end=end_date, interval=interval)

            if history.empty:
                return []

            ohlcv_list = []
            for timestamp, row in history.iterrows():
                ohlcv = OHLCV(
                    symbol=symbol,
                    timestamp=timestamp.to_pydatetime(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row["Volume"]),
                )
                ohlcv_list.append(ohlcv)

            logger.debug(f"Fetched {len(ohlcv_list)} historical records for {symbol}")
            return ohlcv_list

        except Exception as e:
            logger.error(f"Error in _fetch_historical_sync for {symbol}: {e}")
            return []

    async def get_multiple_tickers(self, symbols: List[str]) -> Dict[str, Ticker]:
        """
        Get ticker data for multiple symbols concurrently

        Args:
            symbols: List of trading symbols

        Returns:
            Dict of {symbol: Ticker}
        """
        tasks = [self.get_ticker(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        tickers = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {symbol}: {result}")
            elif result is not None:
                tickers[symbol] = result

        logger.info(f"Fetched {len(tickers)}/{len(symbols)} tickers")
        return tickers


class MarketDataManager:
    """
    High-level market data manager

    Handles multiple providers and caching
    """

    def __init__(self, provider: str = "yfinance"):
        """
        Initialize market data manager

        Args:
            provider: Data provider name (yfinance, polygon, alpaca)
        """
        self.provider_name = provider

        # Initialize provider
        if provider == "yfinance":
            self.provider = YFinanceProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Simple cache
        self._cache: Dict[str, Ticker] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(seconds=60)  # 1 minute cache

        logger.info(f"MarketDataManager initialized with provider: {provider}")

    async def get_ticker(self, symbol: str, use_cache: bool = True) -> Optional[Ticker]:
        """
        Get ticker with caching

        Args:
            symbol: Trading symbol
            use_cache: Whether to use cached data

        Returns:
            Ticker object or None
        """
        # Check cache
        if use_cache and symbol in self._cache:
            cache_age = datetime.utcnow() - self._cache_timestamp[symbol]
            if cache_age < self._cache_ttl:
                logger.debug(f"Using cached data for {symbol}")
                return self._cache[symbol]

        # Fetch fresh data
        ticker = await self.provider.get_ticker(symbol)

        if ticker:
            self._cache[symbol] = ticker
            self._cache_timestamp[symbol] = datetime.utcnow()

        return ticker

    async def get_multiple_tickers(
        self, symbols: List[str], use_cache: bool = True
    ) -> Dict[str, Ticker]:
        """
        Get multiple tickers with caching

        Args:
            symbols: List of symbols
            use_cache: Whether to use cached data

        Returns:
            Dict of {symbol: Ticker}
        """
        result = {}
        symbols_to_fetch = []

        if use_cache:
            for symbol in symbols:
                if symbol in self._cache:
                    cache_age = datetime.utcnow() - self._cache_timestamp[symbol]
                    if cache_age < self._cache_ttl:
                        result[symbol] = self._cache[symbol]
                        continue
                symbols_to_fetch.append(symbol)
        else:
            symbols_to_fetch = symbols

        # Fetch missing symbols
        if symbols_to_fetch:
            fresh_data = await self.provider.get_multiple_tickers(symbols_to_fetch)
            result.update(fresh_data)

            # Update cache
            for symbol, ticker in fresh_data.items():
                self._cache[symbol] = ticker
                self._cache_timestamp[symbol] = datetime.utcnow()

        return result

    async def get_historical(
        self, symbol: str, days: int = 30, interval: str = "1d"
    ) -> List[OHLCV]:
        """
        Get historical data

        Args:
            symbol: Trading symbol
            days: Number of days of history
            interval: Data interval

        Returns:
            List of OHLCV data
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        return await self.provider.get_historical(symbol, start_date, end_date, interval)

    def clear_cache(self) -> None:
        """Clear the data cache"""
        self._cache.clear()
        self._cache_timestamp.clear()
        logger.info("Market data cache cleared")
