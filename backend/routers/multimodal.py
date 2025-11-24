from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, TextContentItem, ImageContentItem, ImageUrl
from azure.core.credentials import AzureKeyCredential
from langfuse import Langfuse
import time
import base64
from config import settings


router = APIRouter(prefix="/multimodal", tags=["multimodal"])

# Initialize Azure AI Inference client for multimodal
client = ChatCompletionsClient(
    endpoint="https://foundry-service-lego.cognitiveservices.azure.com/models",
    credential=AzureKeyCredential(settings.openai_api_key),
    model="Phi-4-multimodal-instruct"
)

# Initialize Langfuse client
langfuse = Langfuse(
    secret_key=settings.langfuse_secret_key,
    public_key=settings.langfuse_public_key,
    host=settings.langfuse_base_url
)


class MultimodalResponse(BaseModel):
    question: str
    answer: str
    usage: dict


def ask_multimodal_question(question: str, image_data: str, image_format: str) -> tuple[str, dict]:
    """Ask a question about an image using the multimodal model"""
    
    # Create a Langfuse trace
    trace = langfuse.trace(
        name="multimodal_question",
        metadata={"model": "Phi-4-multimodal-instruct"}
    )
    
    # Create data URL from base64 image
    data_url = ImageUrl(url=f"data:image/{image_format};base64,{image_data}")
    
    print(f"🚀 Starting multimodal LLM call with question: {question[:50]}...")
    
    # Record start time with timestamp
    from datetime import datetime
    start_time = datetime.now()
    
    # Make the API call
    response = client.complete(
        messages=[
            SystemMessage("You are a helpful assistant that can analyze images and answer questions about them."),
            UserMessage(content=[
                TextContentItem(text=question),
                ImageContentItem(image_url=data_url)
            ]),
        ],
 
    )
    
    # Record end time
    end_time = datetime.now()
    
    answer = response.choices[0].message.content
    
    # Create usage dict
    usage = {
        "input": response.usage.prompt_tokens,
        "output": response.usage.completion_tokens,
        "total": response.usage.total_tokens
    }
    
    # Log to Langfuse with proper structure
    langfuse.generation(
        name="phi4_multimodal_completion",
        model="Phi-4-multimodal-instruct",
        model_parameters={
          #  "temperature": 0.7,
           # "max_tokens": 2048
        },
        input=[
            {"role": "system", "content": "You are a helpful assistant that can analyze images and answer questions about them."},
            {"role": "user", "content": question}
        ],
        output=answer,
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
    print(f"✅ Multimodal LLM Response received")
    print(f"   Input tokens: {usage['input']}")
    print(f"   Output tokens: {usage['output']}")
    print(f"   Total tokens: {usage['total']}")
    print(f"   Latency: {latency:.2f}s")
    
    return answer, usage


@router.post("/ask-with-image", response_model=MultimodalResponse)
async def ask_multimodal_with_file(
    question: str = Form(..., description="Your question about the image"),
    image: UploadFile = File(..., description="Image file to analyze")
):
    """Ask a question about an image (upload image file directly - works in /docs!)"""
    
    print(f"\n{'='*80}")
    print(f"📥 New multimodal request with file upload: {question}")
    print(f"📷 Image: {image.filename} ({image.content_type})")
    print(f"{'='*80}\n")
    
    try:
        # Read and encode image to base64
        image_bytes = await image.read()
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        
        # Detect image format from content type
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
        
        answer, usage = ask_multimodal_question(
            question,
            image_data,
            image_format
        )
        
        print(f"\n{'='*80}")
        print(f"🔄 Flushing Langfuse events...")
        langfuse.flush()
        print(f"✅ Flush complete - check Langfuse dashboard!")
        print(f"{'='*80}\n")
        
        return MultimodalResponse(
            question=question,
            answer=answer,
            usage=usage
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        langfuse.flush()
        raise HTTPException(status_code=500, detail=f"Error processing multimodal question: {str(e)}")

