---
layout: default
title: PeaceCorpGPT - Multimodal Multiagent Chatbot with LLMOps
---

## 📚 Documentation Pages

- [Introduction and Feasibility](overview.md)
- [Architecture](architecture.md)
- [Functional Requirements](functional-requirements.md)
- [Non-Functional Requirements](non-functional-requirements.md)

---

# PeaceCorpGPT: Multimodal Multiagent Chatbot with LLMOps

An intelligent multimodal question-answering system that routes queries to specialized AI models based on content complexity. Built with a multi-agent architecture, the system automatically selects between OpenAI GPT-4o-mini (simple queries) and GPT-4o (complex/multimodal queries), with full observability through Langfuse.

## 🏗️ Project Structure

```
lego-case/
├── backend/                      # FastAPI backend application
│   ├── app.py                   # Main FastAPI application entry point
│   ├── config.py                # Configuration and environment management
│   ├── schemas.py               # Pydantic models for request/response validation
│   ├── prompts.py               # System prompts for different AI agents
│   ├── routers/
│   │   ├── router.py           # Intelligent query routing logic
│   │   ├── multimodal.py       # Multimodal (image + text) processing
│   │   └── chat.py             # Simple chat endpoint
│   ├── tests/                  # Comprehensive test suite
│   │   ├── test_router.py      # Router logic tests
│   │   ├── test_multimodal.py  # Multimodal endpoint tests
│   │   └── conftest.py         # Pytest fixtures and configuration
│   ├── pyproject.toml          # Python dependencies (uv/pip)
│   └── Dockerfile              # Backend containerization
│
├── frontend/                    # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx             # Main application component
│   │   ├── components/         # Reusable UI components
│   │   │   ├── ChatArea.tsx    # Message display component
│   │   │   └── InputArea.tsx   # User input with image upload
│   │   ├── hooks/              # Custom React hooks
│   │   │   └── useImageQuestion.ts  # API communication logic
│   │   └── types/              # TypeScript type definitions
│   ├── package.json            # Node dependencies
│   └── Dockerfile              # Frontend containerization
│
├── docs/                        # GitHub Pages documentation site
│   ├── index.md                # Landing page
│   ├── architecture.md         # System architecture details
│   ├── functional-requirements.md
│   ├── non-functional-requirements.md
│   └── assets/                 # Images and diagrams
│
├── terraform/                   # Infrastructure as Code (Azure)
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values
│   └── providers.tf            # Provider configurations
│
└── langfuse-on-azure/          # Observability and tracing setup
    ├── infra/                  # Bicep templates for Azure deployment
    └── scripts/                # Deployment automation scripts
```

## 🧠 How It Works

1. **User Input**: User submits a question (with optional image) via the React frontend
2. **Router Agent**: Analyzes the query using GPT-4o-mini to determine complexity
3. **Agent Selection**:
   - Simple queries → GPT-4o-mini (fast, cost-effective)
   - Complex/multimodal queries → GPT-4o (advanced reasoning)
4. **Processing**: Selected agent processes the request with appropriate context
5. **Response**: Answer returned to user with full tracing in Langfuse
6. **Observability**: All interactions logged for monitoring, debugging, and optimization

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ and `uv` package manager
- Node.js 18+ and npm
- OpenAI API key
- (Optional) Langfuse account for observability

### Backend Setup

```bash
cd backend
uv sync                    # Install dependencies with uv
uv run uvicorn app:app --reload  # Run development server
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Frontend Setup

```bash
cd frontend
npm install               # Install dependencies
npm run dev              # Run development server
```

The UI will be available at `http://localhost:5173`

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required
OPENAI_API_KEY=your_key_here

# Optional (for LLMOps observability)
LANGFUSE_SECRET_KEY=your_key_here
LANGFUSE_PUBLIC_KEY=your_key_here
LANGFUSE_BASE_URL=your_url_here

# Optional (Azure OpenAI alternative)
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
```

## 🧪 Testing

```bash
cd backend
uv run pytest -v         # Verbose output
uv run pytest tests/test_router.py  # Test routing logic
uv run pytest tests/test_multimodal.py  # Test multimodal endpoint
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/chat` | POST | Simple text chat (no routing) |
| `/multimodal` | POST | Multimodal query with intelligent routing |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

Example multimodal request:
```json
{
  "prompt": "What's in this image?",
  "image": "base64_encoded_image_string"
}
```

## 🐳 Docker Deployment

Both backend and frontend include `Dockerfile` and `deploy.sh` scripts for containerized deployment.

## Key Features

### Multi-Agent Architecture
- **Intelligent Router Agent**: Analyzes query complexity and selects optimal model
- **Simple Query Agent**: Uses GPT-4o-mini for straightforward questions (cost-effective)
- **Complex Query Agent**: Leverages GPT-4o for advanced reasoning and multimodal tasks

### Multimodal Capabilities
- **Image + Text Processing**: Upload images with questions for visual understanding
- **Flexible Input**: Supports text-only queries or combined image-text queries
- **Base64 Image Encoding**: Efficient image transmission to AI models

### LLMOps & Observability
- **Langfuse Integration**: Full request/response tracing and monitoring
- **Performance Metrics**: Track latency, token usage, and costs per query
- **Debug Mode**: Detailed logging for development and troubleshooting
- **A/B Testing Ready**: Infrastructure supports model comparison and experimentation

### Production-Ready
- **FastAPI Backend**: Async, high-performance API with automatic OpenAPI docs
- **Type Safety**: Pydantic schemas and TypeScript for end-to-end type checking
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Container-Ready**: Docker support for both frontend and backend
- **Cloud Native**: Terraform IaC for Azure Container Apps deployment

## 🛠️ Tech Stack

**Backend**
- FastAPI (Python 3.12+)
- OpenAI Python SDK (GPT-4o, GPT-4o-mini)
- Langfuse (observability)
- Pydantic (data validation)
- pytest (testing)

**Frontend**
- React 18
- TypeScript
- Vite (build tool)
- Modern CSS with responsive design

**Infrastructure**
- Azure Container Apps
- Azure Container Registry
- Terraform (IaC)
- PostgreSQL (for Langfuse)

**Development Tools**
- uv (fast Python package manager)
- ESLint + TypeScript
- Docker & Docker Compose
