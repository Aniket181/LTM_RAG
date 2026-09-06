"""
Health Check Endpoint
Provides a lightweight health check for the API and its connected components.
Used by load balancers, monitoring systems, and Docker healthchecks.
"""

import logging
import time
from typing import Any, Dict

from fastapi import APIRouter

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Track application start time for uptime reporting
_start_time: float = time.time()


def _check_database() -> Dict[str, Any]:
    """
    Attempt a lightweight database connectivity check.
    Returns status dict with 'status' and optional 'error' keys.
    """
    try:
        # Import here to avoid circular imports; DB not required in Phase 1
        from sqlalchemy import text
        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except ImportError:
        # Database module not yet initialized (Phase 1 — expected)
        return {"status": "not_configured"}
    except Exception as exc:
        logger.warning("Database health check failed: %s", str(exc))
        return {"status": "error", "error": str(exc)}


def _check_vector_store() -> Dict[str, Any]:
    """Check vector store availability."""
    try:
        import chromadb  # noqa: F401
        return {"status": "ok", "type": settings.vector_store_type}
    except ImportError:
        return {"status": "not_configured"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@router.get(
    "/health",
    summary="System Health Check",
    description=(
        "Returns the operational status of the API and its core components. "
        "A 200 response indicates the API is running. "
        "Individual component statuses may show 'not_configured' in early phases."
    ),
    tags=["System"],
)
async def health_check() -> Dict[str, Any]:
    """
    System health check endpoint.

    Returns:
        JSON object with:
        - status: overall system status ("ok" | "degraded" | "error")
        - version: application version
        - uptime_seconds: seconds since application start
        - environment: current environment (development / production)
        - components: per-component health status
    """
    uptime = round(time.time() - _start_time, 2)

    db_status = _check_database()
    vector_status = _check_vector_store()

    # Determine overall status
    component_statuses = [db_status["status"], vector_status["status"]]
    if any(s == "error" for s in component_statuses):
        overall = "degraded"
    else:
        overall = "ok"

    logger.debug("Health check requested | uptime=%.2fs | overall=%s", uptime, overall)

    return {
        "status": overall,
        "version": settings.app_version,
        "app_name": settings.app_name,
        "uptime_seconds": uptime,
        "environment": settings.app_env,
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.embedding_model,
        "components": {
            "api": {"status": "ok"},
            "database": db_status,
            "vector_store": vector_status,
        },
    }
