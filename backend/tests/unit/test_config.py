"""
Unit Tests — Application Configuration
Tests for the Pydantic Settings config module.
"""

import pytest

from app.core.config import Settings, get_settings


class TestSettings:
    """Tests for application configuration loading."""

    def test_default_app_name(self) -> None:
        """App name should have a sensible default."""
        s = Settings()
        assert "RAG" in s.app_name or "Scholarship" in s.app_name

    def test_default_llm_provider_is_mock(self) -> None:
        """Default LLM provider must be 'mock' (no API key required)."""
        s = Settings()
        assert s.llm_provider == "mock"

    def test_default_vector_store_is_chromadb(self) -> None:
        """Default vector store must be 'chromadb' for development."""
        s = Settings()
        assert s.vector_store_type == "chromadb"

    def test_database_url_construction(self) -> None:
        """Database URL must be correctly assembled from components."""
        s = Settings(
            postgres_user="testuser",
            postgres_password="testpass",
            postgres_host="localhost",
            postgres_port=5432,
            postgres_db="testdb",
        )
        assert s.database_url == "postgresql://testuser:testpass@localhost:5432/testdb"

    def test_cors_origins_list_parsed(self) -> None:
        """CORS origins string must be parsed into a list."""
        s = Settings(cors_origins="http://localhost:3000,http://localhost:8080")
        origins = s.cors_origins_list
        assert isinstance(origins, list)
        assert "http://localhost:3000" in origins
        assert "http://localhost:8080" in origins

    def test_invalid_log_level_raises(self) -> None:
        """Invalid log level should raise a ValueError."""
        with pytest.raises(Exception):
            Settings(log_level="VERBOSE")

    def test_valid_log_levels(self) -> None:
        """All standard log levels should be accepted."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            s = Settings(log_level=level)
            assert s.log_level == level

    def test_settings_singleton(self) -> None:
        """get_settings() should return the same cached instance."""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_retrieval_top_k_default(self) -> None:
        """Default retrieval top-K should be 5."""
        s = Settings()
        assert s.retrieval_top_k == 5

    def test_chunk_size_default(self) -> None:
        """Default chunk size should be 512."""
        s = Settings()
        assert s.chunk_size == 512
