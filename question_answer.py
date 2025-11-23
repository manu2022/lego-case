from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from langfuse import observe, get_client
from langfuse.openai import OpenAI
from contextlib import asynccontextmanager


# Settings configuration
class Settings(BaseSettings):
    """Settings loaded from .env file"""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    openai_api_key: str
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_base_url: str = "http://langfuse.legocase.com"


# Load settings
settings = Settings()

# Initialize OpenAI client
endpoint = "https://foundry-service-lego.openai.azure.com/openai/v1"
deployment_name = "gpt-5-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=settings.openai_api_key
)


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
    yield
    # Shutdown: Flush Langfuse events
    langfuse = get_client()
    langfuse.flush()


# Initialize FastAPI app
app = FastAPI(
    title="Question Answer API",
    description="A simple API to ask questions and get answers from GPT-5 Mini",
    version="1.0.0",
    lifespan=lifespan
)


@observe()
def ask_question(question: str) -> str:
    """Ask a question and get an answer from the LLM"""
    completion = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        name="gpt-5-mini-question",  # Name for identification in Langfuse
        metadata={
            "model": "gpt-5-mini",
            "endpoint": "azure-openai",
            "question_type": "general_knowledge"
        }
    )
    
    answer = completion.choices[0].message.content
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
async def ask(request: QuestionRequest):
    """
    Ask a question and get an answer from the LLM
    
    Args:
        request: QuestionRequest with the question to ask
        
    Returns:
        AnswerResponse with the question and answer
    """
    try:
        answer = ask_question(request.question)
        return AnswerResponse(
            question=request.question,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
