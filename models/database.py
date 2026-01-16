# backend/models/database.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    lead = relationship("Lead", back_populates="conversation", uselist=False, cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), unique=True)
    
    # Contact info
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Qualification data
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    preferred_areas = Column(JSON, nullable=True)
    property_type = Column(String, nullable=True)
    purpose = Column(String, nullable=True)
    timeline = Column(String, nullable=True)
    payment_preference = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="new")
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="lead")

# Cache table for LLM responses
class ResponseCache(Base):
    __tablename__ = "response_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String, unique=True, index=True)
    context_hash = Column(String)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    hit_count = Column(Integer, default=0)