# Autonomous Evolutionary Trading Agent

## Project Overview

An AI-powered autonomous trading system that uses evolutionary algorithms and LLM-driven strategy generation to develop and optimize trading strategies through paper trading simulation.

## Core Concept

The system starts with basic trading algorithms and evolves them daily using LLM analysis. Each day, the top-performing strategies are analyzed by an LLM (GPT/Claude), which identifies success patterns, proposes improvements, and generates new candidate algorithms. These strategies compete in a simulated trading environment with real market data.

## Key Features

- **Real-time Market Data Integration**: Continuous access to ticker data (price, volume, OHLC, etc.)
- **Sentiment Analysis**: Integration of market sentiment indicators (Fear & Greed Index, social sentiment)
- **Paper Trading Engine**: Simulated trading with $100 starting capital
- **Evolutionary Strategy Development**: Daily LLM-powered algorithm evolution
- **Performance Tracking**: Comprehensive metrics on strategy performance
- **Zero-Risk Testing**: All trades are simulated, no real money involved

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TRADING AGENT SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │  Data Ingestion │         │  Sentiment Data  │          │
│  │     Layer       │         │     Provider     │          │
│  │                 │         │                  │          │
│  │ - Market APIs   │         │ - Fear/Greed     │          │
│  │ - WebSockets    │         │ - Social Media   │          │
│  │ - Real-time     │         │ - News API       │          │
│  └────────┬────────┘         └────────┬─────────┘          │
│           │                           │                     │
│           └───────────┬───────────────┘                     │
│                       ▼                                      │
│           ┌───────────────────────┐                         │
│           │   Data Aggregator     │                         │
│           │   & Preprocessor      │                         │
│           └───────────┬───────────┘                         │
│                       ▼                                      │
│           ┌───────────────────────┐                         │
│           │  Algorithm Executor   │◄──────────┐            │
│           │                       │            │            │
│           │ - Strategy Runner     │            │            │
│           │ - Signal Generator    │            │            │
│           │ - Multi-threading     │            │            │
│           └───────────┬───────────┘            │            │
│                       ▼                         │            │
│           ┌───────────────────────┐            │            │
│           │  Paper Trading Engine │            │            │
│           │                       │            │            │
│           │ - Portfolio Manager   │            │            │
│           │ - Order Execution     │            │            │
│           │ - P&L Tracking        │            │            │
│           └───────────┬───────────┘            │            │
│                       ▼                         │            │
│           ┌───────────────────────┐            │            │
│           │  Performance Tracker  │            │            │
│           │                       │            │            │
│           │ - Metrics DB          │            │            │
│           │ - Returns Analysis    │            │            │
│           │ - Risk Metrics        │            │            │
│           └───────────┬───────────┘            │            │
│                       ▼                         │            │
│           ┌───────────────────────┐            │            │
│           │   Evolution Engine    │            │            │
│           │   (Daily, EOD)        │            │            │
│           │                       │            │            │
│           │ - Top N Selection     │            │            │
│           │ - LLM Integration     │            │            │
│           │ - Strategy Generation │            │            │
│           └───────────┬───────────┘            │            │
│                       │                         │            │
│                       └─────────────────────────┘            │
│                         (New Algorithms)                     │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Data Ingestion Layer
**Purpose**: Fetch and stream real-time market data

**Responsibilities**:
- Connect to market data APIs (Alpha Vantage, Polygon.io, Yahoo Finance, IEX Cloud)
- Maintain WebSocket connections for real-time price updates
- Handle rate limiting and API quotas
- Cache and buffer data
- Provide unified interface for multiple data sources

**Key Data Points**:
- Price (bid, ask, last)
- Volume
- OHLC (Open, High, Low, Close)
- Market depth (optional)
- Trading timestamps

### 2. Sentiment Data Provider
**Purpose**: Aggregate market sentiment indicators

**Data Sources**:
- Fear & Greed Index (CNN Business, Alternative.me for crypto)
- Social media sentiment (Twitter, Reddit via APIs)
- News sentiment (News API, Finnhub)
- VIX (Volatility Index)

**Output**: Normalized sentiment score (-1 to 1 or 0 to 100)

### 3. Algorithm Executor
**Purpose**: Run multiple trading strategies concurrently

**Features**:
- Algorithm registry/catalog
- Parallel execution of strategies
- Signal generation from each algorithm
- Resource management
- Error handling and isolation (one algorithm failure doesn't crash system)

**Algorithm Interface**:
```python
class TradingAlgorithm:
    def analyze(data, sentiment) -> Signal:
        """
        Returns: BUY, SELL, HOLD signal with confidence score
        """
```

### 4. Paper Trading Engine
**Purpose**: Simulate real trading without financial risk

**Features**:
- Virtual portfolio management ($100 starting capital)
- Order execution simulation (market, limit orders)
- Realistic slippage and commission modeling
- Position tracking (open/closed positions)
- Cash management
- Transaction history

**Key Metrics**:
- Current portfolio value
- Total P&L
- Win rate
- Sharpe ratio
- Maximum drawdown

### 5. Performance Tracker
**Purpose**: Evaluate and rank algorithm performance

**Metrics Tracked**:
- Return on Investment (ROI)
- Profit/Loss (absolute and percentage)
- Number of trades
- Win/loss ratio
- Average profit per trade
- Maximum drawdown
- Sharpe ratio
- Sortino ratio
- Time-weighted performance

**Storage**: SQLite or PostgreSQL database with time-series data

### 6. Evolution Engine (LLM-Powered)
**Purpose**: Evolve trading strategies using AI analysis

**Process** (Runs daily after market close):
1. **Selection**: Extract top N performing algorithms (e.g., top 10-20)
2. **Analysis**: Send to LLM with:
   - Algorithm code/description
   - Performance metrics
   - Market conditions during testing period
   - Prompt asking for analysis
3. **Generation**: LLM outputs:
   - Analysis of why certain strategies succeeded/failed
   - Proposed modifications to existing algorithms
   - Brand new algorithm proposals
4. **Integration**: Parse LLM output, add new algorithms to registry
5. **Pruning**: Remove worst performers to maintain manageable algorithm pool

**LLM Prompt Structure**:
```
You are a quantitative trading strategist. Here are the top performing
algorithms from today's trading session:

[Algorithm 1 - Code + Performance]
[Algorithm 2 - Code + Performance]
...

Market conditions: [Summary]
Sentiment range: [Min-Max]

Tasks:
1. Analyze why certain algorithms outperformed others
2. Identify common patterns in successful strategies
3. Propose 5 modifications to existing algorithms
4. Generate 5 completely new algorithm ideas
5. Ensure algorithms are simple, interpretable, and executable

Format each algorithm as valid Python code following our Algorithm Interface.
```

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI (for any API endpoints/dashboard)
- **Real-time Processing**: asyncio, websockets
- **Data Storage**: PostgreSQL or SQLite
- **Task Scheduling**: APScheduler or Celery

### Data & APIs
- **Market Data**:
  - Polygon.io (excellent real-time API)
  - Alpha Vantage (free tier available)
  - Yahoo Finance API (yfinance library)
- **Sentiment Data**:
  - Alternative.me API (crypto fear/greed)
  - News API
  - Twitter API v2
- **LLM Integration**:
  - OpenAI API (GPT-4)
  - Anthropic API (Claude)

### Libraries
- `pandas`, `numpy` - Data manipulation
- `asyncio`, `aiohttp` - Async operations
- `websockets` - Real-time data streaming
- `sqlalchemy` - Database ORM
- `pydantic` - Data validation
- `anthropic` or `openai` - LLM integration
- `pytest` - Testing

### Monitoring (Optional)
- Prometheus + Grafana for metrics
- Logging: structlog or loguru

## Implementation Phases

### Phase 1: Foundation (Week 1-2) ✅ COMPLETED
**Status**: ✅ Complete (2025-11-09)

**Goals**: Set up core infrastructure

**Tasks**:
- [x] Project scaffolding and repository setup
- [x] Define data models (Ticker, Signal, Trade, Algorithm, Performance)
- [x] Implement data ingestion for one market data source (Yahoo Finance)
- [x] Create basic paper trading engine
  - [x] Portfolio class
  - [x] Order execution logic
  - [x] P&L calculation
- [x] Database schema design and setup (SQLAlchemy + SQLite)
- [x] Basic logging and error handling (loguru)
- [x] Configuration management (YAML)
- [x] Sentiment data integration (Fear & Greed Index)
- [x] SMA Crossover starter algorithm
- [x] Main application with trading loop

**Deliverables**: ✅ All Complete
- ✅ Can fetch real-time data (5 symbols via Yahoo Finance)
- ✅ Can execute simulated trades ($100 starting capital)
- ✅ Can track portfolio state (positions, P&L, performance)
- ✅ Database persistence with 6 tables
- ✅ Modular, extensible architecture

### Phase 2: Algorithm Framework (Week 3)
**Goals**: Create strategy execution system

**Tasks**:
- [ ] Design algorithm interface/base class
- [ ] Implement 5-7 starter algorithms:
  - [ ] Simple Moving Average (SMA) crossover
  - [ ] RSI-based strategy
  - [ ] MACD strategy
  - [ ] Sentiment-driven strategy
  - [ ] Mean reversion strategy
  - [ ] Momentum strategy
  - [ ] Combined sentiment + technical strategy
- [ ] Algorithm executor with concurrent execution
- [ ] Signal aggregation and conflict resolution
- [ ] Performance tracking system

**Deliverables**:
- Multiple strategies running simultaneously
- Real-time performance metrics

### Phase 3: Sentiment Integration (Week 4)
**Goals**: Add sentiment analysis capabilities

**Tasks**:
- [ ] Integrate Fear & Greed Index API
- [ ] Add news sentiment analysis
- [ ] Implement sentiment normalization
- [ ] Create sentiment-aware algorithms
- [ ] Test sentiment signal quality

**Deliverables**:
- Sentiment data flowing into algorithms
- Sentiment metrics in dashboard

### Phase 4: Evolution Engine (Week 5-6)
**Goals**: Implement LLM-powered strategy evolution

**Tasks**:
- [ ] Design evolution pipeline
- [ ] Implement top-N algorithm selection logic
- [ ] Create LLM prompt templates
- [ ] Integrate OpenAI/Anthropic API
- [ ] Build algorithm code parser (safely parse LLM-generated code)
- [ ] Implement algorithm validation and sandboxing
- [ ] Create daily scheduling system (runs at market close)
- [ ] Algorithm versioning and genealogy tracking

**Deliverables**:
- Automated daily evolution cycle
- New algorithms generated from LLM
- Safety mechanisms for code execution

### Phase 5: Optimization & Monitoring (Week 7-8)
**Goals**: Polish and production-ready

**Tasks**:
- [ ] Performance optimization
- [ ] Comprehensive error handling
- [ ] Add web dashboard for monitoring (Streamlit or Dash)
- [ ] Implement alerting system
- [ ] Backtesting framework
- [ ] Documentation
- [ ] Unit and integration tests

**Deliverables**:
- Production-ready system
- Monitoring dashboard
- Complete documentation

### Phase 6: Advanced Features (Optional)
**Goals**: Enhanced capabilities

**Ideas**:
- [ ] Multi-asset support (stocks, crypto, forex)
- [ ] Machine learning-based performance prediction
- [ ] Risk management constraints (max drawdown limits, position sizing)
- [ ] Portfolio optimization (Markowitz, Kelly Criterion)
- [ ] Strategy combinations/ensembles
- [ ] Real-time visualization and charting
- [ ] Export to live trading (with safety checks)

## Key Algorithms (Starters)

### 1. SMA Crossover
```python
Buy when short-term MA crosses above long-term MA
Sell when short-term MA crosses below long-term MA
Parameters: short_window=20, long_window=50
```

### 2. RSI Mean Reversion
```python
Buy when RSI < 30 (oversold)
Sell when RSI > 70 (overbought)
Parameter: period=14
```

### 3. Sentiment + Price Action
```python
Buy when sentiment is extreme fear AND price dropped >2% today
Sell when sentiment is extreme greed AND price rose >2% today
```

### 4. MACD Strategy
```python
Buy when MACD line crosses above signal line
Sell when MACD line crosses below signal line
Parameters: fast=12, slow=26, signal=9
```

### 5. Momentum Strategy
```python
Buy when 5-day return > threshold AND sentiment positive
Sell when 5-day return < -threshold OR sentiment negative
Parameter: threshold=3%
```

## Risk Considerations

### Technical Risks
- **API Rate Limits**: Implement caching and request throttling
- **Data Quality**: Handle missing data, outliers, API downtime
- **Code Injection**: Sandbox LLM-generated code, validate before execution
- **Infinite Loops**: Timeout mechanisms for algorithm execution

### Financial Risks (For future live trading)
- **Over-optimization**: Strategies may overfit to historical data
- **Transaction Costs**: Model realistic commissions and slippage
- **Market Impact**: Even paper trading should simulate realistic execution
- **Black Swan Events**: Strategies may fail during extreme market conditions

### Safety Measures
- Start with paper trading only
- Implement kill switches and position limits
- Log all decisions for audit
- Human review of LLM-generated strategies before deployment
- Gradual rollout of new algorithms (canary deployment)

## Success Metrics

### System Performance
- System uptime > 99% during market hours
- Data latency < 1 second
- Algorithm execution time < 100ms per strategy

### Trading Performance
- Beat buy-and-hold baseline
- Positive Sharpe ratio > 1.0
- Maximum drawdown < 20%
- Win rate > 50%

### Evolution Effectiveness
- New algorithms show improvement over time
- Top 25% of algorithms should beat random baseline
- Diversity in strategy types maintained

## Configuration Example

```yaml
# config.yaml
market:
  symbols: ["AAPL", "GOOGL", "MSFT", "TSLA", "BTC-USD"]
  data_source: "polygon"
  update_frequency: 60  # seconds

paper_trading:
  initial_capital: 100.0
  commission: 0.001  # 0.1%
  slippage: 0.0005   # 0.05%

evolution:
  schedule: "16:30"  # Market close time (EST)
  top_n: 15
  max_algorithms: 100
  llm_provider: "anthropic"
  llm_model: "claude-opus-4"

sentiment:
  enabled: true
  sources: ["fear_greed", "news_api"]
  update_frequency: 300  # 5 minutes

performance:
  evaluation_window: 1  # days
  metrics: ["roi", "sharpe", "max_drawdown", "win_rate"]
```

## Getting Started

### Prerequisites
- Python 3.10+
- API keys for market data provider
- API key for LLM (OpenAI/Anthropic)
- PostgreSQL (optional, can start with SQLite)

### Quick Start
```bash
# Clone and setup
git clone <repository>
cd trading-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys

# Initialize database
python scripts/init_db.py

# Run the system
python main.py
```

## Future Enhancements

1. **Multi-timeframe Analysis**: Strategies that analyze multiple timeframes
2. **Portfolio Theory**: Implement MPT for optimal asset allocation
3. **Reinforcement Learning**: Use RL agents alongside rule-based strategies
4. **Social Trading**: Incorporate "wisdom of the crowd" from trading forums
5. **Explainability**: Generate human-readable explanations for each trade
6. **Live Trading Integration**: Safe transition to real trading with limits
7. **Strategy Marketplace**: Share and discover strategies from community

## Resources & References

### Market Data APIs
- [Polygon.io](https://polygon.io) - Real-time and historical market data
- [Alpha Vantage](https://www.alphavantage.co) - Free tier available
- [IEX Cloud](https://iexcloud.io) - Financial data platform

### Sentiment Data
- [Alternative.me API](https://alternative.me/crypto/fear-and-greed-index/) - Crypto Fear & Greed
- [News API](https://newsapi.org) - News articles

### Learning Resources
- "Advances in Financial Machine Learning" by Marcos López de Prado
- "Algorithmic Trading" by Ernie Chan
- [QuantConnect](https://www.quantconnect.com) - Algorithmic trading platform
- [Zipline](https://github.com/quantopian/zipline) - Backtesting library

---

## Project Timeline: 8-10 Weeks

**Week 1-2**: Foundation & Paper Trading Engine
**Week 3-4**: Algorithm Framework & Sentiment Integration
**Week 5-6**: Evolution Engine & LLM Integration
**Week 7-8**: Optimization, Testing & Monitoring
**Week 9-10**: Polish & Advanced Features

---

## Notes

- This is a research/educational project - not financial advice
- Paper trading only initially, real trading requires extensive testing
- Keep algorithms interpretable and auditable
- Monitor for overfitting and regime changes in markets
- The LLM evolution is experimental - may need tuning

## Contact & Collaboration

[Add your contact information and contribution guidelines here]

---

**Status**: Phase 1 Complete ✅ | Phase 2 Ready to Start
**Last Updated**: 2025-11-09
**Version**: 1.0

## Phase 1 Completion Summary

### What We Built
- **31 Python files** with comprehensive trading infrastructure
- **2,870+ lines of code** across models, trading engine, and algorithms
- **6 database tables** for persistence (algorithms, orders, trades, positions, metrics, snapshots)
- **Complete paper trading engine** with $100 starting capital
- **Market data integration** via Yahoo Finance (AAPL, GOOGL, MSFT, TSLA, BTC-USD)
- **Sentiment analysis** via Fear & Greed Index
- **SMA Crossover algorithm** with sentiment awareness
- **Main trading loop** with automated iterations and reporting

### Key Files
- `src/models/` - Pydantic data models
- `src/trading/portfolio.py` - Paper trading engine
- `src/data/market_data.py` - Market data fetching
- `src/data/sentiment.py` - Sentiment provider
- `src/algorithms/sma_crossover.py` - SMA crossover strategy
- `main.py` - Trading system orchestrator
- `scripts/init_db.py` - Database initialization

### Running the System
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Run trading system
python main.py
```

### Next Steps
Phase 2 will add multiple trading algorithms (RSI, MACD, momentum, mean-reversion) and concurrent execution.
