"""
FastAPI Application Entry Point
RAG-Based Student Education Opportunity and Scholarship Eligibility Intelligence System

This module creates and configures the FastAPI application instance.
It registers:
  - All API routers
  - CORS middleware
  - Exception handlers
  - Application lifecycle events (startup / shutdown)
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import setup_logging

# Configure logging before anything else runs
setup_logging(log_level=settings.log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan handler (replaces deprecated on_event).
    Code before yield runs on startup; code after yield runs on shutdown.
    """
    # --- Startup ---
    logger.info("=" * 60)
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Environment  : %s", settings.app_env)
    logger.info("Debug mode   : %s", settings.debug)
    logger.info("LLM provider : %s", settings.llm_provider)
    logger.info("Vector store : %s", settings.vector_store_type)
    logger.info("Embedding    : %s", settings.embedding_model)
    logger.info("API docs     : http://%s:%d/docs", settings.api_host, settings.api_port)
    logger.info("=" * 60)

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("Application shutting down gracefully.")


def create_application() -> FastAPI:
    """
    Application factory.
    Returns a fully configured FastAPI instance.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "An intelligent system that helps students discover educational "
            "opportunities and scholarships and determine their eligibility "
            "using RAG, Hybrid Retrieval, and a Deterministic Eligibility Engine."
        ),
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------
    # CORS Middleware
    # ------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # Exception Handlers
    # ------------------------------------------------------------------
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ------------------------------------------------------------------
    # Routers
    # ------------------------------------------------------------------
    app.include_router(api_router)

    return app


# Create the application instance
app = create_application()
