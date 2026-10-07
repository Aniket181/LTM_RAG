"""
RAG Engine Core
Coordinates retrieval and LLM generation.
"""

from typing import List
from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.llm import get_llm
from app.retrieval.hybrid_search import HybridSearcher
from app.schemas.rag import AskRequest, AnswerResponse, SourceAttribution
from app.models.opportunity import Opportunity
from app.models.document import SourceDocument

class RAGEngine:
    def __init__(self, db: Session):
        self.db = db
        self.searcher = HybridSearcher(db)
        self.llm = get_llm()
        
        self.system_prompt = """You are a student education opportunity assistant. Answer the user's question ONLY using the provided document context.
Rules:
1. Use only information contained in the provided context.
2. Do not use outside knowledge.
3. Do not invent scholarship eligibility criteria.
4. Do not invent deadlines.
5. Do not invent scholarship amounts or benefits.
6. Do not invent required documents.
7. Do not invent application procedures.
8. If the requested information is not present in the context, say: "I don't know based on the provided documents."
9. Do not make an official eligibility decision.
10. If the context is ambiguous or incomplete, explicitly state that.
11. Preserve the distinction between documented facts and missing information.
12. Give concise answers and cite the provided sources."""

    def ask(self, request: AskRequest) -> AnswerResponse:
        # 1. Retrieve Context
        results = self.searcher.search(
            query=request.query,
            k=request.top_k,
            opportunity_id=request.opportunity_id
        )
        
        # Filter out chunks that are semantically irrelevant
        # Recalibrated for Phase G corpus (884 chunks): BGE distance > 0.32 is typically noise
        filtered_results = []
        for res in results:
            dist = res.get("distance_score")
            if dist is not None and dist > 0.32:
                continue
            filtered_results.append(res)
            
        results = filtered_results
        
        if not results:
            return AnswerResponse(
                answer="I don't know based on the provided documents.",
                sources=[]
            )
            
        # 2. Extract Sources & Format Context
        context_parts = []
        sources = []
        
        for idx, res in enumerate(results):
            chunk_id = res["chunk_id"]
            doc_id = res.get("document_id")
            opp_id = res.get("opportunity_id")
            page_num = res.get("page_number")
            score = res.get("score") # RRF Score
            doc_title = res.get("document_title")
            source_url = res.get("source_url")
            
            # Fetch opportunity name if opp_id exists
            opp_name = None
            if opp_id:
                opp = self.db.query(Opportunity).filter(Opportunity.id == opp_id).first()
                if opp:
                    opp_name = opp.name
                    
            sources.append(SourceAttribution(
                chunk_id=chunk_id,
                document_id=doc_id,
                opportunity_id=opp_id,
                opportunity_name=opp_name,
                similarity_score=score,
                source_title=doc_title,
                page_number=page_num,
                source_url=source_url
            ))
            
            # Format this chunk into the prompt context
            source_label = f"[Source {idx + 1}: {doc_title or 'Unknown'} (Page {page_num or 'Unknown'})]"
            context_parts.append(f"{source_label}\n{res['chunk_text']}")
            
        formatted_context = "\n\n".join(context_parts)
        
        # 3. Construct Final Prompt
        prompt = f"DOCUMENT CONTEXT:\n{formatted_context}\n\nUSER QUESTION:\n{request.query}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # 4. Generate Answer
        response = self.llm.invoke(messages)
        answer_text = response.content if hasattr(response, "content") else str(response)
        
        return AnswerResponse(
            answer=answer_text,
            sources=sources
        )
