"""
LLM Factory
Instantiates language models based on the configured provider.
"""
from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from app.core.config import settings

def get_llm() -> BaseChatModel:
    """
    Factory function to return the configured LLM.
    Raises ValueError if provider is unsupported or improperly configured.
    """
    if settings.llm_provider == "mock":
        try:
            from langchain_community.chat_models.fake import FakeListChatModel
        except ImportError:
            from langchain_core.language_models.fake_chat_models import FakeListChatModel
        # Return a simple fake model for testing
        return FakeListChatModel(responses=["I don't know based on the provided documents."])
        
    elif settings.llm_provider == "ollama":
        try:
            from langchain_community.chat_models import ChatOllama
        except ImportError:
            from langchain_ollama import ChatOllama
            
        if not settings.ollama_base_url or not settings.ollama_model:
            raise ValueError("OLLAMA_BASE_URL and OLLAMA_MODEL must be configured when llm_provider='ollama'.")
            
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.0  # We want deterministic grounded responses
        )
        
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}. Supported: mock, ollama")
