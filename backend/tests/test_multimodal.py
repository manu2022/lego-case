"""Integration tests for multimodal functionality"""
import pytest
from pathlib import Path
import sys

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from routers.multimodal import ask_multimodal_question, pdf_to_images


@pytest.mark.integration
def test_multimodal_pdf_revenue_question(sample_pdf_path):
    """Multimodal agent should extract revenue data from PDF"""
    if not sample_pdf_path.exists():
        pytest.skip(f"test.pdf not found at {sample_pdf_path}")
    
    with open(sample_pdf_path, "rb") as f:
        pdf_content = f.read()
    
    pdf_images = pdf_to_images(pdf_content, max_pages=5)
    assert len(pdf_images) > 0
    
    image_data, image_format = pdf_images[0]
    question = "what was revenue in 2016"
    
    answer, usage = ask_multimodal_question(question, image_data, image_format)
    
    assert "90" in answer, f"Expected '90' in answer, got: {answer}"
    assert len(answer) > 0
    assert "input" in usage
    assert "output" in usage
    assert "total" in usage
