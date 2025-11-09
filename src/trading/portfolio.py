"""
Portfolio management for paper trading
"""

from typing import Dict, Optional, List
from datetime import datetime
import uuid
from src.models import (
    Order,
    Trade,
    Position,
    PortfolioSnapshot,
    OrderType,
    OrderStatus,
    PositionSide,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Portfolio:
    """
    Paper trading portfolio manager

    Manages virtual cash, positions, orders, and tracks performance
    """

    def __init__(
        self,
        initial_capital: float = 100.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
    ):
        """
        Initialize portfolio

        Args:
            initial_capital: Starting cash amount
            commission_rate: Commission as fraction of trade value
            slippage_rate: Slippage as fraction of price
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

        # Positions: {symbol: Position}
        self.positions: Dict[str, Position] = {}

        # Order history
        self.orders: List[Order] = []

        # Trade history
        self.trades: List[Trade] = []

        # Performance tracking
        self.peak_value = initial_capital
        self.total_commissions = 0.0
        self.total_slippage = 0.0

        logger.info(f"Portfolio initialized with ${initial_capital:.2f}")

    def get_position(self, symbol: str, algorithm_id: str) -> Optional[Position]:
        """
        Get current position for a symbol

        Args:
            symbol: Trading symbol
            algorithm_id: Algorithm ID

        Returns:
            Position object or None
        """
        key = f"{algorithm_id}:{symbol}"
        return self.positions.get(key)

    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value

        Args:
            current_prices: Dict of {symbol: price}

        Returns:
            Total value (cash + positions)
        """
        positions_value = 0.0

        for position in self.positions.values():
            if position.quantity > 0 and position.symbol in current_prices:
                positions_value += position.quantity * current_prices[position.symbol]

        return self.cash + positions_value

    def create_order(
        self,
        symbol: str,
        algorithm_id: str,
        side: PositionSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None,
    ) -> Order:
        """
        Create a new order

        Args:
            symbol: Trading symbol
            algorithm_id: Algorithm placing the order
            side: LONG (buy) or SHORT (sell)
            quantity: Number of shares/units
            order_type: MARKET or LIMIT
            limit_price: Price for limit orders

        Returns:
            Created order
        """
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        order = Order(
            order_id=order_id,
            algorithm_id=algorithm_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            limit_price=limit_price,
            status=OrderStatus.PENDING,
        )

        self.orders.append(order)
        logger.info(f"Order created: {order_id} - {side} {quantity} {symbol}")

        return order

    def execute_order(self, order: Order, current_price: float) -> bool:
        """
        Execute a pending order

        Args:
            order: Order to execute
            current_price: Current market price

        Returns:
            True if executed successfully, False otherwise
        """
        if order.status != OrderStatus.PENDING:
            logger.warning(f"Order {order.order_id} is not pending")
            return False

        # Check if limit order can be executed
        if order.order_type == OrderType.LIMIT:
            if order.limit_price is None:
                logger.error(f"Limit order {order.order_id} has no limit price")
                order.status = OrderStatus.REJECTED
                return False

            if order.side == PositionSide.LONG and current_price > order.limit_price:
                logger.debug(f"Limit buy not executed: price {current_price} > limit {order.limit_price}")
                return False

            if order.side == PositionSide.SHORT and current_price < order.limit_price:
                logger.debug(f"Limit sell not executed: price {current_price} < limit {order.limit_price}")
                return False

        # Calculate execution price with slippage
        slippage_amount = current_price * self.slippage_rate
        if order.side == PositionSide.LONG:
            execution_price = current_price + slippage_amount  # Buy higher
        else:
            execution_price = current_price - slippage_amount  # Sell lower

        # Calculate costs
        trade_value = execution_price * order.quantity
        commission = trade_value * self.commission_rate

        # Check if we have enough cash for buy orders
        if order.side == PositionSide.LONG:
            total_cost = trade_value + commission
            if self.cash < total_cost:
                logger.warning(f"Insufficient cash for order {order.order_id}: need ${total_cost:.2f}, have ${self.cash:.2f}")
                order.status = OrderStatus.REJECTED
                return False

        # Execute the order
        order.filled_price = execution_price
        order.filled_at = datetime.utcnow()
        order.commission = commission
        order.slippage = slippage_amount * order.quantity
        order.status = OrderStatus.FILLED

        # Update tracking
        self.total_commissions += commission
        self.total_slippage += order.slippage

        # Update position
        self._update_position(order)

        # Update cash
        if order.side == PositionSide.LONG:
            self.cash -= (trade_value + commission)
        else:
            self.cash += (trade_value - commission)

        logger.info(
            f"Order executed: {order.order_id} - {order.side} {order.quantity} {order.symbol} "
            f"@ ${execution_price:.2f} (commission: ${commission:.4f})"
        )

        return True

    def _update_position(self, order: Order) -> None:
        """
        Update position based on filled order

        Args:
            order: Filled order
        """
        key = f"{order.algorithm_id}:{order.symbol}"
        position = self.positions.get(key)

        if order.side == PositionSide.LONG:
            # Buy: add to position
            if position is None:
                # New position
                self.positions[key] = Position(
                    symbol=order.symbol,
                    algorithm_id=order.algorithm_id,
                    side=PositionSide.LONG,
                    quantity=order.quantity,
                    average_price=order.filled_price,
                    opened_at=order.filled_at,
                )
            else:
                # Add to existing position
                total_cost = (position.average_price * position.quantity) + (order.filled_price * order.quantity)
                position.quantity += order.quantity
                position.average_price = total_cost / position.quantity
                position.side = PositionSide.LONG

        elif order.side == PositionSide.SHORT:
            # Sell: reduce position
            if position is None:
                logger.warning(f"Trying to sell {order.symbol} but no position exists")
                return

            position.quantity -= order.quantity

            if position.quantity <= 0:
                # Close position
                self._close_position(order, position)
                del self.positions[key]

    def _close_position(self, exit_order: Order, position: Position) -> None:
        """
        Close a position and create trade record

        Args:
            exit_order: Exit order
            position: Position being closed
        """
        # Find entry order (last buy order for this symbol/algorithm)
        entry_order = None
        for order in reversed(self.orders):
            if (
                order.symbol == position.symbol
                and order.algorithm_id == position.algorithm_id
                and order.side == PositionSide.LONG
                and order.status == OrderStatus.FILLED
            ):
                entry_order = order
                break

        if entry_order is None:
            logger.warning(f"Could not find entry order for position {position.symbol}")
            return

        # Calculate P&L
        gross_pnl = (exit_order.filled_price - position.average_price) * position.quantity
        net_pnl = gross_pnl - (entry_order.commission + exit_order.commission + entry_order.slippage + exit_order.slippage)
        pnl_percent = (gross_pnl / (position.average_price * position.quantity)) * 100

        # Create trade record
        trade = Trade(
            trade_id=f"TRADE-{uuid.uuid4().hex[:8].upper()}",
            algorithm_id=position.algorithm_id,
            symbol=position.symbol,
            entry_order_id=entry_order.order_id,
            entry_price=position.average_price,
            entry_time=entry_order.filled_at,
            entry_quantity=position.quantity,
            exit_order_id=exit_order.order_id,
            exit_price=exit_order.filled_price,
            exit_time=exit_order.filled_at,
            exit_quantity=position.quantity,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            pnl_percent=pnl_percent,
            total_commission=entry_order.commission + exit_order.commission,
            total_slippage=entry_order.slippage + exit_order.slippage,
            is_open=False,
        )

        self.trades.append(trade)
        logger.info(
            f"Position closed: {trade.trade_id} - {trade.symbol} "
            f"P&L: ${net_pnl:.2f} ({pnl_percent:.2f}%)"
        )

    def get_snapshot(self, current_prices: Dict[str, float]) -> PortfolioSnapshot:
        """
        Get current portfolio snapshot

        Args:
            current_prices: Dict of {symbol: price}

        Returns:
            Portfolio snapshot
        """
        positions_value = 0.0

        for position in self.positions.values():
            if position.quantity > 0 and position.symbol in current_prices:
                positions_value += position.quantity * current_prices[position.symbol]

        total_value = self.cash + positions_value
        total_pnl = total_value - self.initial_capital
        total_pnl_percent = (total_pnl / self.initial_capital) * 100

        # Update peak value
        if total_value > self.peak_value:
            self.peak_value = total_value

        return PortfolioSnapshot(
            cash=self.cash,
            positions_value=positions_value,
            total_value=total_value,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            num_positions=len([p for p in self.positions.values() if p.quantity > 0]),
        )

    def get_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown

        Returns:
            Maximum drawdown as negative percentage
        """
        if self.peak_value <= 0:
            return 0.0

        current_value = self.cash + sum(
            p.quantity * (p.current_price or p.average_price)
            for p in self.positions.values()
            if p.quantity > 0
        )

        drawdown = ((current_value - self.peak_value) / self.peak_value) * 100
        return min(drawdown, 0.0)

    def reset(self) -> None:
        """Reset portfolio to initial state"""
        self.cash = self.initial_capital
        self.positions.clear()
        self.orders.clear()
        self.trades.clear()
        self.peak_value = self.initial_capital
        self.total_commissions = 0.0
        self.total_slippage = 0.0
        logger.info("Portfolio reset")
