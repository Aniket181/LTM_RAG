"""
PDF Document Loader
Uses LangChain's PyPDFLoader to extract text from PDF files.
"""

import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

class DocumentLoader:
    """Handles the extraction of raw text from PDF files."""

    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        """
        Loads a PDF file and extracts text page by page.
        
        Args:
            file_path: Absolute or relative path to the PDF file.
            
        Returns:
            List[Document]: A list of LangChain Document objects containing page_content and metadata.
            
        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the file is not a valid PDF or cannot be parsed.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Ensure metadata has the source path
            for doc in documents:
                doc.metadata["source"] = file_path
                
            return documents
        except Exception as e:
            raise ValueError(f"Failed to parse PDF {file_path}. Error: {str(e)}")
