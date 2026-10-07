"""
Eligibility Evaluation Pydantic Schemas
Defines request and response validation schemas for rule-based eligibility evaluation.
"""

from typing import Any, List, Optional
import uuid

from pydantic import BaseModel, Field


class RuleResultSchema(BaseModel):
    """Result of an individual deterministic eligibility rule check."""

    rule_name: str
    condition: str
    student_value: Optional[Any] = None
    required_value: str
    result: str = Field(..., description="PASS, FAIL, WARN, UNKNOWN")
    detail: str


class EligibilityResultSchema(BaseModel):
    """Aggregated eligibility evaluation result for an opportunity."""

    opportunity_id: uuid.UUID
    overall_status: str = Field(
        ...,
        description="ELIGIBLE, NOT_ELIGIBLE, POTENTIALLY_ELIGIBLE, INSUFFICIENT_INFORMATION",
    )
    rule_results: List[RuleResultSchema]
    summary: str


class EligibilityCheckRequest(BaseModel):
    """Request payload to evaluate eligibility for a student against opportunities."""

    student_id: str
    opportunity_ids: Optional[List[uuid.UUID]] = None


class EligibilityCheckResponse(BaseModel):
    """Response payload containing evaluation results."""

    student_id: str
    evaluations: List[EligibilityResultSchema]
