# backend/database/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import get_settings
from models.database import Base
import os

settings = get_settings()

# Ensure data directory exists
os.makedirs("./data", exist_ok=True)

# Conversations database
conv_engine = create_engine(
    settings.SQLITE_CONVERSATIONS_URL,
    connect_args={"check_same_thread": False}
)
ConversationSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=conv_engine)

# Cache database
cache_engine = create_engine(
    settings.SQLITE_CACHE_URL,
    connect_args={"check_same_thread": False}
)
CacheSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cache_engine)

def init_databases():
    """Initialize all databases"""
    Base.metadata.create_all(bind=conv_engine)
    Base.metadata.create_all(bind=cache_engine)
    print("[OK] Databases initialized")

def get_conversation_db():
    """Dependency for conversation DB"""
    db = ConversationSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_cache_db():
    """Dependency for cache DB"""
    db = CacheSessionLocal()
    try:
        yield db
    finally:
        db.close()