from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Literal
from langfuse.decorators import observe
from anthropic import AnthropicFoundry
import json
import base64
from config import settings

router_api = APIRouter(prefix="/router", tags=["router"])

# Claude client for intelligent routing
claude_client = AnthropicFoundry(
    api_key=settings.claude_api_key,
    base_url=settings.claude_endpoint
)

ROUTER_SYSTEM_PROMPT = """You are a query router. Classify queries and remove PII.

Output Format (JSON only):
{"agent": "<agent>", "query": "<sanitized_query>"}

Agents:
- qa_agent: Workplace questions, emails, documents, summaries
- irrelevant: Off-topic, inappropriate, or non-work queries

PII Replacement:
- Names → [NAME]
- Emails → [EMAIL]
- Phones → [PHONE]
- Addresses → [ADDRESS]
- SSN → [SSN]
- Credit cards → [CREDIT_CARD]

Example:
Input: "Summarize the email from Manuel Tena at manuel@company.com"
Output: {"agent": "qa_agent", "query": "Summarize the email from [NAME] at [EMAIL]"}

Always return ONLY valid JSON, no additional text."""


class RouterResponse(BaseModel):
    """Response from router classification"""
    agent: Literal["qa_agent", "irrelevant"] = Field(..., description="Selected agent")
    query: str = Field(..., description="Sanitized query with PII removed")


class FinalResponse(BaseModel):
    """Final response to user"""
    answer: str
    agent_used: str


@observe()
def classify_and_sanitize(query: str) -> RouterResponse:
    """Classify query and remove PII using Claude"""
    
    user_message = f"{ROUTER_SYSTEM_PROMPT}\n\nUser query: {query}"
    
    print(f"🔀 Routing query: {query[:50]}...")
    
    message = claude_client.messages.create(
        model=settings.claude_deployment_name,
        messages=[
            {"role": "user", "content": user_message}
        ],
        max_tokens=1024
    )
    
    response_text = message.content[0].text
    print(f"📋 Router response: {response_text}")
    
    # Strip markdown code blocks if present
    if response_text.strip().startswith("```"):
        lines = response_text.strip().split("\n")
        # Remove first line (```json or ```) and last line (```)
        response_text = "\n".join(lines[1:-1])
        print(f"📋 Cleaned response: {response_text}")
    
    try:
        response_data = json.loads(response_text)
        return RouterResponse(**response_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Failed to parse router response: {e}")
        print(f"   Raw response: {response_text}")
        raise HTTPException(status_code=500, detail="Failed to classify query")


@router_api.post("/ask", response_model=FinalResponse)
@observe()
async def route_query(
    question: str = Form(..., description="Your question"),
    image: Optional[UploadFile] = File(None)
):
    """
    Single endpoint for all queries - with or without images
    
    - Classifies query intent (based on text only)
    - Removes PII from query
    - Routes based on: agent classification + image presence
      * Text only → qa_agent
      * Text + image → multimodal_agent
    - Returns answer or irrelevant message
    
    Note: Image is NOT sent to router - only used for routing decision
    """
    
    has_image = image is not None
    print(f"\n{'='*80}")
    print(f"📥 New routing request: {question[:50]}...")
    if has_image:
        print(f"📎 File attached: {image.filename}")
    print(f"{'='*80}\n")
    
    try:
        # Step 1: Classify and sanitize
        classification = classify_and_sanitize(question)
        
        print(f"✅ Classification result:")
        print(f"   Agent: {classification.agent}")
        print(f"   Sanitized query: {classification.query}")
        
        # Step 2: Check if irrelevant
        if classification.agent == "irrelevant":
            print("🚫 Query classified as irrelevant")
            return FinalResponse(
                answer="Sorry, I cannot assist with that query. Please ask work-related questions.",
                agent_used="irrelevant"
            )
        
        # Step 3: Route to appropriate agent
        if has_image:
            # Route to multimodal agent
            print("✅ Routing to Multimodal agent")
            
            from routers.multimodal import ask_multimodal_question
            
            # Read and encode image
            image_bytes = await image.read()
            image_data = base64.b64encode(image_bytes).decode("utf-8")
            
            # Detect format
            image_format = "png"
            if image.content_type:
                if "jpeg" in image.content_type or "jpg" in image.content_type:
                    image_format = "jpeg"
                elif "png" in image.content_type:
                    image_format = "png"
                elif "gif" in image.content_type:
                    image_format = "gif"
                elif "webp" in image.content_type:
                    image_format = "webp"
            
            # Call multimodal
            answer, usage = ask_multimodal_question(
                classification.query,
                image_data,
                image_format
            )
            
            print(f"   Token usage: {usage['input']}/{usage['output']}/{usage['total']}")
            
            return FinalResponse(
                answer=answer,
                agent_used="multimodal_agent"
            )
        else:
            # Route to text agent
            print("✅ Routing to QA agent")
            
            from routers.chat import ask_question
            
            answer = ask_question(classification.query)
            
            return FinalResponse(
                answer=answer,
                agent_used="qa_agent"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in routing: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

