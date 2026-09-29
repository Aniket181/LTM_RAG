"""
Keyword Search Logic (BM25)
Retrieves relevant document chunks using traditional BM25 vocabulary matching.
Uses an in-memory index that can be refreshed.
"""

from typing import List, Dict, Any, Optional
import threading
import uuid
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session
from app.models.document import DocumentChunk, SourceDocument

class KeywordSearcher:
    """
    Executes keyword similarity search on DocumentChunks using BM25.
    Maintains an in-memory BM25 index that can be refreshed periodically.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern so the index is shared across requests."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(KeywordSearcher, cls).__new__(cls)
                    cls._instance._bm25 = None
                    cls._instance._chunks = []
        return cls._instance

    def refresh(self, db: Session):
        """
        Fetches all chunks from the DB and rebuilds the BM25 index.
        Call this after new documents are ingested.
        """
        with self._lock:
            # Fetch all chunks (in a real app at scale, this would be paginated or we'd use a dedicated search engine)
            # We eagerly load source_document so it's ready for serialization
            chunks = db.query(DocumentChunk).all()
            
            self._chunks = chunks
            
            if not chunks:
                self._bm25 = None
                return
                
            tokenized_corpus = [self._tokenize(chunk.content) for chunk in chunks]
            self._bm25 = BM25Okapi(tokenized_corpus)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer (lowercase and split by whitespace)."""
        if not text:
            return []
        return text.lower().split()

    def search(self, query: str, k: int = 5, db: Optional[Session] = None, opportunity_id: Optional[uuid.UUID] = None) -> List[Dict[str, Any]]:
        """
        Finds the top-k most similar document chunks using BM25.
        If the index is not initialized, it will try to initialize it using the provided db session.
        """
        if not query:
            return []

        if self._bm25 is None:
            if db:
                self.refresh(db)
            else:
                # If no db provided and no index exists, we can't search
                return []
                
        if self._bm25 is None or not self._chunks:
            return []

        tokenized_query = self._tokenize(query)
        
        # Get scores for all chunks
        scores = self._bm25.get_scores(tokenized_query)
        
        # Zip scores with chunks, sort by score descending
        chunk_scores = list(zip(self._chunks, scores))
        
        if opportunity_id:
            if not db:
                return []
            from app.models.opportunity import Opportunity
            opp = db.query(Opportunity.source_document_id).filter(Opportunity.id == opportunity_id).first()
            if opp and opp[0]:
                doc_id = opp[0]
                chunk_scores = [
                    cs for cs in chunk_scores 
                    if cs[0].source_document_id == doc_id
                ]
            else:
                return []
            
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Take top k
        top_k = chunk_scores[:k]
        
        # 3. Assemble provenance-rich results
        formatted_results = []
        for chunk, score in top_k:
            if score <= 0.0:
                continue # Skip chunks that have 0 relevance
                
            source_doc = chunk.source_document
            
            formatted_results.append({
                "chunk_id": str(chunk.id),
                "document_id": str(source_doc.id) if source_doc else None,
                "document_title": source_doc.title if source_doc else "Unknown",
                "chunk_text": chunk.content,
                "page_number": chunk.page_number,
                "score": float(score),
                "source_url": source_doc.source_url if source_doc else None,
                "academic_year": source_doc.academic_year if source_doc else None,
                "opportunity_id": str(source_doc.opportunities[0].id) if source_doc and getattr(source_doc, "opportunities", None) else None,
            })

        return formatted_results
