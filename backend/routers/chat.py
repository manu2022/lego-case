from fastapi import APIRouter, HTTPException
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import AzureOpenAI
import logging

from config import settings
from schemas import QuestionRequest, AnswerResponse
from prompts import CHAT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

azure_client = AzureOpenAI(
    api_key=settings.openai_api_key,
    api_version="2024-02-01",
    azure_endpoint="https://foundry-service-lego.openai.azure.com"
)

deployment_name = "gpt-5-mini"


@observe()
def ask_question(question: str) -> str:
    """Ask a question and get an answer from the LLM"""
    
    messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    logger.info(f"Starting LLM call. Question: {question[:50]}...")
    
    completion = azure_client.chat.completions.create(
        model=deployment_name,
        messages=messages
    )
    
    answer = completion.choices[0].message.content
    
    logger.info(
        f"LLM response received. "
        f"Tokens: {completion.usage.prompt_tokens}/{completion.usage.completion_tokens}/{completion.usage.total_tokens} (in/out/total)"
    )
    
    return answer


@router.post("/ask", response_model=AnswerResponse)
@observe()
async def ask(request: QuestionRequest):
    """Ask a question and get an answer from the LLM"""
    
    logger.info(f"New chat request received")
    logger.debug(f"Question: {request.question}")
    
    try:
        answer = ask_question(request.question)
        langfuse_context.flush()
        logger.info("Request completed successfully")
        
        return AnswerResponse(
            question=request.question,
            answer=answer
        )
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        langfuse_context.flush()
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

