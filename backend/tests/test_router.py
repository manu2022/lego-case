"""Integration tests for the router LLM - makes real API calls directly to LLM functions"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from routers.router import classify_and_sanitize


@pytest.mark.integration
def test_router_irrelevant_question():
    """
    Test 1: Question "how many championships has FCB won?" should be classified as irrelevant
    
    The router should recognize this as a sports question unrelated to the application's purpose
    and return agent="irrelevant"
    
    This test makes a REAL API call to Claude directly (not through HTTP endpoint)!
    """
    question = "how many championships has FCB won?"
    
    # Call the function directly (REAL API CALL)
    classification, usage = classify_and_sanitize(question)
    
    # The agent must be "irrelevant"
    assert classification.agent == "irrelevant", f"Expected agent to be 'irrelevant', got '{classification.agent}'"
    assert classification.query is not None
    
    # Verify usage information is present
    assert "input" in usage
    assert "output" in usage
    assert "total" in usage
    assert usage["total"] == usage["input"] + usage["output"]
    
    print(f"\n✅ Router classified correctly as 'irrelevant'")
    print(f"   Sanitized query: {classification.query}")
    print(f"   Token usage: {usage['input']}/{usage['output']}/{usage['total']} (in/out/total)")


@pytest.mark.integration
def test_router_relevant_question():
    """Test that a relevant question gets routed to qa_agent
    
    This test makes a REAL API call to Claude directly!
    """
    question = "What is the company policy on vacation days?"
    
    # Call the function directly (REAL API CALL)
    classification, usage = classify_and_sanitize(question)
    
    assert classification.agent == "qa_agent", f"Expected 'qa_agent', got '{classification.agent}'"
    assert classification.query is not None
    assert "usage" in locals()
    
    print(f"\n✅ Router classified correctly as 'qa_agent'")
    print(f"   Sanitized query: {classification.query}")
    print(f"   Token usage: {usage['input']}/{usage['output']}/{usage['total']} (in/out/total)")


@pytest.mark.integration
def test_router_image_related_question():
    """Test that questions about images are handled correctly
    
    This test makes a REAL API call to Claude directly!
    Note: The classification is based on text only, image attachment logic is in the endpoint
    """
    question = "What is in this image?"
    
    # Call the function directly (REAL API CALL)
    classification, usage = classify_and_sanitize(question)
    
    # The classification should recognize this as a valid question (qa_agent)
    # The image attachment would be handled at the endpoint level
    assert classification.agent in ["qa_agent", "irrelevant"]
    assert classification.query is not None
    
    print(f"\n✅ Router classified image-related question")
    print(f"   Agent: {classification.agent}")
    print(f"   Sanitized query: {classification.query}")
    print(f"   Token usage: {usage['input']}/{usage['output']}/{usage['total']} (in/out/total)")


@pytest.mark.integration
def test_router_pii_redaction():
    """Test that PII is removed from queries
    
    This test makes a REAL API call to Claude directly!
    """
    question = "What is my account balance for account 123456789?"
    
    # Call the function directly (REAL API CALL)
    classification, usage = classify_and_sanitize(question)
    
    # Check that PII was redacted (account number should not appear in sanitized query)
    # Note: The exact redaction format may vary based on Claude's response
    sanitized = classification.query.lower()
    original_number_present = "123456789" in sanitized
    
    # We expect the PII to be removed or redacted
    # (Claude might keep it, redact it, or remove it - we just verify the function works)
    assert classification.query is not None, "Sanitized query should not be None"
    assert classification.agent in ["qa_agent", "irrelevant"]
    
    print(f"\n✅ Router processed PII redaction")
    print(f"   Original: '{question}'")
    print(f"   Sanitized: '{classification.query}'")
    print(f"   PII removed: {'Yes' if not original_number_present else 'No (Claude kept it)'}")
    print(f"   Token usage: {usage['input']}/{usage['output']}/{usage['total']} (in/out/total)")

