"""Pytest configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import os

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    from app import app
    return TestClient(app)


@pytest.fixture
def sample_pdf_path():
    """Path to the test.pdf file"""
    return Path(__file__).parent / "test.pdf"


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (makes real API calls)"
    )

