from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import AzureOpenAI  # Use Langfuse's wrapped AzureOpenAI
from contextlib import asynccontextmanager
import os


# Settings configuration
class Settings(BaseSettings):
    """Settings loaded from environment variables or .env file"""
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True
    )
    
    openai_api_key: str
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_base_url: str = "http://langfuse.legocase.com"


# Load settings
settings = Settings()

# Set Langfuse environment variables (required for decorator)
os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
os.environ["LANGFUSE_HOST"] = settings.langfuse_base_url

# Create Azure OpenAI client wrapped with Langfuse
# This automatically captures tokens, costs, and traces!
azure_client = AzureOpenAI(
    api_key=settings.openai_api_key,
    api_version="2024-02-01",
    azure_endpoint="https://foundry-service-lego.openai.azure.com"
)

deployment_name = "gpt-5-mini"


# Request and Response models
class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    question: str
    answer: str


# Lifespan context manager for cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up - Langfuse initialized")
    print(f"📊 Langfuse host: {settings.langfuse_base_url}")
    yield
    # Shutdown: Flush Langfuse events
    print("🔄 Flushing Langfuse events...")
    langfuse_context.flush()
    print("✅ Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Question Answer API",
    description="A simple API to ask questions and get answers from GPT-5 Mini",
    version="1.0.0",
    lifespan=lifespan
)


@observe()
def ask_question(question: str) -> str:
    """Ask a question and get an answer from the LLM - Langfuse wrapper auto-captures everything!"""
    
    # Prepare messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides accurate and concise answers."
        },
        {
            "role": "user",
            "content": question,
        }
    ]
    
    print(f"🚀 Starting LLM call with question: {question[:50]}...")
    
    # Make API call - Langfuse wrapper automatically captures:
    # - Tokens (input, output, total)
    # - Model info
    # - Latency
    # - Input/output
    completion = azure_client.chat.completions.create(
        model=deployment_name,
        messages=messages
    )
    
    answer = completion.choices[0].message.content
    
    # DEBUG: Log what was captured
    print(f"✅ LLM Response received")
    print(f"   Input tokens: {completion.usage.prompt_tokens}")
    print(f"   Output tokens: {completion.usage.completion_tokens}")
    print(f"   Total tokens: {completion.usage.total_tokens}")
    print(f"   ℹ️  Langfuse wrapper should have auto-captured all this!")
    
    return answer


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Question Answer API",
        "endpoints": {
            "POST /ask": "Ask a question",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/ask", response_model=AnswerResponse)
@observe()
async def ask(request: QuestionRequest):
    """
    Ask a question and get an answer from the LLM
    
    Args:
        request: QuestionRequest with the question to ask
        
    Returns:
        AnswerResponse with the question and answer
    """
    print(f"\n{'='*80}")
    print(f"📥 New request received: {request.question}")
    print(f"{'='*80}\n")
    
    try:
        answer = ask_question(request.question)
        
        print(f"\n{'='*80}")
        print(f"🔄 Flushing Langfuse events...")
        langfuse_context.flush()
        print(f"✅ Flush complete - check Langfuse dashboard!")
        print(f"{'='*80}\n")
        
        return AnswerResponse(
            question=request.question,
            answer=answer
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        # Flush even on error to capture the failed trace
        langfuse_context.flush()
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

