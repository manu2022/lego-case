# PeaceCorpGPT: Multimodal Multiagent Chatbot with LLMOps

An intelligent multimodal question-answering system that routes queries to specialized AI agents based on content complexity. Built with a multi-agent architecture, the system has a router that addresses the questions to the right answer, handling PII and sensitive data, with full observability through Langfuse.

## 📖 Documentation

For detailed architecture, requirements, and design decisions, visit our [GitHub Pages Documentation](https://manu2022.github.io/lego-case/).

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

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ and `uv` package manager
- Node.js 18+ and npm
- Azure Cloud subcription
- Langfuse account for observability

### Backend Setup

```bash
cd backend
uv sync                   
uv run uvicorn app:app --reload 
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install               
npm run dev              
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
| `/` | GET | Root endpoint with API info |
| `/health` | GET | Health check |
| `/router/ask` | POST | Main endpoint with intelligent routing and PII redaction |
| `/chat/ask` | POST | Direct text chat (no routing) |
| `/multimodal/ask-with-image` | POST | Direct multimodal endpoint (no routing) |
| `/docs` | GET | Interactive API documentation (Swagger UI) |



## 🐳 Docker Deployment

Both backend and frontend include `Dockerfile` and `deploy.sh` scripts for containerized deployment to azure.

## Key Features

### Multi-Agent Architecture with Intelligent Router Agent**: Analyzes query complexity and selects optimal agent

### Multimodal Capabilities
- **Image + Text Processing**: Upload images with questions for visual understanding
- **Flexible Input**: Supports text-only queries or combined image-text queries or oother types as pdf
- **Base64 Image Encoding**: Efficient image transmission to AI models

### LLMOps & Observability
- **Langfuse Integration**: Full request/response tracing and monitoring
- **Performance Metrics**: Track latency, token usage, and costs per query
- **A/B Testing Ready**: Infrastructure supports model comparison and experimentation

### Production-Ready
- **FastAPI Backend**: Async, high-performance API with automatic OpenAPI docs
- **Type Safety**: Pydantic schemas and TypeScript for end-to-end type checking
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Container-Ready**: Docker support for both frontend and backend
- **Cloud Native**: Terraform IaC for Azure Container Apps deployment

---

For more details, see the [complete documentation](https://manu2022.github.io/lego-case/).
