"""Integration tests for the multimodal LLM - makes real API calls directly to LLM functions"""
import pytest
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from routers.multimodal import ask_multimodal_question, pdf_to_images
import base64


@pytest.mark.integration
def test_multimodal_pdf_revenue_question(sample_pdf_path):
    """
    Test 2: Send test.pdf with question "what was revenue in 2016"
    
    The answer must contain "90" based on the PDF content
    
    This test makes a REAL API call to the multimodal LLM directly (not through HTTP endpoint)!
    """
    # Check if test.pdf exists
    if not sample_pdf_path.exists():
        pytest.skip(f"test.pdf not found at {sample_pdf_path}")
    
    # Read the PDF file
    with open(sample_pdf_path, "rb") as f:
        pdf_content = f.read()
    
    # Convert PDF to images
    pdf_images = pdf_to_images(pdf_content, max_pages=5)
    
    assert len(pdf_images) > 0, "PDF should have at least one page"
    
    # Use the first page
    image_data, image_format = pdf_images[0]
    
    question = "what was revenue in 2016"
    
    # Call the function directly (REAL API CALL)
    answer, usage = ask_multimodal_question(question, image_data, image_format)
    
    # The answer must contain "90"
    assert "90" in answer, f"Expected answer to contain '90', got: {answer}"
    assert len(answer) > 0
    
    # Verify usage
    assert "input" in usage
    assert "output" in usage
    assert "total" in usage
    
    print(f"\n✅ Multimodal PDF test passed - answer contains '90'")
    print(f"   Question: {question}")
    print(f"   Answer: {answer[:150]}...")
    print(f"   Token usage: {usage['input']}/{usage['output']}/{usage['total']} (in/out/total)")
    print(f"   Pages processed: {len(pdf_images)}")
