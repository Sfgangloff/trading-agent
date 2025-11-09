"""
Configuration management
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class MarketConfig(BaseModel):
    """Market data configuration"""
    symbols: list[str] = Field(default_factory=lambda: ["AAPL", "GOOGL", "MSFT"])
    data_source: str = "yfinance"
    update_frequency: int = 60


class PaperTradingConfig(BaseModel):
    """Paper trading configuration"""
    initial_capital: float = 100.0
    commission: float = 0.001
    slippage: float = 0.0005
    max_position_size: float = 0.2


class EvolutionConfig(BaseModel):
    """Evolution engine configuration"""
    schedule: str = "16:30"
    top_n: int = 15
    max_algorithms: int = 100
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-5-20250929"
    evaluation_window: int = 1


class SentimentConfig(BaseModel):
    """Sentiment analysis configuration"""
    enabled: bool = True
    sources: list[str] = Field(default_factory=lambda: ["fear_greed", "news_api"])
    update_frequency: int = 300


class PerformanceConfig(BaseModel):
    """Performance tracking configuration"""
    metrics: list[str] = Field(default_factory=lambda: ["roi", "sharpe", "max_drawdown", "win_rate"])
    risk_free_rate: float = 0.04


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    file: str = "logs/trading_agent.log"
    rotation: str = "1 day"
    retention: str = "30 days"


class Config(BaseModel):
    """Main configuration"""
    market: MarketConfig = Field(default_factory=MarketConfig)
    paper_trading: PaperTradingConfig = Field(default_factory=PaperTradingConfig)
    evolution: EvolutionConfig = Field(default_factory=EvolutionConfig)
    sentiment: SentimentConfig = Field(default_factory=SentimentConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to config file (default: config/config.yaml)

    Returns:
        Config object
    """
    if config_path is None:
        # Try default locations
        possible_paths = [
            Path("config/config.yaml"),
            Path("config/config.example.yaml"),
        ]

        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break

    if config_path and Path(config_path).exists():
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)
        return Config(**config_dict)
    else:
        # Return default config
        return Config()


# Global config instance
config = load_config()
