"""
Recommendation Engine
Orchestrates scoring and ranking of eligible opportunities.
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.opportunity import Opportunity
from app.eligibility.engine import EligibilityEngine
from app.schemas.recommendations import RankedOpportunityResponse, OpportunityScoreDetail
from app.recommendations.scorer import DeadlineScorer, FinancialNeedScorer, AcademicMeritScorer, DemographicMatchScorer

class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.eligibility_engine = EligibilityEngine(db)
        self.scorers = [
            ("deadline_score", DeadlineScorer()),
            ("financial_need_score", FinancialNeedScorer()),
            ("academic_merit_score", AcademicMeritScorer()),
            ("demographic_match_score", DemographicMatchScorer())
        ]

    def recommend(self, student: Student, top_k: Optional[int] = None, reference_date: date = None) -> List[RankedOpportunityResponse]:
        """
        Retrieves active opportunities, filters by eligibility, and ranks them by score.
        """
        active_opps = self.db.query(Opportunity).filter(Opportunity.status == "Active").all()
        
        ranked_results = []
        for opp in active_opps:
            # 1. Eligibility Gatekeeper
            eligibility_res = self.eligibility_engine.evaluate_opportunity(student, opp)
            
            # Exclude NOT_ELIGIBLE completely
            if eligibility_res.overall_status == "NOT_ELIGIBLE":
                continue
                
            # 2. Score remaining
            score_details = {}
            reasons = []
            total_score = 0
            
            for score_key, scorer in self.scorers:
                result = scorer.score(student, opp, reference_date)
                pts = result.get("score", 0)
                score_details[score_key] = pts
                total_score += pts
                if result.get("reason"):
                    reasons.append(result["reason"])
                    
            score_details["total_score"] = total_score
            score_details["reasons"] = reasons
            
            # We will rank them later, so store in an intermediate structure
            ranked_results.append({
                "opportunity": opp,
                "eligibility": eligibility_res,
                "score": OpportunityScoreDetail(**score_details),
                "total_score": total_score
            })
            
        # 3. Sort Results
        # Deterministic sorting: 
        # a. Eligibility status (ELIGIBLE > POTENTIALLY_ELIGIBLE > INSUFFICIENT_INFORMATION)
        # b. Total score (descending)
        # c. Deadline (ascending, nearer is better. Handle None gracefully)
        # d. Alphabetical name (ascending)
        
        def sort_key(item):
            status_order = {"ELIGIBLE": 0, "POTENTIALLY_ELIGIBLE": 1, "INSUFFICIENT_INFORMATION": 2}
            status_rank = status_order.get(item["eligibility"].overall_status, 99)
            
            score_rank = -item["total_score"] # negative for descending
            
            # Use a dummy far-future date if closing_date is missing
            closing_date = item["opportunity"].closing_date or date(9999, 12, 31)
            
            name = item["opportunity"].name or ""
            
            return (status_rank, score_rank, closing_date, name)
            
        ranked_results.sort(key=sort_key)
        
        # 4. Truncate Top K
        if top_k is not None and top_k > 0:
            ranked_results = ranked_results[:top_k]
            
        # 5. Format Output
        final_responses = []
        for rank_idx, item in enumerate(ranked_results, start=1):
            final_responses.append(
                RankedOpportunityResponse(
                    rank=rank_idx,
                    opportunity=item["opportunity"], # Handled by ConfigDict(from_attributes=True) in OpportunityResponse
                    eligibility=item["eligibility"],
                    score=item["score"]
                )
            )
            
        return final_responses
