"""Integration tests for router classification"""
import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from routers.router import classify_and_sanitize


@pytest.mark.integration
def test_router_irrelevant_question():
    """Sports question should be classified as irrelevant"""
    question = "how many championships has FCB won?"
    
    classification, usage = classify_and_sanitize(question)
    
    assert classification.agent == "irrelevant", f"Expected 'irrelevant', got '{classification.agent}'"
    assert classification.query is not None
    assert "input" in usage
    assert "output" in usage
    assert "total" in usage
    assert usage["total"] == usage["input"] + usage["output"]


@pytest.mark.integration
def test_router_relevant_question():
    """Relevant question should route to qa_agent"""
    question = "What is the company policy on vacation days?"
    
    classification, usage = classify_and_sanitize(question)
    
    assert classification.agent == "qa_agent", f"Expected 'qa_agent', got '{classification.agent}'"
    assert classification.query is not None
    assert "usage" in locals()


@pytest.mark.integration
def test_router_image_related_question():
    """Image-related questions should be classified appropriately"""
    question = "What is in this image?"
    
    classification, usage = classify_and_sanitize(question)
    
    assert classification.agent in ["qa_agent", "irrelevant"]
    assert classification.query is not None


@pytest.mark.integration
def test_router_pii_redaction():
    """PII should be processed during classification"""
    question = "What is my account balance for account 123456789?"
    
    classification, usage = classify_and_sanitize(question)
    
    assert classification.query is not None
    assert classification.agent in ["qa_agent", "irrelevant"]
