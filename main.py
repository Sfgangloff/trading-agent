#!/usr/bin/env python3
"""
Autonomous Evolutionary Trading Agent - Main Entry Point

Phase 1: Foundation Demo
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict

from src.utils.logger import get_logger, setup_logger
from src.utils.config import load_config
from src.data.market_data import MarketDataManager
from src.data.sentiment import SentimentProvider
from src.trading.portfolio import Portfolio
from src.algorithms.sma_crossover import SMAcrossover
from src.models import Signal, SignalType, PositionSide, OrderType

# Setup logger
setup_logger(level="INFO")
logger = get_logger(__name__)


class TradingSystem:
    """
    Main trading system orchestrator

    Coordinates market data, algorithms, and portfolio management
    """

    def __init__(self):
        """Initialize the trading system"""
        logger.info("=" * 60)
        logger.info("Initializing Autonomous Evolutionary Trading Agent")
        logger.info("=" * 60)

        # Load configuration
        self.config = load_config()
        logger.info(f"Configuration loaded: {len(self.config.market.symbols)} symbols")

        # Initialize market data manager
        self.market_data = MarketDataManager(provider=self.config.market.data_source)

        # Initialize sentiment provider
        self.sentiment = SentimentProvider()

        # Initialize portfolio
        self.portfolio = Portfolio(
            initial_capital=self.config.paper_trading.initial_capital,
            commission_rate=self.config.paper_trading.commission,
            slippage_rate=self.config.paper_trading.slippage,
        )

        # Initialize algorithms
        self.algorithms = [
            SMAcrossover(algorithm_id="sma_crossover_v1", short_window=20, long_window=50),
        ]

        logger.info(f"Loaded {len(self.algorithms)} trading algorithms")

        # Trading state
        self.is_running = False
        self.iteration = 0

    async def fetch_market_data(self) -> Dict:
        """
        Fetch current market data and sentiment

        Returns:
            Dict with tickers and sentiment
        """
        logger.info("Fetching market data...")

        # Fetch tickers for all symbols
        tickers = await self.market_data.get_multiple_tickers(
            self.config.market.symbols,
            use_cache=True
        )

        # Fetch sentiment
        sentiment_data = await self.sentiment.get_sentiment()

        logger.info(f"Fetched data for {len(tickers)} symbols")
        if sentiment_data.overall_sentiment is not None:
            logger.info(f"Overall sentiment: {sentiment_data.overall_sentiment:.2f}")

        return {
            "tickers": tickers,
            "sentiment": sentiment_data,
        }

    async def run_algorithms(self, market_data: Dict) -> List[Signal]:
        """
        Run all algorithms and collect signals

        Args:
            market_data: Market data dict

        Returns:
            List of signals
        """
        signals = []
        tickers = market_data["tickers"]
        sentiment = market_data["sentiment"]

        for symbol in self.config.market.symbols:
            if symbol not in tickers:
                continue

            ticker = tickers[symbol]

            # Fetch historical data for algorithms
            historical_data = await self.market_data.get_historical(
                symbol,
                days=60,  # Get enough history for SMA calculations
                interval="1d"
            )

            # Run each algorithm
            for algorithm in self.algorithms:
                try:
                    signal = algorithm.analyze(
                        symbol=symbol,
                        current_data=ticker,
                        historical_data=historical_data,
                        sentiment=sentiment,
                    )

                    if signal:
                        signals.append(signal)
                        logger.info(
                            f"Signal: {algorithm.name} → {signal.signal_type} {symbol} "
                            f"(confidence: {signal.confidence:.2%})"
                        )

                except Exception as e:
                    logger.error(f"Error running {algorithm.name} on {symbol}: {e}")

        return signals

    async def execute_signals(self, signals: List[Signal], market_data: Dict):
        """
        Execute trading signals

        Args:
            signals: List of signals
            market_data: Market data dict
        """
        tickers = market_data["tickers"]

        for signal in signals:
            if signal.symbol not in tickers:
                continue

            current_price = tickers[signal.symbol].price

            # Get current position
            position = self.portfolio.get_position(signal.symbol, signal.algorithm_id)

            # Determine action based on signal and current position
            if signal.signal_type == SignalType.BUY:
                # Only buy if we don't have a position
                if position is None or position.quantity == 0:
                    # Calculate quantity (use a portion of available cash)
                    max_investment = self.portfolio.cash * self.config.paper_trading.max_position_size
                    quantity = int(max_investment / current_price)

                    if quantity > 0:
                        # Create and execute buy order
                        order = self.portfolio.create_order(
                            symbol=signal.symbol,
                            algorithm_id=signal.algorithm_id,
                            side=PositionSide.LONG,
                            quantity=quantity,
                            order_type=OrderType.MARKET,
                        )

                        success = self.portfolio.execute_order(order, current_price)
                        if success:
                            logger.info(f"✓ Bought {quantity} {signal.symbol} @ ${current_price:.2f}")
                        else:
                            logger.warning(f"✗ Failed to execute buy order for {signal.symbol}")

            elif signal.signal_type == SignalType.SELL:
                # Only sell if we have a position
                if position and position.quantity > 0:
                    # Create and execute sell order
                    order = self.portfolio.create_order(
                        symbol=signal.symbol,
                        algorithm_id=signal.algorithm_id,
                        side=PositionSide.SHORT,
                        quantity=position.quantity,
                        order_type=OrderType.MARKET,
                    )

                    success = self.portfolio.execute_order(order, current_price)
                    if success:
                        logger.info(f"✓ Sold {position.quantity} {signal.symbol} @ ${current_price:.2f}")
                    else:
                        logger.warning(f"✗ Failed to execute sell order for {signal.symbol}")

    def print_portfolio_status(self, market_data: Dict):
        """
        Print current portfolio status

        Args:
            market_data: Market data dict
        """
        tickers = market_data["tickers"]
        current_prices = {symbol: ticker.price for symbol, ticker in tickers.items()}

        snapshot = self.portfolio.get_snapshot(current_prices)

        logger.info("-" * 60)
        logger.info("PORTFOLIO STATUS")
        logger.info("-" * 60)
        logger.info(f"Cash:            ${snapshot.cash:.2f}")
        logger.info(f"Positions Value: ${snapshot.positions_value:.2f}")
        logger.info(f"Total Value:     ${snapshot.total_value:.2f}")
        logger.info(f"Total P&L:       ${snapshot.total_pnl:+.2f} ({snapshot.total_pnl_percent:+.2f}%)")
        logger.info(f"Open Positions:  {snapshot.num_positions}")
        logger.info(f"Total Trades:    {len(self.portfolio.trades)}")

        # Show open positions
        if snapshot.num_positions > 0:
            logger.info("\nOpen Positions:")
            for position in self.portfolio.positions.values():
                if position.quantity > 0:
                    current_price = current_prices.get(position.symbol, position.average_price)
                    unrealized_pnl = (current_price - position.average_price) * position.quantity
                    unrealized_pct = (unrealized_pnl / (position.average_price * position.quantity)) * 100

                    logger.info(
                        f"  {position.symbol}: {position.quantity} shares @ ${position.average_price:.2f} "
                        f"(current: ${current_price:.2f}, P&L: ${unrealized_pnl:+.2f} [{unrealized_pct:+.2f}%])"
                    )

        logger.info("-" * 60)

    async def run_iteration(self):
        """Run a single trading iteration"""
        self.iteration += 1
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Iteration #{self.iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'=' * 60}")

        try:
            # 1. Fetch market data
            market_data = await self.fetch_market_data()

            # 2. Run algorithms to generate signals
            signals = await self.run_algorithms(market_data)
            logger.info(f"Generated {len(signals)} trading signals")

            # 3. Execute signals
            if signals:
                await self.execute_signals(signals, market_data)

            # 4. Print portfolio status
            self.print_portfolio_status(market_data)

        except Exception as e:
            logger.error(f"Error in trading iteration: {e}", exc_info=True)

    async def run(self, iterations: int = 5, interval: int = 60):
        """
        Run the trading system

        Args:
            iterations: Number of iterations to run (None for infinite)
            interval: Seconds between iterations
        """
        self.is_running = True
        logger.info(f"Starting trading system (iterations: {iterations}, interval: {interval}s)")

        try:
            for i in range(iterations):
                await self.run_iteration()

                if i < iterations - 1:
                    logger.info(f"\nWaiting {interval} seconds until next iteration...")
                    await asyncio.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\nShutdown requested by user")
        except Exception as e:
            logger.error(f"Fatal error in trading system: {e}", exc_info=True)
        finally:
            self.is_running = False
            logger.info("Trading system stopped")

            # Final summary
            await self.print_final_summary()

    async def print_final_summary(self):
        """Print final trading summary"""
        logger.info("\n" + "=" * 60)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 60)

        logger.info(f"Initial Capital:    ${self.portfolio.initial_capital:.2f}")
        logger.info(f"Final Capital:      ${self.portfolio.cash:.2f}")
        logger.info(f"Total Trades:       {len(self.portfolio.trades)}")

        if self.portfolio.trades:
            winning_trades = [t for t in self.portfolio.trades if t.net_pnl and t.net_pnl > 0]
            losing_trades = [t for t in self.portfolio.trades if t.net_pnl and t.net_pnl <= 0]

            logger.info(f"Winning Trades:     {len(winning_trades)}")
            logger.info(f"Losing Trades:      {len(losing_trades)}")

            if len(self.portfolio.trades) > 0:
                win_rate = len(winning_trades) / len(self.portfolio.trades) * 100
                logger.info(f"Win Rate:           {win_rate:.1f}%")

        logger.info(f"Total Commissions:  ${self.portfolio.total_commissions:.2f}")
        logger.info(f"Total Slippage:     ${self.portfolio.total_slippage:.2f}")
        logger.info("=" * 60)


async def main():
    """Main entry point"""
    # Create and run trading system
    system = TradingSystem()

    # Run for 5 iterations with 60 second intervals (demo mode)
    # In production, you might run indefinitely with shorter intervals
    await system.run(iterations=3, interval=30)


if __name__ == "__main__":
    asyncio.run(main())
