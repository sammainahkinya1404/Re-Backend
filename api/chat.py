# backend/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.schemas import ChatRequest, ChatResponse
from database.session import get_conversation_db
from services.conversation_service import conversation_service
from services.rag_service import rag_service
from services.llm_service import llm_service
from prompts.system_prompt import get_system_prompt
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_conversation_db)
):
    """
    Send a message and get AI response
    """
    
    try:
        # Save user message
        conversation_service.add_message(
            session_id=request.session_id,
            role="user",
            content=request.message,
            db=db
        )
        
        # Get conversation history (last 10 messages for context)
        history = conversation_service.get_recent_messages(
            session_id=request.session_id,
            db=db,
            n=10
        )
        
        # Retrieve relevant context from knowledge base
        rag_result = rag_service.retrieve_context(request.message)
        context = rag_result["context"]
        sources = rag_result["sources"]
        
        # Get system prompt
        system_prompt = get_system_prompt()
        
        # Generate response
        response_text = await llm_service.generate_response(
            messages=history,
            system_prompt=system_prompt,
            context=context,
            use_cache=True
        )
        
        # Save assistant response
        conversation_service.add_message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            db=db
        )
        
        return ChatResponse(
            session_id=request.session_id,
            message=response_text,
            sources=sources,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        print(f"[ERROR] Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    db: Session = Depends(get_conversation_db)
):
    """
    Get conversation history
    """
    
    history = conversation_service.get_conversation_history(
        session_id=session_id,
        db=db
    )
    
    return {
        "session_id": session_id,
        "messages": history,
        "count": len(history)
    }

@router.post("/new-session")
async def create_new_session():
    """
    Create a new chat session
    """
    
    session_id = conversation_service.generate_session_id()
    
    return {
        "session_id": session_id,
        "message": "New session created"
    }