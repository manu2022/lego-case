from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langfuse.decorators import langfuse_context
from config import settings
from routers import chat, multimodal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for cleanup"""
    # Startup
    print("=" * 80)
    print("🚀 Starting FastAPI application...")
    print(f"📊 Langfuse host: {settings.langfuse_base_url}")
    print(f"✅ Configuration loaded successfully")
    print(f"🤖 Models: gpt-5-mini, Phi-4-multimodal-instruct")
    print("=" * 80)
    yield
    # Shutdown: Flush Langfuse events
    print("🔄 Flushing Langfuse events...")
    langfuse_context.flush()
    print("✅ Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Question Answer API",
    description="API for text and multimodal question answering",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
# Parse CORS origins from settings (comma-separated string to list)
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
print(f"🔒 CORS enabled for origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(multimodal.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Question Answer API",
        "endpoints": {
            "POST /chat/ask": "Ask a text question",
            "POST /multimodal/ask-with-image": "Ask a question about an image (upload file - try in /docs!)",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
