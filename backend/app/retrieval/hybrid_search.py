"""
Hybrid Search Logic (Semantic + Keyword)
Fuses the results of pgvector semantic search and BM25 keyword search
using Reciprocal Rank Fusion (RRF).
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.retrieval.search import SemanticSearcher
from app.retrieval.keyword_search import KeywordSearcher

class HybridSearcher:
    """Executes both semantic and keyword searches and fuses the results."""
    
    def __init__(self, db: Session):
        self.db = db
        self.semantic_searcher = SemanticSearcher(db)
        self.keyword_searcher = KeywordSearcher()
        
    def search(self, query: str, k: int = 5, rrf_k: int = 60) -> List[Dict[str, Any]]:
        """
        Executes hybrid search.
        
        Args:
            query: The search query string.
            k: The final number of results to return.
            rrf_k: The 'k' constant used in the Reciprocal Rank Fusion formula. Default 60.
        """
        if not query:
            return []
            
        # 1. Fetch top results from both engines (fetch a larger pool for better fusion)
        pool_size = max(k * 2, 20)
        
        semantic_results = self.semantic_searcher.search(query, k=pool_size)
        keyword_results = self.keyword_searcher.search(query, k=pool_size, db=self.db)
        
        # 2. Reciprocal Rank Fusion (RRF)
        # Formula: RRF_score(d) = 1 / (rrf_k + rank_semantic(d)) + 1 / (rrf_k + rank_keyword(d))
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}
        
        # Process Semantic Ranks
        for rank, item in enumerate(semantic_results):
            chunk_id = item["chunk_id"]
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = item
                rrf_scores[chunk_id] = 0.0
            
            # Distance score from pgvector (lower distance = better).
            # We already sorted them in semantic_searcher by distance ascending,
            # so rank is accurate (index 0 is best).
            rrf_scores[chunk_id] += 1.0 / (rrf_k + rank + 1)
            
        # Process Keyword Ranks
        for rank, item in enumerate(keyword_results):
            chunk_id = item["chunk_id"]
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = item
                rrf_scores[chunk_id] = 0.0
                
            rrf_scores[chunk_id] += 1.0 / (rrf_k + rank + 1)
            
        # 3. Sort by aggregated RRF score (descending)
        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 4. Format and return top K
        final_results = []
        for chunk_id, score in sorted_chunks[:k]:
            result_item = chunk_map[chunk_id]
            # Replace the original engine score with the hybrid RRF score
            result_item["score"] = score
            # Remove distance_score if it exists to keep schema uniform
            if "distance_score" in result_item:
                result_item["distance_score"] = None
            final_results.append(result_item)
            
        return final_results
