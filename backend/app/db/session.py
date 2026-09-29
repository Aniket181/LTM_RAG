"""
Database Engine and Session Management
Configures the SQLAlchemy connection pool, sessionmaker, and session dependency.
"""

from typing import Generator
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Connection arguments
connect_args = {}
# If SQLite is used for tests/fallback, check_same_thread=False is needed
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Create database engine with connection pooling and health check (pool_pre_ping)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10 if not settings.database_url.startswith("sqlite") else 5,
    max_overflow=20 if not settings.database_url.startswith("sqlite") else 0,
    connect_args=connect_args,
    echo=False,
)

# Session factory bound to engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a scoped database session.
    Automatically closes session upon request completion or rolls back on unhandled error.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        db.rollback()
        logger.error("Database session rolled back due to error: %s", exc)
        raise
    finally:
        db.close()
