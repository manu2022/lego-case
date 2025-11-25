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
    sanitized_query: str
    agent: str


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
    image: Optional[UploadFile] = File(default=None)
):
    """
    Single endpoint for query classification and PII redaction
    
    - Classifies query intent (based on text only)
    - Removes PII from query
    - Determines agent based on classification + image presence:
      * irrelevant → irrelevant
      * Text only → qa_agent
      * Text + image → multimodal_agent
    - Returns sanitized query and selected agent
    
    Note: This endpoint does NOT execute the query, only classifies and sanitizes it
    """
    
    # Handle empty file uploads from forms (FastAPI/Swagger sends empty string)
    has_image = image is not None and image.filename
    
    print(f"\n{'='*80}")
    print(f"📥 New routing request: {question[:50]}...")
    if has_image:
        print(f"📎 File attached: {image.filename}")
    else:
        print("📝 Text only query")
    print(f"{'='*80}\n")
    
    try:
        # Step 1: Classify and sanitize
        classification = classify_and_sanitize(question)
        
        print(f"✅ Classification result:")
        print(f"   Agent: {classification.agent}")
        print(f"   Sanitized query: {classification.query}")
        
        # Step 2: Determine agent based on classification and image presence
        if classification.agent == "irrelevant":
            print("🚫 Query classified as irrelevant")
            selected_agent = "irrelevant"
        elif has_image:
            print("✅ Selected agent: multimodal_agent (image attached)")
            selected_agent = "multimodal_agent"
        else:
            print("✅ Selected agent: qa_agent (text only)")
            selected_agent = "qa_agent"
        
        return FinalResponse(
            sanitized_query=classification.query,
            agent=selected_agent
        )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in routing: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

