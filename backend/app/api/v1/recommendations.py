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
from app.core.demo import TEMP_STUDENT_PROFILES
from datetime import datetime

router = APIRouter()

@router.get("/{student_id}", response_model=List[RankedOpportunityResponse])
def get_recommendations(
    student_id: str,
    top_k: Optional[int] = Query(None, gt=0, description="Number of top recommendations to return"),
    db: Session = Depends(get_db)
):
    """
    Evaluates eligibility and scores active opportunities to return a ranked recommendation list.
    """
    if student_id in TEMP_STUDENT_PROFILES:
        profile_data = TEMP_STUDENT_PROFILES[student_id]
        student = Student(**profile_data)
        try:
            parsed_id = uuid.UUID(student_id)
        except ValueError:
            parsed_id = uuid.uuid4()
        student.id = parsed_id
        student.created_at = datetime.utcnow()
        student.updated_at = datetime.utcnow()
    else:
        try:
            parsed_id = uuid.UUID(student_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Student not found")
            
        student = db.query(Student).filter(Student.id == parsed_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
    engine = RecommendationEngine(db)
    results = engine.recommend(student, top_k=top_k)
    
    return results
