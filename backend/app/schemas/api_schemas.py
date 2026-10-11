"""
Pydantic API request and response contracts.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# Citations
class Citation(BaseModel):
    guest: str
    episode_title: str
    timestamp: str  # e.g., "00:14:22"
    quote_snippet: Optional[str] = None
    youtube_url: Optional[str] = None


# Messages
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    user_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    route: Optional[str] = None
    latency_ms: Optional[int] = None
    created_at: datetime


# Artifacts
class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    message_id: Optional[str] = None
    type: Literal["markdown", "html"]
    title: str
    content: str
    created_at: datetime


# Sessions
class SessionCreate(BaseModel):
    title: Optional[str] = "New Chat"
    user_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class SessionDetailResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []


class SessionSummary(BaseModel):
    id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: int


# System Config
class ConfigResponse(BaseModel):
    active_provider: str
    active_model: str
    embedding_model: str
    available_providers: List[str]
    local_ollama_available: bool
    cloud_anthropic_available: bool
    cloud_openai_available: bool
