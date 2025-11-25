import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def test_client():
    from app import app
    return TestClient(app)


@pytest.fixture
def sample_pdf_path():
    return Path(__file__).parent / "test.pdf"


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
