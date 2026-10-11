"""
SQLAlchemy 2.0 async database models for Supabase / PostgreSQL / SQLite.
Contains tables:
- chats
- chat_history
- responses_and_times
- file_uploads_and_generations
- each_models_history_and_tokens_usage
- documents & chunks (for Lenny transcripts RAG)
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text, Integer, Float, DateTime, ForeignKey, Index, BigInteger
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="Vetrii")
    title: Mapped[str] = mapped_column(String(255), default="New Chat")
    plan_tier: Mapped[str] = mapped_column(String(50), default="free")  # "free", "pro_10", "team_20", "enterprise_50"
    provider: Mapped[str] = mapped_column(String(50), default="ollama")
    model: Mapped[str] = mapped_column(String(100), default="qwen2.5:3b")
    storage_archive_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    messages: Mapped[List["ChatHistory"]] = relationship("ChatHistory", back_populates="chat", cascade="all, delete-orphan", order_by="ChatHistory.created_at")
    responses_and_times: Mapped[List["ResponseTime"]] = relationship("ResponseTime", back_populates="chat", cascade="all, delete-orphan")
    file_uploads: Mapped[List["FileUploadGeneration"]] = relationship("FileUploadGeneration", back_populates="chat", cascade="all, delete-orphan")
    token_usages: Mapped[List["ModelHistoryTokenUsage"]] = relationship("ModelHistoryTokenUsage", back_populates="chat", cascade="all, delete-orphan")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String(36), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user", "assistant", "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    thought: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # DeepSeek reasoning
    citations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    response_metric: Mapped[Optional["ResponseTime"]] = relationship("ResponseTime", back_populates="message", uselist=False)


class ResponseTime(Base):
    __tablename__ = "responses_and_times"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String(36), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("chat_history.id", ondelete="SET NULL"), nullable=True)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_per_second: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    time_to_first_token_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="success")  # "success", "refusal", "error"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="responses_and_times")
    message: Mapped[Optional["ChatHistory"]] = relationship("ChatHistory", back_populates="response_metric")


class FileUploadGeneration(Base):
    __tablename__ = "file_uploads_and_generations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String(36), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "pdf", "docx", "txt", "code"
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    storage_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "artifact_html", "ship30_essay", "analysis"
    generated_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="file_uploads")


class ModelHistoryTokenUsage(Base):
    __tablename__ = "each_models_history_and_tokens_usage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String(36), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    plan_type: Mapped[str] = mapped_column(String(50), default="free")
    cost_estimate_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="token_usages")


# Document & Chunk for Lenny Podcast Transcripts RAG
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    guest: Mapped[str] = mapped_column(String(255), nullable=False)
    source_path: Mapped[str] = mapped_column(String(500), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    chunks: Mapped[List["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    speaker: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")


# User model
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


# Compatibility aliases for legacy routes
Session = Chat
Message = ChatHistory
Artifact = FileUploadGeneration
