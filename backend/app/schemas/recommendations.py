"""
Recommendation Engine Pydantic Schemas
Defines request and response validation schemas for opportunity scoring and ranking.
"""

from typing import List
from pydantic import BaseModel
from app.schemas.opportunity import OpportunityResponse
from app.schemas.eligibility import EligibilityResultSchema


class OpportunityScoreDetail(BaseModel):
    """Breakdown of points awarded to an opportunity during recommendation scoring."""
    
    deadline_score: int
    financial_need_score: int
    academic_merit_score: int
    demographic_match_score: int
    total_score: int
    reasons: List[str]


class RankedOpportunityResponse(BaseModel):
    """Combines an opportunity with its eligibility and score ranking."""
    
    rank: int
    opportunity: OpportunityResponse
    eligibility: EligibilityResultSchema
    score: OpportunityScoreDetail
