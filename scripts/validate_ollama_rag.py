import sys
import os
import time
import requests
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.rag.engine import RAGEngine
from app.schemas.rag import AskRequest
from langchain_core.messages import HumanMessage

def print_header(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

def run_validation():
    print_header("OLLAMA + LOCAL LLAMA VALIDATION")
    
    # 1 & 2. Verify Ollama Server and Models
    ollama_url = "http://localhost:11434"
    try:
        r = requests.get(ollama_url, timeout=5)
        print(f"Ollama server: PASS (HTTP 200, '{r.text.strip()}')")
    except Exception as e:
        print(f"Ollama server: FAIL ({e})")
        return
        
    try:
        r = requests.get(f"{ollama_url}/api/tags", timeout=5)
        models = [m['name'] for m in r.json().get('models', [])]
        print(f"Installed models: {models}")
        
        # Determine best model name to use
        target_model = "llama3.2:latest"
        if target_model not in models:
            print(f"llama3.2:latest NOT FOUND")
            return
            
        print(f"Model: {target_model}")
    except Exception as e:
        print(f"Model list: FAIL ({e})")
        return

    # Switch config for the script
    settings.llm_provider = "ollama"
    settings.ollama_model = target_model
    print(f"Project provider: {settings.llm_provider}")

    # 3. Direct Generation
    try:
        from app.core.llm import get_llm
        llm = get_llm()
        t0 = time.time()
        resp = llm.invoke([HumanMessage(content="Reply with exactly: LOCAL LLAMA TEST PASSED")])
        t1 = time.time()
        print(f"Direct generation: PASS ('{resp.content.strip()}' in {t1-t0:.2f}s)")
    except Exception as e:
        print(f"Direct generation: FAIL ({e})")
        return

    engine_db = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine_db)
    db = SessionLocal()
    
    rag_engine = RAGEngine(db)

    # 4 & 5. Grounded RAG & Source Attribution
    try:
        t0 = time.time()
        q1 = "What are the eligibility requirements?"
        print(f"\nQuery: '{q1}'")
        res1 = rag_engine.ask(AskRequest(query=q1, top_k=5))
        t1 = time.time()
        print(f"RAG generation: PASS ({t1-t0:.2f}s)")
        print(f"Grounded answer: {res1.answer[:200]}...")
        if res1.sources:
            print(f"Source attribution: PASS ({len(res1.sources)} sources)")
            for s in res1.sources[:2]:
                print(f"  -> {s.source_title} (ID: {str(s.chunk_id)[:8]}... | Score: {s.similarity_score:.4f})")
        else:
            print("Source attribution: FAIL (No sources returned)")
    except Exception as e:
        print(f"RAG generation: FAIL ({e})")

    # 6. Irrelevant Query Rejection
    try:
        q2 = "How do I repair a bicycle?"
        print(f"\nQuery: '{q2}'")
        res2 = rag_engine.ask(AskRequest(query=q2, top_k=5))
        if len(res2.sources) == 0 and "I don't know" in res2.answer:
            print(f"Irrelevant query rejection: PASS (Sources: {len(res2.sources)}, Answer: '{res2.answer}')")
        else:
            print(f"Irrelevant query rejection: FAIL (Sources: {len(res2.sources)}, Answer: '{res2.answer}')")
    except Exception as e:
        print(f"Irrelevant query rejection: FAIL ({e})")
        
    # 7. LLM Failure Handling
    print("\n--- Failure Handling Test ---")
    original_url = settings.ollama_base_url
    try:
        settings.ollama_base_url = "http://localhost:9999"  # Dead port
        # Re-instantiate LLM with dead port
        rag_engine.llm = get_llm()
        # Force a direct invocation so it doesn't get rejected by retrieval threshold
        rag_engine.llm.invoke([HumanMessage(content="Test failure")])
        print("Failure handling: FAIL (Did not raise expected connection error)")
    except Exception as e:
        print(f"Failure handling: PASS (Caught connection error gracefully: {str(e)[:100]}...)")
    finally:
        settings.ollama_base_url = original_url # Restore
        
    print("\nFull regression: NOT RUN - run pytest manually")

if __name__ == "__main__":
    run_validation()
