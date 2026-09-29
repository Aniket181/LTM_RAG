"""
Documents API Router
Handles file uploads and triggers the document ingestion pipeline.
"""

import os
import shutil
import uuid
from typing import Any, List
from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, pagination_params
from app.models.document import SourceDocument, DocumentChunk
from app.schemas.document import SourceDocumentResponse, DocumentChunkResponse

from app.ingestion.loader import DocumentLoader
from app.ingestion.cleaner import TextCleaner
from app.ingestion.chunker import DocumentChunker

router = APIRouter()

# Ensure raw data directory exists
RAW_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw"))
os.makedirs(RAW_DATA_DIR, exist_ok=True)


import logging

logger = logging.getLogger(__name__)

def process_document_pipeline(document_id: uuid.UUID, file_path: str, db: Session):
    """Background task to run the ingestion pipeline."""
    # Retrieve document from DB
    doc_record = db.query(SourceDocument).filter(SourceDocument.id == document_id).first()
    if not doc_record:
        logger.error(f"Document {document_id} not found in database.")
        return
        
    try:
        logger.info(f"Starting ingestion pipeline for document {document_id} at {file_path}")
        
        # 1. Load
        raw_docs = DocumentLoader.load_pdf(file_path)
        num_pages = len(raw_docs)
        raw_chars = sum(len(d.page_content) for d in raw_docs)
        logger.info(f"Loaded {num_pages} pages containing {raw_chars} characters.")
        
        # 2. Clean
        cleaned_docs = TextCleaner.clean_documents(raw_docs)
        clean_chars = sum(len(d.page_content) for d in cleaned_docs)
        logger.info(f"Cleaned text, resulting in {clean_chars} characters.")
        
        # 3. Chunk
        chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
        chunks = chunker.chunk_documents(cleaned_docs)
        num_chunks = len(chunks)
        logger.info(f"Chunker generated {num_chunks} chunks.")
        
        if num_chunks == 0:
            logger.warning(f"Document {document_id} produced 0 chunks. Marking as Failed.")
            doc_record.ingestion_status = "Failed"
            db.commit()
            return
            
        # 4. Save Chunks to Database
        inserted = 0
        for chunk in chunks:
            page_num = chunk.metadata.get("page", 0) + 1  # 1-indexed for display
            chunk_idx = chunk.metadata.get("chunk_index", 0)
            
            new_chunk = DocumentChunk(
                source_document_id=document_id,
                content=chunk.page_content,
                chunk_index=chunk_idx,
                page_number=page_num,
                chunk_metadata=chunk.metadata
            )
            db.add(new_chunk)
            inserted += 1
            
        logger.info(f"Inserted {inserted} chunks into database for document {document_id}.")
        
        # Update document status
        doc_record.ingestion_status = "Processed"
        db.commit()
        
    except Exception as e:
        doc_record.ingestion_status = "Failed"
        db.commit()
        logger.error(f"Pipeline failed for {file_path}: {str(e)}", exc_info=True)


@router.post("/upload", response_model=SourceDocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(None),
    document_type: str = Form("Scholarship Guideline"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload a PDF document and start the ingestion pipeline in the background.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    # Generate unique filename to prevent collisions
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(RAW_DATA_DIR, unique_filename)
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create database record
    new_doc = SourceDocument(
        title=title or file.filename,
        source_url=file.filename, # Using filename as fallback
        document_type=document_type,
        file_path=file_path,
        ingestion_status="Pending",
        last_verified_date=date.today()
    )
    
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # Trigger background ingestion
    background_tasks.add_task(process_document_pipeline, new_doc.id, file_path, db)
    
    return new_doc


@router.get("/", response_model=List[SourceDocumentResponse])
def get_documents(
    db: Session = Depends(get_db),
    params: dict = Depends(pagination_params)
) -> Any:
    """Retrieve all uploaded source documents."""
    return db.query(SourceDocument).offset(params["skip"]).limit(params["limit"]).all()


@router.get("/{id}", response_model=SourceDocumentResponse)
def get_document(
    id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Any:
    """Retrieve a specific document's metadata by ID."""
    document = db.query(SourceDocument).filter(SourceDocument.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{id}/chunks", response_model=List[DocumentChunkResponse])
def get_document_chunks(
    id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Any:
    """Retrieve all extracted chunks for a specific document."""
    document = db.query(SourceDocument).filter(SourceDocument.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return db.query(DocumentChunk).filter(DocumentChunk.source_document_id == id).order_by(DocumentChunk.chunk_index).all()
