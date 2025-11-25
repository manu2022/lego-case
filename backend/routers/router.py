from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, Tuple
from langfuse.decorators import observe
from langfuse import Langfuse
from anthropic import AnthropicFoundry
from datetime import datetime
import json
import logging

from config import settings
from schemas import RouterResponse, FinalResponse
from prompts import ROUTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

langfuse = Langfuse(
    secret_key=settings.langfuse_secret_key,
    public_key=settings.langfuse_public_key,
    host=settings.langfuse_base_url
)

router_api = APIRouter(prefix="/router", tags=["router"])


def get_claude_client():
    """Lazy-load Claude client to avoid startup issues"""
    return AnthropicFoundry(
        api_key=settings.claude_api_key,
        base_url=settings.claude_endpoint
    )


@observe()
def classify_and_sanitize(query: str) -> Tuple[RouterResponse, dict]:
    """Classify query and remove PII using Claude
    
    Returns:
        Tuple of (RouterResponse, usage_dict)
    """
    
    user_message = f"{ROUTER_SYSTEM_PROMPT}\n\nUser query: {query}"
    
    logger.info(f"Routing query: {query[:50]}...")
    
    # Create Langfuse trace for tracking
    trace = langfuse.trace(
        name="router_classification",
        metadata={"model": settings.claude_deployment_name}
    )
    
    start_time = datetime.now()
    
    claude_client = get_claude_client()
    message = claude_client.messages.create(
        model=settings.claude_deployment_name,
        messages=[
            {"role": "user", "content": user_message}
        ],
        max_tokens=1024
    )
    
    end_time = datetime.now()
    
    response_text = message.content[0].text
    logger.debug(f"Router raw response: {response_text}")
    
    # Extract usage information
    usage = {
        "input": message.usage.input_tokens,
        "output": message.usage.output_tokens,
        "total": message.usage.input_tokens + message.usage.output_tokens
    }
    
    # Log usage to Langfuse
    langfuse.generation(
        name="claude_router_completion",
        model=settings.claude_deployment_name,
        model_parameters={"max_tokens": 1024},
        input=[
            {"role": "user", "content": user_message}
        ],
        output=response_text,
        usage={
            "input": usage["input"],
            "output": usage["output"],
            "total": usage["total"],
            "unit": "TOKENS"
        },
        start_time=start_time,
        end_time=end_time,
        trace_id=trace.id
    )
    
    latency = (end_time - start_time).total_seconds()
    logger.info(
        f"Router LLM response received. "
        f"Tokens: {usage['input']}/{usage['output']}/{usage['total']} (in/out/total). "
        f"Latency: {latency:.2f}s"
    )
    
    # Strip markdown code blocks if present
    if response_text.strip().startswith("```"):
        lines = response_text.strip().split("\n")
        response_text = "\n".join(lines[1:-1])
        logger.debug(f"Cleaned response: {response_text}")
    
    try:
        response_data = json.loads(response_text)
        return RouterResponse(**response_data), usage
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse router response: {e}")
        logger.error(f"Raw response: {response_text}")
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
    
    has_image = image is not None and image.filename
    
    logger.info(f"New routing request: {question[:50]}...")
    if has_image:
        logger.info(f"File attached: {image.filename}")
    else:
        logger.info("Text only query")
    
    try:
        # Step 1: Classify and sanitize
        classification, usage = classify_and_sanitize(question)
        
        logger.info(f"Classification result: agent={classification.agent}")
        logger.debug(f"Sanitized query: {classification.query}")
        
        # Step 2: Determine agent based on classification and image presence
        if classification.agent == "irrelevant":
            logger.info("Query classified as irrelevant")
            selected_agent = "irrelevant"
        elif has_image:
            logger.info("Selected agent: multimodal_agent (image attached)")
            selected_agent = "multimodal_agent"
        else:
            logger.info("Selected agent: qa_agent (text only)")
            selected_agent = "qa_agent"
        
        # Flush Langfuse events
        langfuse.flush()
        
        return FinalResponse(
            sanitized_query=classification.query,
            agent=selected_agent,
            usage=usage
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in routing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

