# backend/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    DEEPSEEK_API_KEY: str
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"

    # Database
    SQLITE_CONVERSATIONS_URL: str = "sqlite:///./data/conversations.db"
    SQLITE_CACHE_URL: str = "sqlite:///./data/cache.db"

    # Vector Store
    FAISS_INDEX_PATH: str = "./data/vector_store"

    # LangChain Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200

    # RAG Settings
    RETRIEVAL_TOP_K: int = 5

    # App Settings
    APP_NAME: str = "Kenya Real Estate Sales Agent"
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()