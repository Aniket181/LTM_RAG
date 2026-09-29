"""
Semantic Embeddings Generator
Uses Hugging Face's local sentence-transformers to compute 384-dimensional embeddings.
Supports loading from a local filesystem directory to avoid network access.
"""

import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings

class LocalEmbedder:
    """Service to load the embedding model and compute embeddings locally."""

    _instance = None
    _model = None

    def __new__(cls):
        """Singleton pattern to ensure the model is only loaded into memory once."""
        if cls._instance is None:
            cls._instance = super(LocalEmbedder, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        """Initialize the HuggingFace embedding model."""
        model_name_or_path = getattr(settings, "embedding_model", "BAAI/bge-small-en-v1.5")
        
        # Use CPU by default, or MPS/CUDA if available
        # HuggingFaceEmbeddings uses sentence-transformers under the hood
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}  # True for cosine similarity
        
        # If the model is a local directory path, force offline mode to avoid SSL/network errors
        if os.path.exists(model_name_or_path) and os.path.isdir(model_name_or_path):
            # local_files_only applies at the sentence-transformers/transformers level
            model_kwargs['local_files_only'] = True
            model_kwargs['trust_remote_code'] = False

        self._model = HuggingFaceEmbeddings(
            model_name=model_name_or_path,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of document chunks.
        
        Args:
            texts: List of string chunks to embed.
            
        Returns:
            List of embedding vectors (384-dimensional).
        """
        if not texts:
            return []
        return self._model.embed_documents(texts)

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single search query.
        
        Args:
            query: User's search query string.
            
        Returns:
            A single embedding vector (384-dimensional).
        """
        if not query:
            return []
        return self._model.embed_query(query)

