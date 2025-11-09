"""
Database utilities and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_agent.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,  # Set to True for SQL query logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator:
    """
    Database session dependency for FastAPI/general use

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables
    """
    from src.utils.db_models import (
        AlgorithmDB,
        OrderDB,
        TradeDB,
        PositionDB,
        PerformanceMetricsDB,
        PortfolioSnapshotDB,
    )

    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """
    Drop all database tables (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)
