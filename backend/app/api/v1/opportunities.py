"""
Opportunities API Router
Handles CRUD operations for scholarships, fellowships, and educational opportunities.
"""

from typing import Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, pagination_params
from app.models.opportunity import Opportunity
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityFilter,
    OpportunityResponse,
    OpportunityUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[OpportunityResponse])
def get_opportunities(
    db: Session = Depends(get_db),
    params: dict = Depends(pagination_params),
    filters: OpportunityFilter = Depends(),
) -> Any:
    """
    Retrieve opportunities.
    Supports pagination and basic filtering (e.g., status, opportunity_type, category).
    """
    query = db.query(Opportunity)

    if filters.status:
        query = query.filter(Opportunity.status == filters.status)
    if filters.opportunity_type:
        query = query.filter(Opportunity.opportunity_type == filters.opportunity_type)
    
    # Note: Complex JSON filtering (like education_level, category) will be expanded
    # in Phase 6/8. For now, simple text matching or list retrieval.
    
    if filters.query:
        query = query.filter(Opportunity.name.ilike(f"%{filters.query}%"))

    opportunities = query.offset(params["skip"]).limit(params["limit"]).all()
    return opportunities


@router.get("/{id}", response_model=OpportunityResponse)
def get_opportunity(
    id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve a specific opportunity by ID."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )
    return opportunity


@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    *,
    db: Session = Depends(get_db),
    opportunity_in: OpportunityCreate,
) -> Any:
    """Create a new opportunity."""
    # Check if opportunity with same name already exists
    existing = db.query(Opportunity).filter(Opportunity.name == opportunity_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An opportunity with this name already exists.",
        )
    
    opportunity = Opportunity(**opportunity_in.model_dump())
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.put("/{id}", response_model=OpportunityResponse)
def update_opportunity(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
    opportunity_in: OpportunityUpdate,
) -> Any:
    """Update an existing opportunity."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )
    
    update_data = opportunity_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)
        
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


@router.delete("/{id}", response_model=OpportunityResponse)
def delete_opportunity(
    *,
    db: Session = Depends(get_db),
    id: uuid.UUID,
) -> Any:
    """Delete an opportunity."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )
    
    db.delete(opportunity)
    db.commit()
    return opportunity
