"""
API v1 Router
Aggregates all route groups under the /api/v1 prefix.
Each module registers its own router here as it is implemented.
"""

from fastapi import APIRouter

from app.api.v1 import health

api_router = APIRouter(prefix="/api/v1")

# --- System ---
api_router.include_router(health.router)

# --- Future routers (added in later phases) ---
from app.api.v1 import opportunities, documents, search, students, eligibility, recommendations, rag

api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(eligibility.router, prefix="/eligibility", tags=["Eligibility"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])

