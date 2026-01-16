# backend/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User's message")

class ChatResponse(BaseModel):
    session_id: str
    message: str
    sources: Optional[List[str]] = None  # Sources used in RAG
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LeadInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_areas: Optional[List[str]] = None
    property_type: Optional[str] = None
    purpose: Optional[str] = None
    timeline: Optional[str] = None
    payment_preference: Optional[str] = None

class ConversationHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    lead_info: Optional[LeadInfo] = None
    created_at: datetime
    updated_at: datetime