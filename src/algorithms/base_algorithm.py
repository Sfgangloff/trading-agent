"""
Base class for trading algorithms
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.models import Signal, Ticker, SentimentData, OHLCV
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TradingAlgorithm(ABC):
    """
    Abstract base class for trading algorithms

    All trading algorithms must inherit from this class and implement
    the analyze() method
    """

    def __init__(self, algorithm_id: str, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize trading algorithm

        Args:
            algorithm_id: Unique algorithm identifier
            name: Human-readable name
            parameters: Algorithm-specific parameters
        """
        self.algorithm_id = algorithm_id
        self.name = name
        self.parameters = parameters or {}

        # Historical data storage (for algorithms that need it)
        self.price_history: Dict[str, List[OHLCV]] = {}

        logger.info(f"Algorithm initialized: {name} ({algorithm_id})")

    @abstractmethod
    def analyze(
        self,
        symbol: str,
        current_data: Ticker,
        historical_data: List[OHLCV],
        sentiment: Optional[SentimentData] = None,
    ) -> Optional[Signal]:
        """
        Analyze market data and generate trading signal

        Args:
            symbol: Trading symbol
            current_data: Current ticker data
            historical_data: Historical OHLCV data
            sentiment: Sentiment data (optional)

        Returns:
            Signal object (BUY/SELL/HOLD) or None
        """
        pass

    def update_history(self, symbol: str, data: List[OHLCV]) -> None:
        """
        Update historical data for a symbol

        Args:
            symbol: Trading symbol
            data: Historical OHLCV data
        """
        self.price_history[symbol] = data

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """
        Get algorithm parameter

        Args:
            key: Parameter key
            default: Default value if not found

        Returns:
            Parameter value
        """
        return self.parameters.get(key, default)

    def set_parameter(self, key: str, value: Any) -> None:
        """
        Set algorithm parameter

        Args:
            key: Parameter key
            value: Parameter value
        """
        self.parameters[key] = value
        logger.debug(f"{self.name}: Set parameter {key} = {value}")

    def __str__(self) -> str:
        return f"{self.name} ({self.algorithm_id})"

    def __repr__(self) -> str:
        return f"TradingAlgorithm(id={self.algorithm_id}, name={self.name})"
