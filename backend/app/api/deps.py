"""
Shared API Dependencies
FastAPI dependency injection functions used across multiple endpoints.
Database sessions, authentication context, pagination params, etc.
"""

from typing import Generator

from fastapi import Query


# ------------------------------------------------------------------
# Pagination
# ------------------------------------------------------------------


def pagination_params(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum records to return"),
) -> dict:
    """
    Common pagination dependency.
    Inject into endpoint functions with: params: dict = Depends(pagination_params)
    """
    return {"skip": skip, "limit": limit}


# ------------------------------------------------------------------
# Database Session
# ------------------------------------------------------------------

from app.db.session import get_db

__all__ = ["pagination_params", "get_db"]
