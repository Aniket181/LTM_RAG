"""
Opportunity Pydantic Schemas
Defines request and response validation schemas for opportunities, scholarships, and fellowships.
"""

from datetime import date, datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field


class OpportunityBase(BaseModel):
    """Base opportunity attributes."""

    name: str = Field(..., max_length=255, description="Scheme title")
    provider: str = Field(..., max_length=255, description="Disbursing ministry, trust, or institute")
    description: str = Field(..., description="Complete description of the scheme")
    opportunity_type: str = Field(
        ..., description="Scholarship, Fellowship, Grant, Loan, Award"
    )
    education_level: List[str] = Field(
        ..., description="Eligible levels, e.g. ['UG', 'PG', 'PhD']"
    )
    course: Optional[List[str]] = Field(default_factory=list, description="Target courses")
    field_of_study: Optional[List[str]] = Field(default_factory=list, description="Target fields of study")
    minimum_cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    minimum_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    maximum_income: Optional[float] = Field(default=None, ge=0.0)
    minimum_income: Optional[float] = Field(default=None, ge=0.0)
    age_limit_max: Optional[int] = Field(default=None, ge=0, le=100)
    category: Optional[List[str]] = Field(default_factory=list)
    gender: Optional[str] = Field(default=None, max_length=50)
    state: Optional[List[str]] = Field(default_factory=list)
    domicile_requirement: Optional[str] = Field(default=None, max_length=255)
    institution_type: Optional[List[str]] = Field(default_factory=list)
    nationality_requirement: Optional[str] = Field(default="Indian", max_length=100)
    benefit_description: Optional[str] = None
    amount: Optional[float] = Field(default=None, ge=0.0)
    duration: Optional[str] = Field(default=None, max_length=100)
    opening_date: Optional[date] = None
    closing_date: Optional[date] = None
    renewal_info: Optional[str] = None
    required_documents: Optional[List[str]] = Field(default_factory=list)
    application_process: Optional[str] = None
    official_url: Optional[str] = Field(default=None, max_length=500)
    academic_year: Optional[str] = Field(default=None, max_length=50)
    last_verified_date: Optional[date] = None
    status: str = Field(default="Active", description="Active, Closed, Upcoming, Unknown")
    source_document_id: Optional[uuid.UUID] = None


class OpportunityCreate(OpportunityBase):
    """Payload for creating a new opportunity."""
    pass


class OpportunityUpdate(BaseModel):
    """Payload for updating an existing opportunity."""

    name: Optional[str] = None
    provider: Optional[str] = None
    description: Optional[str] = None
    opportunity_type: Optional[str] = None
    education_level: Optional[List[str]] = None
    course: Optional[List[str]] = None
    field_of_study: Optional[List[str]] = None
    minimum_cgpa: Optional[float] = None
    minimum_percentage: Optional[float] = None
    maximum_income: Optional[float] = None
    minimum_income: Optional[float] = None
    age_limit_max: Optional[int] = None
    category: Optional[List[str]] = None
    gender: Optional[str] = None
    state: Optional[List[str]] = None
    domicile_requirement: Optional[str] = None
    institution_type: Optional[List[str]] = None
    nationality_requirement: Optional[str] = None
    benefit_description: Optional[str] = None
    amount: Optional[float] = None
    duration: Optional[str] = None
    opening_date: Optional[date] = None
    closing_date: Optional[date] = None
    renewal_info: Optional[str] = None
    required_documents: Optional[List[str]] = None
    application_process: Optional[str] = None
    official_url: Optional[str] = None
    academic_year: Optional[str] = None
    last_verified_date: Optional[date] = None
    status: Optional[str] = None
    source_document_id: Optional[uuid.UUID] = None


class OpportunityResponse(OpportunityBase):
    """Response model for an opportunity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class OpportunityFilter(BaseModel):
    """Filter parameters for querying opportunities."""

    query: Optional[str] = None
    opportunity_type: Optional[str] = None
    education_level: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None
    max_income: Optional[float] = None
    min_cgpa: Optional[float] = None
    status: Optional[str] = "Active"
