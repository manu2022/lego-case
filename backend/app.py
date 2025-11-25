from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langfuse.decorators import langfuse_context
import logging

from config import settings
from routers import chat, multimodal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for cleanup"""
    # Startup
    logger.info("Starting FastAPI application")
    logger.info(f"Langfuse host: {settings.langfuse_base_url}")
    logger.info("Configuration loaded successfully")
    logger.info("Models: gpt-5-mini, Phi-4-multimodal-instruct")
    yield
    # Shutdown
    logger.info("Flushing Langfuse events")
    langfuse_context.flush()
    logger.info("Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Question Answer API",
    description="API for text and multimodal question answering",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
logger.info(f"CORS enabled for origins: {cors_origins}")

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
