"""Pydantic schemas for API request/response models"""
from pydantic import BaseModel, Field
from typing import Optional


class QuestionRequest(BaseModel):
    """Request model for text-only questions"""
    question: str = Field(..., description="The question to ask the LLM")


class AnswerResponse(BaseModel):
    """Response model for text-only questions"""
    question: str
    answer: str


class MultimodalResponse(BaseModel):
    """Response model for multimodal (image/PDF) questions"""
    question: str
    answer: str
    usage: dict
    file_type: str = "image"
    pages_processed: Optional[int] = None


class UsageMetrics(BaseModel):
    """Token usage metrics"""
    input: int
    output: int
    total: int
    unit: str = "TOKENS"

