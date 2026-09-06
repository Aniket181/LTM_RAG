"""
Pytest Configuration and Shared Fixtures
All tests in this project use this conftest.py for shared setup.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Provide a synchronous FastAPI test client for the duration of the test session.
    This client does not require a running server.
    """
    with TestClient(app) as c:
        yield c
