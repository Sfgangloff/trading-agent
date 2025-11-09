"""
Performance tracking models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    """Performance metrics for an algorithm"""

    algorithm_id: str = Field(..., description="Algorithm identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Time period
    period_start: datetime
    period_end: datetime
    days: int = Field(..., ge=0, description="Number of days evaluated")

    # Returns
    total_return: float = Field(..., description="Total return (absolute $)")
    total_return_percent: float = Field(..., description="Total return percentage")
    annualized_return: Optional[float] = Field(None, description="Annualized return percentage")

    # Trading activity
    total_trades: int = Field(default=0, ge=0)
    winning_trades: int = Field(default=0, ge=0)
    losing_trades: int = Field(default=0, ge=0)

    # Win rate
    win_rate: float = Field(default=0.0, ge=0, le=1, description="Percentage of winning trades")

    # Profit metrics
    average_profit_per_trade: float = Field(default=0.0)
    largest_win: float = Field(default=0.0)
    largest_loss: float = Field(default=0.0)

    # Risk metrics
    max_drawdown: float = Field(default=0.0, le=0, description="Maximum drawdown (negative value)")
    max_drawdown_percent: float = Field(default=0.0, le=0, description="Maximum drawdown percentage")

    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    sortino_ratio: Optional[float] = Field(None, description="Sortino ratio")
    calmar_ratio: Optional[float] = Field(None, description="Calmar ratio")

    # Volatility
    volatility: Optional[float] = Field(None, ge=0, description="Return volatility (standard deviation)")

    # Portfolio metrics
    starting_capital: float = Field(..., gt=0)
    ending_capital: float = Field(..., gt=0)
    peak_capital: float = Field(..., gt=0, description="Highest portfolio value reached")

    # Costs
    total_commissions: float = Field(default=0.0, ge=0)
    total_slippage: float = Field(default=0.0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "algorithm_id": "sma_crossover_v1",
                "timestamp": "2025-11-09T16:30:00",
                "period_start": "2025-11-08T09:30:00",
                "period_end": "2025-11-09T16:00:00",
                "days": 1,
                "total_return": 5.50,
                "total_return_percent": 5.5,
                "annualized_return": None,
                "total_trades": 3,
                "winning_trades": 2,
                "losing_trades": 1,
                "win_rate": 0.67,
                "average_profit_per_trade": 1.83,
                "largest_win": 4.50,
                "largest_loss": -1.50,
                "max_drawdown": -2.00,
                "max_drawdown_percent": -2.0,
                "sharpe_ratio": 1.5,
                "sortino_ratio": 2.1,
                "calmar_ratio": 2.75,
                "volatility": 3.2,
                "starting_capital": 100.0,
                "ending_capital": 105.50,
                "peak_capital": 107.00,
                "total_commissions": 0.53,
                "total_slippage": 0.15
            }
        }


class PortfolioSnapshot(BaseModel):
    """Snapshot of portfolio state at a point in time"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Capital
    cash: float = Field(..., ge=0)
    positions_value: float = Field(default=0.0, ge=0)
    total_value: float = Field(..., gt=0)

    # Performance
    total_pnl: float = Field(default=0.0)
    total_pnl_percent: float = Field(default=0.0)

    # Open positions count
    num_positions: int = Field(default=0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-09T16:00:00",
                "cash": 50.25,
                "positions_value": 175.50,
                "total_value": 225.75,
                "total_pnl": 125.75,
                "total_pnl_percent": 125.75,
                "num_positions": 2
            }
        }


class AlgorithmRanking(BaseModel):
    """Algorithm ranking for evolution selection"""

    algorithm_id: str
    name: str
    rank: int = Field(..., ge=1)

    # Key metrics for ranking
    total_return_percent: float
    sharpe_ratio: Optional[float] = None
    win_rate: float
    max_drawdown_percent: float

    # Composite score
    score: float = Field(..., description="Weighted composite score for ranking")

    class Config:
        json_schema_extra = {
            "example": {
                "algorithm_id": "sma_crossover_v1",
                "name": "Simple Moving Average Crossover",
                "rank": 1,
                "total_return_percent": 5.5,
                "sharpe_ratio": 1.5,
                "win_rate": 0.67,
                "max_drawdown_percent": -2.0,
                "score": 8.75
            }
        }
