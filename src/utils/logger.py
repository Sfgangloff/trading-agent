"""
Logging configuration using loguru
"""

import sys
from pathlib import Path
from loguru import logger
import os


def setup_logger(
    level: str = "INFO",
    log_file: str = "logs/trading_agent.log",
    rotation: str = "1 day",
    retention: str = "30 days",
) -> None:
    """
    Configure the logger for the trading system

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        rotation: When to rotate log files
        retention: How long to keep old log files
    """
    # Remove default handler
    logger.remove()

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Console handler (colorized)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # File handler (detailed)
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation=rotation,
        retention=retention,
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    logger.info(f"Logger initialized - Level: {level}, File: {log_file}")


def get_logger(name: str = None):
    """
    Get a logger instance

    Args:
        name: Optional name for the logger

    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Initialize with defaults from environment
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logger(level=log_level)
