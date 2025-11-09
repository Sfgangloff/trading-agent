#!/usr/bin/env python3
"""
Database initialization script

Creates all necessary database tables for the trading agent system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.database import init_db, engine
from src.utils.db_models import Base


def main():
    """Initialize the database"""
    print("Initializing database...")
    print(f"Database URL: {engine.url}")

    try:
        # Create all tables
        init_db()
        print("✓ Database tables created successfully!")

        # List created tables
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
