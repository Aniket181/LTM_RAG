"""
Text Cleaner
Cleans and normalizes extracted text from PDFs before chunking and embedding.
"""

import re
from typing import List
from langchain_core.documents import Document

class TextCleaner:
    """Provides utilities for cleaning raw PDF text."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans a single string of text.
        - Replaces excessive newlines with a single space.
        - Removes excessive spaces.
        - Normalizes basic unicode characters.
        """
        if not text:
            return ""
            
        # Replace 3 or more newlines with double newline to preserve paragraph breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace single newlines that are just line-wraps (followed by lower case)
        text = re.sub(r'(?<!\n)\n(?=[a-z])', ' ', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix missing spaces after punctuation
        text = re.sub(r'([.?!])([A-Z])', r'\1 \2', text)
        
        return text.strip()

    @staticmethod
    def clean_documents(documents: List[Document]) -> List[Document]:
        """
        Cleans the page_content of a list of Documents.
        
        Args:
            documents: List of LangChain Documents.
            
        Returns:
            List[Document]: The cleaned documents (modifies in place).
        """
        for doc in documents:
            doc.page_content = TextCleaner.clean_text(doc.page_content)
        return documents
