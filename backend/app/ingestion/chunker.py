"""
Document Chunker
Splits long documents into smaller chunks for vector embeddings using LangChain's RecursiveCharacterTextSplitter.
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    """Handles splitting of documents into optimal chunks for RAG."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size (int): The maximum number of characters per chunk.
            chunk_overlap (int): The number of overlapping characters between chunks.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of Documents into chunks.
        
        Args:
            documents: List of LangChain Documents.
            
        Returns:
            List[Document]: The chunked documents. Each chunk retains the metadata of its parent.
        """
        if not documents:
            return []
            
        chunks = self.splitter.split_documents(documents)
        
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            
        return chunks
