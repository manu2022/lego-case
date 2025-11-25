from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, TextContentItem, ImageContentItem, ImageUrl
from azure.core.credentials import AzureKeyCredential
from langfuse import Langfuse
from datetime import datetime
import base64
import logging
from typing import Optional

from config import settings
from schemas import MultimodalResponse
from prompts import MULTIMODAL_SYSTEM_PROMPT

# Configure logging
logger = logging.getLogger(__name__)

# Try to import PDF processing libraries
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("PyMuPDF not installed. PDF support disabled. Install with: pip install PyMuPDF")


router = APIRouter(prefix="/multimodal", tags=["multimodal"])

# Initialize Azure AI Inference client for multimodal
client = ChatCompletionsClient(
    endpoint=settings.azure_ai_foundry_endpoint,
    credential=AzureKeyCredential(settings.openai_api_key),
    model=settings.multimodal_model_name
)

# Initialize Langfuse client
langfuse = Langfuse(
    secret_key=settings.langfuse_secret_key,
    public_key=settings.langfuse_public_key,
    host=settings.langfuse_base_url
)


def pdf_to_images(pdf_bytes: bytes, max_pages: int = 5) -> list[tuple[str, str]]:
    """Convert PDF pages to base64-encoded images
    
    Args:
        pdf_bytes: PDF file content as bytes
        max_pages: Maximum number of pages to process (default: 5)
        
    Returns:
        List of tuples (base64_image_data, format)
    """
    if not PDF_SUPPORT:
        raise HTTPException(
            status_code=400, 
            detail="PDF processing not supported. PyMuPDF library not installed."
        )
    
    try:
        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        images = []
        
        # Process pages (limit to max_pages to avoid overwhelming the model)
        num_pages = min(len(pdf_document), max_pages)
        
        for page_num in range(num_pages):
            page = pdf_document[page_num]
            
            # Render page to image (PNG format, 150 DPI for good quality)
            pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
            
            # Convert to PNG bytes
            img_bytes = pix.tobytes("png")
            
            # Encode to base64
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            
            images.append((img_base64, "png"))
        
        pdf_document.close()
        
        logger.info(f"Converted {num_pages} PDF page(s) to images")
        return images
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")


def ask_multimodal_question(question: str, image_data: str, image_format: str) -> tuple[str, dict]:
    """Ask a question about an image using the multimodal model"""
    
    trace = langfuse.trace(
        name="multimodal_question",
        metadata={"model": settings.multimodal_model_name}
    )
    
    data_url = ImageUrl(url=f"data:image/{image_format};base64,{image_data}")
    
    logger.info(f"Starting multimodal LLM call with {settings.multimodal_model_name}. Question: {question[:50]}...")
    start_time = datetime.now()
    
    response = client.complete(
        messages=[
            SystemMessage(MULTIMODAL_SYSTEM_PROMPT),
            UserMessage(content=[
                TextContentItem(text=question),
                ImageContentItem(image_url=data_url)
            ]),
        ],
    )
    
    end_time = datetime.now()
    answer = response.choices[0].message.content
    
    usage = {
        "input": response.usage.prompt_tokens,
        "output": response.usage.completion_tokens,
        "total": response.usage.total_tokens
    }
    
    langfuse.generation(
        name="multimodal_completion",
        model=settings.multimodal_model_name,
        model_parameters={},
        input=[
            {"role": "system", "content": MULTIMODAL_SYSTEM_PROMPT},
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
    logger.info(
        f"Multimodal LLM response received. "
        f"Tokens: {usage['input']}/{usage['output']}/{usage['total']} (in/out/total). "
        f"Latency: {latency:.2f}s"
    )
    
    return answer, usage


@router.post("/ask-with-image", response_model=MultimodalResponse)
async def ask_multimodal_with_file(
    question: str = Form(..., description="Your question about the image or PDF"),
    image: UploadFile = File(..., description="Image or PDF file to analyze")
):
    """Ask a question about an image or PDF document
    
    Supports:
    - Images: JPEG, PNG, GIF, WEBP
    - PDFs: Converts first 5 pages to images and analyzes them
    
    For PDFs with multiple pages, all pages are analyzed together.
    """
    
    logger.info(f"New multimodal request. File: {image.filename} ({image.content_type})")
    logger.debug(f"Question: {question}")
    
    try:
        file_bytes = await image.read()
        file_type = "image"
        pages_processed = None
        
        # Check if it's a PDF
        is_pdf = (
            image.content_type == "application/pdf" or 
            (image.filename and image.filename.lower().endswith('.pdf'))
        )
        
        if is_pdf:
            logger.info("Processing PDF file")
            file_type = "pdf"
            
            pdf_images = pdf_to_images(file_bytes, max_pages=5)
            pages_processed = len(pdf_images)
            
            if len(pdf_images) == 1:
                image_data, image_format = pdf_images[0]
                answer, usage = ask_multimodal_question(question, image_data, image_format)
            else:
                logger.info(f"Processing multi-page PDF with {len(pdf_images)} pages")
                all_answers = []
                total_usage = {"input": 0, "output": 0, "total": 0}
                
                for idx, (img_data, img_format) in enumerate(pdf_images, 1):
                    page_question = f"Page {idx} of the document: {question}"
                    answer, usage = ask_multimodal_question(page_question, img_data, img_format)
                    all_answers.append(f"**Page {idx}:**\n{answer}")
                    
                    total_usage["input"] += usage["input"]
                    total_usage["output"] += usage["output"]
                    total_usage["total"] += usage["total"]
                
                answer = "\n\n".join(all_answers)
                usage = total_usage
                
        else:
            logger.info("Processing image file")
            image_data = base64.b64encode(file_bytes).decode("utf-8")
            
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
            
            answer, usage = ask_multimodal_question(question, image_data, image_format)
        
        langfuse.flush()
        logger.info("Request completed successfully")
        
        return MultimodalResponse(
            question=question,
            answer=answer,
            usage=usage,
            file_type=file_type,
            pages_processed=pages_processed
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing multimodal question: {str(e)}", exc_info=True)
        langfuse.flush()
        raise HTTPException(status_code=500, detail=f"Error processing multimodal question: {str(e)}")

