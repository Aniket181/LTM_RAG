"""
Database Initialization Utilities
Helper functions to create tables or verify connectivity.
"""

import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


def check_db_connection() -> bool:
    """Verify that the database engine can establish a valid connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database connection check failed: %s", exc)
        return False


def init_db() -> None:
    """
    Create all database tables defined in Base metadata.
    Primarily useful for development, test databases, or rapid bootstrapping.
    """
    # Import all models so metadata knows about all tables
    import app.models  # noqa: F401

    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
