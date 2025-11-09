# Autonomous Evolutionary Trading Agent

An AI-powered autonomous trading system that uses evolutionary algorithms and LLM-driven strategy generation to develop and optimize trading strategies through paper trading simulation.

## Project Status

**Phase 1 (Foundation):** ✅ Complete

The foundation is now complete with:
- ✅ Project structure and configuration
- ✅ Core data models (Ticker, Signal, Trade, Algorithm, Performance)
- ✅ Database schema (SQLAlchemy)
- ✅ Paper trading engine with Portfolio management
- ✅ Market data ingestion (Yahoo Finance)
- ✅ Sentiment analysis (Fear & Greed Index)
- ✅ Starter trading algorithm (SMA Crossover)
- ✅ Logging and error handling

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** If you encounter issues installing `ta-lib`, you can remove it from requirements.txt for now. We're using `pandas-ta` as an alternative.

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (optional for Phase 1)
# For basic functionality, the default settings work with Yahoo Finance
```

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Run the Trading System

```bash
python main.py
```

This will run a demo that:
- Fetches real-time market data for configured symbols
- Analyzes data using the SMA Crossover algorithm
- Generates buy/sell signals
- Executes simulated trades with $100 starting capital
- Tracks portfolio performance

## Project Structure

```
trading-agent/
├── src/
│   ├── models/          # Data models (Pydantic)
│   │   ├── base.py
│   │   ├── market.py
│   │   ├── signal.py
│   │   ├── trade.py
│   │   ├── algorithm.py
│   │   └── performance.py
│   ├── data/            # Data ingestion
│   │   ├── market_data.py
│   │   └── sentiment.py
│   ├── trading/         # Paper trading engine
│   │   └── portfolio.py
│   ├── algorithms/      # Trading strategies
│   │   ├── base_algorithm.py
│   │   └── sma_crossover.py
│   ├── utils/           # Utilities
│   │   ├── database.py
│   │   ├── db_models.py
│   │   ├── logger.py
│   │   └── config.py
│   ├── evolution/       # LLM evolution (Phase 4)
│   └── performance/     # Performance tracking (Phase 2)
├── config/
│   └── config.example.yaml
├── scripts/
│   └── init_db.py
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## How It Works

### Phase 1: Foundation (Current)

1. **Market Data**: Fetches real-time and historical data from Yahoo Finance
2. **Sentiment Analysis**: Gets Fear & Greed Index for market sentiment
3. **Algorithm Execution**: Runs SMA Crossover strategy to generate signals
4. **Paper Trading**: Simulates trades with realistic commissions and slippage
5. **Performance Tracking**: Monitors portfolio value, P&L, and position details

### Example Output

```
============================================================
Iteration #1 - 2025-11-09 14:30:00
============================================================
Fetching market data...
Fetched data for 5 symbols
Overall sentiment: 0.32

Signal: SMA Crossover Strategy → BUY AAPL (confidence: 78%)
✓ Bought 10 AAPL @ $175.50

------------------------------------------------------------
PORTFOLIO STATUS
------------------------------------------------------------
Cash:            $24.25
Positions Value: $1755.00
Total Value:     $1779.25
Total P&L:       +$1679.25 (+1679.25%)
Open Positions:  1
Total Trades:    0

Open Positions:
  AAPL: 10 shares @ $175.50 (current: $175.50, P&L: +$0.00 [+0.00%])
------------------------------------------------------------
```

## Configuration

Edit `config/config.example.yaml` and save as `config/config.yaml`:

```yaml
market:
  symbols:
    - AAPL
    - GOOGL
    - MSFT
    - TSLA
    - BTC-USD
  data_source: "yfinance"
  update_frequency: 60

paper_trading:
  initial_capital: 100.0
  commission: 0.001      # 0.1%
  slippage: 0.0005       # 0.05%
  max_position_size: 0.2 # Max 20% per position
```

## Current Algorithms

### SMA Crossover
- **Strategy**: Buy when 20-day SMA crosses above 50-day SMA, sell when it crosses below
- **Sentiment Integration**: Boosts confidence when sentiment aligns with signal
- **Parameters**:
  - `short_window`: 20 days
  - `long_window`: 50 days
  - `confidence_threshold`: 0.7

## Next Steps (Upcoming Phases)

### Phase 2: Algorithm Framework (Week 3)
- [ ] Implement additional starter algorithms (RSI, MACD, momentum, etc.)
- [ ] Multi-algorithm concurrent execution
- [ ] Signal aggregation and conflict resolution
- [ ] Enhanced performance tracking

### Phase 3: Sentiment Integration (Week 4)
- [ ] News sentiment analysis
- [ ] Social media sentiment
- [ ] VIX integration
- [ ] Sentiment-driven algorithms

### Phase 4: Evolution Engine (Week 5-6)
- [ ] LLM integration (GPT-4/Claude)
- [ ] Automated strategy evolution
- [ ] Algorithm selection and ranking
- [ ] Code generation and validation

### Phase 5: Optimization & Monitoring (Week 7-8)
- [ ] Web dashboard (Streamlit/Dash)
- [ ] Backtesting framework
- [ ] Advanced metrics (Sharpe, Sortino, Calmar ratios)
- [ ] Alerting system

## Testing

To test the system:

```bash
# Run the main system (short demo)
python main.py

# Initialize/reset database
python scripts/init_db.py

# Run tests (when implemented)
pytest tests/
```

## Database

The system uses SQLite by default (`trading_agent.db`). Tables:

- `algorithms` - Trading algorithms
- `orders` - Order history
- `trades` - Completed trades
- `positions` - Current positions
- `performance_metrics` - Algorithm performance
- `portfolio_snapshots` - Portfolio history

## Environment Variables

Required (in `.env`):

```bash
# Optional for Phase 1, required for Phase 4+
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Market data (optional, yfinance works without keys)
POLYGON_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///./trading_agent.db
```

## Contributing

This is a research/educational project. See `CLAUDE.md` for detailed specifications and roadmap.

## Disclaimer

**This is for educational and research purposes only. This is not financial advice. Paper trading only - no real money is involved. Do not use for actual trading without extensive testing and risk management.**

## License

MIT License

---

**Version:** 1.0.0
**Last Updated:** 2025-11-09
**Status:** Phase 1 Complete
