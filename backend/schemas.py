"""Pydantic schemas for API request/response models"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class QuestionRequest(BaseModel):
    """Request model for text-only questions"""
    question: str = Field(..., description="The question to ask the LLM")


class AnswerResponse(BaseModel):
    """Response model for text-only questions"""
    question: str
    answer: str


class MultimodalResponse(BaseModel):
    """Response model for multimodal (image) questions"""
    question: str
    answer: str
    usage: dict
    file_type: str = Field(default="image", description="Type of file processed (image or pdf)")
    pages_processed: Optional[int] = Field(default=None, description="Number of pages processed for PDFs")


class RouterResponse(BaseModel):
    """Response from router classification"""
    agent: Literal["qa_agent", "irrelevant"] = Field(..., description="Selected agent")
    query: str = Field(..., description="Sanitized query with PII removed")


class FinalResponse(BaseModel):
    """Final response from router to user"""
    sanitized_query: str
    agent: str
    usage: dict = Field(..., description="Token usage information")

