"""
Semantic Search Logic
Retrieves relevant document chunks from PostgreSQL using pgvector cosine distance.
"""

from typing import List, Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session
from app.models.document import DocumentChunk
from app.retrieval.embedder import LocalEmbedder

class SemanticSearcher:
    """Executes semantic similarity search on DocumentChunks."""

    def __init__(self, db: Session):
        self.db = db
        self.embedder = LocalEmbedder()

    def search(self, query: str, k: int = 5, opportunity_id: Optional[uuid.UUID] = None) -> List[Dict[str, Any]]:
        """
        Embeds the query and finds the top-k most similar document chunks.
        Uses pgvector's cosine distance operator `<=>`.
        """
        if not query:
            return []

        # 1. Embed query
        query_embedding = self.embedder.embed_query(query)

        # 2. Vector search via pgvector cosine distance
        distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label('distance')
        
        base_query = self.db.query(DocumentChunk, distance_col).filter(DocumentChunk.embedding.is_not(None))
        
        if opportunity_id:
            from app.models.opportunity import Opportunity
            opp = self.db.query(Opportunity.source_document_id).filter(Opportunity.id == opportunity_id).first()
            if opp and opp[0]:
                base_query = base_query.filter(DocumentChunk.source_document_id == opp[0])
            else:
                return []
            
        results = (
            base_query
            .order_by(distance_col)
            .limit(k)
            .all()
        )

        # 3. Assemble provenance-rich results
        formatted_results = []
        for chunk, distance in results:
            source_doc = chunk.source_document
            
            formatted_results.append({
                "chunk_id": str(chunk.id),
                "document_id": str(source_doc.id) if source_doc else None,
                "document_title": source_doc.title if source_doc else "Unknown",
                "chunk_text": chunk.content,
                "page_number": chunk.page_number,
                "distance_score": float(distance),
                "source_url": source_doc.source_url if source_doc else None,
                "academic_year": source_doc.academic_year if source_doc else None,
                "opportunity_id": str(source_doc.opportunities[0].id) if source_doc and getattr(source_doc, "opportunities", None) else None,
            })

        return formatted_results
