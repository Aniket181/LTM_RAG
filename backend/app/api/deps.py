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
# Database Session (placeholder — wired in Phase 2)
# ------------------------------------------------------------------

# from app.db.session import SessionLocal
#
# def get_db() -> Generator:
#     """
#     Provide a database session for the duration of a request.
#     Automatically closes the session when the request completes.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
