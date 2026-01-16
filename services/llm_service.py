# backend/services/llm_service.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config import get_settings
from typing import List, Dict
import hashlib
from database.session import get_cache_db
from models.database import ResponseCache
from sqlalchemy.orm import Session

settings = get_settings()

class LLMService:
    def __init__(self):
        # DeepSeek is OpenAI-compatible, so we use ChatOpenAI with custom base URL
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_URL.replace("/chat/completions", ""),
            temperature=0.7,
            max_tokens=1000,
        )
    
    def _generate_cache_key(self, messages: List[Dict], context: str) -> str:
        """Generate cache key from messages and context"""
        content = str(messages) + context
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str, db: Session) -> str:
        """Get cached response if exists"""
        cached = db.query(ResponseCache).filter(
            ResponseCache.query_hash == cache_key
        ).first()
        
        if cached:
            # Increment hit count
            cached.hit_count += 1
            db.commit()
            return cached.response
        
        return None
    
    def _cache_response(self, cache_key: str, context_hash: str, response: str, db: Session):
        """Cache LLM response"""
        cache_entry = ResponseCache(
            query_hash=cache_key,
            context_hash=context_hash,
            response=response,
            hit_count=0
        )
        db.add(cache_entry)
        db.commit()
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        context: str = "",
        use_cache: bool = True
    ) -> str:
        """Generate response from DeepSeek"""
        
        # Check cache if enabled
        if use_cache:
            cache_key = self._generate_cache_key(messages, context)
            db = next(get_cache_db())
            
            cached_response = self._get_cached_response(cache_key, db)
            if cached_response:
                print("[OK] Cache hit!")
                return cached_response
        
        # Build full system prompt with context
        full_system_prompt = system_prompt
        if context:
            full_system_prompt = f"{system_prompt}\n\n# RELEVANT CONTEXT:\n{context}"
        
        # Convert to LangChain message format
        langchain_messages = [SystemMessage(content=full_system_prompt)]
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        # Generate response
        try:
            response = await self.llm.ainvoke(langchain_messages)
            response_text = response.content

            # Cache the response
            if use_cache:
                context_hash = hashlib.md5(context.encode()).hexdigest()
                self._cache_response(cache_key, context_hash, response_text, db)

            return response_text

        except Exception as e:
            print(f"[ERROR] LLM Error: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."

# Singleton instance
llm_service = LLMService()