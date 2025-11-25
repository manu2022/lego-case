from fastapi import APIRouter, HTTPException
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import AzureOpenAI

from config import settings
from schemas import QuestionRequest, AnswerResponse
from prompts import CHAT_SYSTEM_PROMPT

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
    
    print(f"🚀 Starting LLM call with question: {question[:50]}...")
    
    completion = azure_client.chat.completions.create(
        model=deployment_name,
        messages=messages
    )
    
    answer = completion.choices[0].message.content
    
    print(f"✅ LLM Response received")
    print(f"   Input tokens: {completion.usage.prompt_tokens}")
    print(f"   Output tokens: {completion.usage.completion_tokens}")
    print(f"   Total tokens: {completion.usage.total_tokens}")
    print(f"   ℹ️  Langfuse wrapper should have auto-captured all this!")
    
    return answer


@router.post("/ask", response_model=AnswerResponse)
@observe()
async def ask(request: QuestionRequest):
    """Ask a question and get an answer from the LLM"""
    
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
        langfuse_context.flush()
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

