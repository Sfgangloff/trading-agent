"""
Simple Moving Average (SMA) Crossover Strategy

Buy when short-term SMA crosses above long-term SMA
Sell when short-term SMA crosses below long-term SMA
"""

from typing import Optional, List
import pandas as pd

from src.models import Signal, Ticker, SentimentData, OHLCV, SignalType
from .base_algorithm import TradingAlgorithm
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SMAcrossover(TradingAlgorithm):
    """
    SMA Crossover trading algorithm

    Parameters:
        short_window: Period for short-term SMA (default: 20)
        long_window: Period for long-term SMA (default: 50)
        confidence_threshold: Minimum confidence to generate signal (default: 0.7)
    """

    def __init__(
        self,
        algorithm_id: str = "sma_crossover_v1",
        short_window: int = 20,
        long_window: int = 50,
    ):
        super().__init__(
            algorithm_id=algorithm_id,
            name="SMA Crossover Strategy",
            parameters={
                "short_window": short_window,
                "long_window": long_window,
                "confidence_threshold": 0.7,
            },
        )

    def analyze(
        self,
        symbol: str,
        current_data: Ticker,
        historical_data: List[OHLCV],
        sentiment: Optional[SentimentData] = None,
    ) -> Optional[Signal]:
        """
        Analyze using SMA crossover strategy

        Args:
            symbol: Trading symbol
            current_data: Current ticker data
            historical_data: Historical OHLCV data
            sentiment: Sentiment data (optional)

        Returns:
            Signal or None
        """
        short_window = self.get_parameter("short_window", 20)
        long_window = self.get_parameter("long_window", 50)

        # Need enough historical data
        if len(historical_data) < long_window + 2:
            logger.debug(f"{self.name}: Insufficient data for {symbol} (need {long_window + 2}, have {len(historical_data)})")
            return None

        try:
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "close": ohlcv.close,
                    "timestamp": ohlcv.timestamp,
                }
                for ohlcv in historical_data
            ])

            # Calculate SMAs
            df["sma_short"] = df["close"].rolling(window=short_window).mean()
            df["sma_long"] = df["close"].rolling(window=long_window).mean()

            # Get last two rows to detect crossover
            if len(df) < 2:
                return None

            prev = df.iloc[-2]
            curr = df.iloc[-1]

            # Check for valid SMAs
            if pd.isna(prev["sma_short"]) or pd.isna(prev["sma_long"]):
                return None
            if pd.isna(curr["sma_short"]) or pd.isna(curr["sma_long"]):
                return None

            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No crossover detected"

            # Bullish crossover: short SMA crosses above long SMA
            if prev["sma_short"] <= prev["sma_long"] and curr["sma_short"] > curr["sma_long"]:
                signal_type = SignalType.BUY
                # Confidence based on how decisive the crossover is
                crossover_magnitude = (curr["sma_short"] - curr["sma_long"]) / curr["sma_long"]
                confidence = min(0.7 + abs(crossover_magnitude) * 100, 0.95)
                reason = f"Bullish SMA crossover: {short_window}-day SMA crossed above {long_window}-day SMA"

                # Boost confidence if sentiment is positive
                if sentiment and sentiment.overall_sentiment and sentiment.overall_sentiment > 0.3:
                    confidence = min(confidence + 0.1, 0.99)
                    reason += " (positive sentiment)"

            # Bearish crossover: short SMA crosses below long SMA
            elif prev["sma_short"] >= prev["sma_long"] and curr["sma_short"] < curr["sma_long"]:
                signal_type = SignalType.SELL
                crossover_magnitude = (curr["sma_long"] - curr["sma_short"]) / curr["sma_short"]
                confidence = min(0.7 + abs(crossover_magnitude) * 100, 0.95)
                reason = f"Bearish SMA crossover: {short_window}-day SMA crossed below {long_window}-day SMA"

                # Boost confidence if sentiment is negative
                if sentiment and sentiment.overall_sentiment and sentiment.overall_sentiment < -0.3:
                    confidence = min(confidence + 0.1, 0.99)
                    reason += " (negative sentiment)"

            # Only generate signal if confidence meets threshold
            confidence_threshold = self.get_parameter("confidence_threshold", 0.7)
            if signal_type == SignalType.HOLD or confidence < confidence_threshold:
                return None

            # Create signal
            signal = Signal(
                algorithm_id=self.algorithm_id,
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                reason=reason,
            )

            logger.info(f"{self.name}: Generated {signal_type} signal for {symbol} (confidence: {confidence:.2f})")
            return signal

        except Exception as e:
            logger.error(f"{self.name}: Error analyzing {symbol}: {e}")
            return None
