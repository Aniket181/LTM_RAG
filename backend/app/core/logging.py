"""
Logging Configuration
Sets up structured, leveled logging for the entire application.
Logs are written to stdout (for containerization compatibility) and optionally to a file.
Sensitive information (API keys, passwords) must NEVER be logged.
"""

import logging
import sys
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file:  Optional path to write logs to a file in addition to stdout.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Formatter: timestamp | level | module | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove any existing handlers to avoid duplicate logs
    root_logger.handlers.clear()

    # --- stdout handler ---
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(numeric_level)
    stdout_handler.setFormatter(formatter)
    root_logger.addHandler(stdout_handler)

    # --- Optional file handler ---
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging configured | level=%s", log_level.upper()
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger for use in a specific module.

    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Starting operation")
    """
    return logging.getLogger(name)
