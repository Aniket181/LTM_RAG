"""
Recommendations API Router
Exposes the recommendation engine.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.student import Student
from app.schemas.recommendations import RankedOpportunityResponse
from app.recommendations.engine import RecommendationEngine

router = APIRouter()

@router.get("/{student_id}", response_model=List[RankedOpportunityResponse])
def get_recommendations(
    student_id: uuid.UUID,
    top_k: Optional[int] = Query(None, gt=0, description="Number of top recommendations to return"),
    db: Session = Depends(get_db)
):
    """
    Evaluates eligibility and scores active opportunities to return a ranked recommendation list.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    engine = RecommendationEngine(db)
    results = engine.recommend(student, top_k=top_k)
    
    return results
