"""
SQLAlchemy ORM models for database persistence
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, JSON, Text, Enum
from datetime import datetime
from .database import Base
from src.models.base import AlgorithmStatus, OrderType, OrderStatus, PositionSide


class AlgorithmDB(Base):
    """Algorithm database model"""

    __tablename__ = "algorithms"

    algorithm_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    code = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)

    parameters = Column(JSON, nullable=False, default={})

    status = Column(Enum(AlgorithmStatus), nullable=False, default=AlgorithmStatus.ACTIVE, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent_algorithm_id = Column(String, nullable=True, index=True)
    generation = Column(Integer, nullable=False, default=0)

    tags = Column(JSON, nullable=False, default=[])


class OrderDB(Base):
    """Order database model"""

    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    algorithm_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)

    order_type = Column(Enum(OrderType), nullable=False)
    side = Column(Enum(PositionSide), nullable=False)

    quantity = Column(Float, nullable=False)

    limit_price = Column(Float, nullable=True)
    filled_price = Column(Float, nullable=True)

    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    filled_at = Column(DateTime, nullable=True)

    commission = Column(Float, nullable=False, default=0.0)
    slippage = Column(Float, nullable=False, default=0.0)


class TradeDB(Base):
    """Trade database model"""

    __tablename__ = "trades"

    trade_id = Column(String, primary_key=True, index=True)
    algorithm_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)

    entry_order_id = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    entry_time = Column(DateTime, nullable=False, index=True)
    entry_quantity = Column(Float, nullable=False)

    exit_order_id = Column(String, nullable=True)
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime, nullable=True, index=True)
    exit_quantity = Column(Float, nullable=True)

    gross_pnl = Column(Float, nullable=True)
    net_pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)

    total_commission = Column(Float, nullable=False, default=0.0)
    total_slippage = Column(Float, nullable=False, default=0.0)

    is_open = Column(Boolean, nullable=False, default=True, index=True)


class PositionDB(Base):
    """Position database model"""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, index=True)
    algorithm_id = Column(String, nullable=False, index=True)

    side = Column(Enum(PositionSide), nullable=False, default=PositionSide.NONE)
    quantity = Column(Float, nullable=False, default=0.0)
    average_price = Column(Float, nullable=False, default=0.0)

    current_price = Column(Float, nullable=True)
    market_value = Column(Float, nullable=True)

    unrealized_pnl = Column(Float, nullable=True)
    unrealized_pnl_percent = Column(Float, nullable=True)

    opened_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class PerformanceMetricsDB(Base):
    """Performance metrics database model"""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    algorithm_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    days = Column(Integer, nullable=False)

    total_return = Column(Float, nullable=False)
    total_return_percent = Column(Float, nullable=False)
    annualized_return = Column(Float, nullable=True)

    total_trades = Column(Integer, nullable=False, default=0)
    winning_trades = Column(Integer, nullable=False, default=0)
    losing_trades = Column(Integer, nullable=False, default=0)

    win_rate = Column(Float, nullable=False, default=0.0)

    average_profit_per_trade = Column(Float, nullable=False, default=0.0)
    largest_win = Column(Float, nullable=False, default=0.0)
    largest_loss = Column(Float, nullable=False, default=0.0)

    max_drawdown = Column(Float, nullable=False, default=0.0)
    max_drawdown_percent = Column(Float, nullable=False, default=0.0)

    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    calmar_ratio = Column(Float, nullable=True)

    volatility = Column(Float, nullable=True)

    starting_capital = Column(Float, nullable=False)
    ending_capital = Column(Float, nullable=False)
    peak_capital = Column(Float, nullable=False)

    total_commissions = Column(Float, nullable=False, default=0.0)
    total_slippage = Column(Float, nullable=False, default=0.0)


class PortfolioSnapshotDB(Base):
    """Portfolio snapshot database model"""

    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    cash = Column(Float, nullable=False)
    positions_value = Column(Float, nullable=False, default=0.0)
    total_value = Column(Float, nullable=False)

    total_pnl = Column(Float, nullable=False, default=0.0)
    total_pnl_percent = Column(Float, nullable=False, default=0.0)

    num_positions = Column(Integer, nullable=False, default=0)
