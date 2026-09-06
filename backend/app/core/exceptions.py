"""
Centralized Exception Handlers and Custom Exception Classes.
All application-level exceptions are defined here for consistency.
FastAPI exception handlers are registered in main.py.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ============================================================
# Custom Exception Classes
# ============================================================


class AppException(Exception):
    """Base class for all application-level exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class ResourceNotFoundException(AppException):
    """Raised when a requested resource does not exist in the database."""

    def __init__(self, resource_type: str, resource_id: Any) -> None:
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"resource_type": resource_type, "resource_id": str(resource_id)},
        )


class ValidationException(AppException):
    """Raised when input data fails business logic validation."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"field": field} if field else {},
        )


class DatabaseException(AppException):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "A database error occurred.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class EligibilityEngineException(AppException):
    """Raised when the eligibility engine encounters an unexpected error."""

    def __init__(self, message: str = "Eligibility evaluation failed.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RAGPipelineException(AppException):
    """Raised when the RAG pipeline fails."""

    def __init__(self, message: str = "RAG pipeline encountered an error.") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class DocumentIngestionException(AppException):
    """Raised when document ingestion or processing fails."""

    def __init__(self, message: str, filename: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"filename": filename} if filename else {},
        )


# ============================================================
# FastAPI Exception Handlers
# ============================================================


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all custom AppException subclasses."""
    logger.error(
        "Application error | path=%s | status=%d | message=%s",
        request.url.path,
        exc.status_code,
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "detail": exc.detail,
            "path": str(request.url.path),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI's built-in HTTPException."""
    logger.warning(
        "HTTP error | path=%s | status=%d | detail=%s",
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "detail": {},
            "path": str(request.url.path),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions."""
    logger.exception(
        "Unhandled exception | path=%s | error=%s",
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected internal error occurred. Please try again later.",
            "detail": {},
            "path": str(request.url.path),
        },
    )
