# Backend LLM Integration Tests

This directory contains **real integration tests** that make actual API calls to LLM services.

## ⚠️ Important

These tests:
- ✅ Make **REAL API calls** to Claude and Azure AI
- ✅ Call LLM functions **directly** (not through HTTP endpoints)
- ✅ Take **several seconds** to run
- ✅ **Cost money** (consume API tokens)
- ✅ **Require valid API keys** in your environment

## Setup

### 1. Navigate to the backend directory
```bash
cd backend
```

### 2. Install the test dependencies
```bash
# Using uv (recommended) - make sure you're in the backend/ directory!
uv pip install pytest pytest-asyncio

# OR using pip
pip install pytest pytest-asyncio
```

### 3. Ensure API keys are configured
Make sure you have a `.env` file in the backend directory with:
```bash
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here
LANGFUSE_SECRET_KEY=your_key_here
LANGFUSE_PUBLIC_KEY=your_key_here
LANGFUSE_BASE_URL=your_langfuse_url_here
```

**Important:** These are **integration tests** - they will actually call the LLM APIs!

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test files
```bash
# Test router endpoint
pytest tests/test_router.py

# Test multimodal endpoint
pytest tests/test_multimodal.py
```

### Run specific test functions
```bash
# Test irrelevant question classification
pytest tests/test_router.py::test_router_irrelevant_question

# Test PDF revenue question
pytest tests/test_multimodal.py::test_multimodal_pdf_revenue_question
```

### Run with verbose output
```bash
pytest -v
```

### Run with detailed output and logs
```bash
pytest -v -s
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in your browser to see the report
```

## Test Structure

### test_router.py - Router LLM Tests
Tests the `classify_and_sanitize()` function **directly** by calling Claude:
- **test_router_irrelevant_question**: ✅ Tests that "how many championships has FCB won?" is classified as `agent="irrelevant"` (REAL Claude API call)
- **test_router_relevant_question**: Tests routing of relevant questions to `qa_agent` (REAL Claude API call)
- **test_router_image_related_question**: Tests classification of image-related questions (REAL Claude API call)
- **test_router_pii_redaction**: Tests PII handling in queries (REAL Claude API call)

### test_multimodal.py - Multimodal LLM Tests
Tests the `ask_multimodal_question()` function **directly** by calling Azure AI:
- **test_multimodal_pdf_revenue_question**: ✅ Tests PDF analysis with `test.pdf` - verifies that asking "what was revenue in 2016" returns an answer containing "90" (REAL Azure AI API call)

## Test Requirements

- ⚠️ The tests make **REAL API calls** to Claude and Azure AI services
- 💰 Tests **cost money** (they consume API tokens)
- 🔑 Tests **require valid API keys** configured in `.env`
- 📄 For the PDF test, the `test.pdf` file is located in the `tests/` directory
- ⏱️ Tests take **several seconds** to run (expect 2-10 seconds per test)
- 🎯 Tests call LLM functions **directly**, not through HTTP endpoints

## How It Works

These are **true integration tests** that:
1. Import the LLM functions directly from `routers/router.py` and `routers/multimodal.py`
2. Call the functions with real inputs
3. Make actual API calls to Claude and Azure AI
4. Verify the real LLM responses

Example:
```python
# This is what the test does:
from routers.router import classify_and_sanitize

# Call the function directly - makes REAL API call to Claude!
classification, usage = classify_and_sanitize("how many championships has FCB won?")

# Verify the real response
assert classification.agent == "irrelevant"
```

## Fixtures

Available fixtures (defined in `conftest.py`):
- `sample_pdf_path`: Path to the test.pdf file

## Expected Runtime

- **test_router_irrelevant_question**: ~2-5 seconds
- **test_router_relevant_question**: ~2-5 seconds  
- **test_router_image_related_question**: ~2-5 seconds
- **test_router_pii_redaction**: ~2-5 seconds
- **test_multimodal_pdf_revenue_question**: ~5-10 seconds (PDF processing + LLM call)

**Total**: Expect ~15-30 seconds for all tests

