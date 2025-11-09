"""
Trade and order models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .base import OrderType, OrderStatus, PositionSide


class Order(BaseModel):
    """Order model"""

    order_id: str = Field(..., description="Unique order identifier")
    algorithm_id: str = Field(..., description="Algorithm that generated the order")
    symbol: str = Field(..., description="Trading symbol")

    order_type: OrderType = Field(..., description="MARKET or LIMIT")
    side: PositionSide = Field(..., description="LONG or SHORT")

    quantity: float = Field(..., gt=0, description="Number of shares/units")

    # Pricing
    limit_price: Optional[float] = Field(None, gt=0, description="Limit price for limit orders")
    filled_price: Optional[float] = Field(None, gt=0, description="Actual execution price")

    # Status
    status: OrderStatus = Field(default=OrderStatus.PENDING)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    filled_at: Optional[datetime] = Field(None)

    # Costs
    commission: float = Field(default=0.0, ge=0)
    slippage: float = Field(default=0.0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD-123456",
                "algorithm_id": "sma_crossover_v1",
                "symbol": "AAPL",
                "order_type": "MARKET",
                "side": "LONG",
                "quantity": 10,
                "limit_price": None,
                "filled_price": 175.50,
                "status": "FILLED",
                "created_at": "2025-11-09T10:30:00",
                "filled_at": "2025-11-09T10:30:05",
                "commission": 0.175,
                "slippage": 0.05
            }
        }


class Trade(BaseModel):
    """Completed trade (buy + sell pair)"""

    trade_id: str = Field(..., description="Unique trade identifier")
    algorithm_id: str = Field(..., description="Algorithm that executed the trade")
    symbol: str = Field(..., description="Trading symbol")

    # Entry
    entry_order_id: str
    entry_price: float = Field(..., gt=0)
    entry_time: datetime
    entry_quantity: float = Field(..., gt=0)

    # Exit
    exit_order_id: Optional[str] = Field(None)
    exit_price: Optional[float] = Field(None, gt=0)
    exit_time: Optional[datetime] = Field(None)
    exit_quantity: Optional[float] = Field(None, gt=0)

    # P&L
    gross_pnl: Optional[float] = Field(None, description="Gross profit/loss")
    net_pnl: Optional[float] = Field(None, description="Net profit/loss after costs")
    pnl_percent: Optional[float] = Field(None, description="P&L percentage")

    # Costs
    total_commission: float = Field(default=0.0, ge=0)
    total_slippage: float = Field(default=0.0, ge=0)

    # Status
    is_open: bool = Field(default=True, description="Whether position is still open")

    class Config:
        json_schema_extra = {
            "example": {
                "trade_id": "TRADE-789",
                "algorithm_id": "sma_crossover_v1",
                "symbol": "AAPL",
                "entry_order_id": "ORD-123456",
                "entry_price": 175.50,
                "entry_time": "2025-11-09T10:30:00",
                "entry_quantity": 10,
                "exit_order_id": "ORD-123457",
                "exit_price": 178.00,
                "exit_time": "2025-11-09T14:30:00",
                "exit_quantity": 10,
                "gross_pnl": 25.0,
                "net_pnl": 24.5,
                "pnl_percent": 1.42,
                "total_commission": 0.35,
                "total_slippage": 0.15,
                "is_open": False
            }
        }


class Position(BaseModel):
    """Current position in a symbol"""

    symbol: str
    algorithm_id: str

    side: PositionSide = Field(default=PositionSide.NONE)
    quantity: float = Field(default=0.0, ge=0)
    average_price: float = Field(default=0.0, ge=0)

    current_price: Optional[float] = Field(None, gt=0)
    market_value: Optional[float] = Field(None, ge=0)

    unrealized_pnl: Optional[float] = Field(None)
    unrealized_pnl_percent: Optional[float] = Field(None)

    opened_at: Optional[datetime] = Field(None)

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "algorithm_id": "sma_crossover_v1",
                "side": "LONG",
                "quantity": 10,
                "average_price": 175.50,
                "current_price": 178.00,
                "market_value": 1780.00,
                "unrealized_pnl": 25.00,
                "unrealized_pnl_percent": 1.42,
                "opened_at": "2025-11-09T10:30:00"
            }
        }
