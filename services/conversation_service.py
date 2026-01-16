# backend/services/conversation_service.py
from sqlalchemy.orm import Session
from models.database import Conversation, Message, Lead
from models.schemas import ChatMessage, LeadInfo
from typing import List, Optional
from datetime import datetime
import uuid

class ConversationService:
    
    @staticmethod
    def get_or_create_conversation(session_id: str, db: Session) -> Conversation:
        """Get existing conversation or create new one"""
        
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            conversation = Conversation(session_id=session_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        return conversation
    
    @staticmethod
    def add_message(
        session_id: str,
        role: str,
        content: str,
        db: Session
    ) -> Message:
        """Add message to conversation"""
        
        conversation = ConversationService.get_or_create_conversation(session_id, db)
        
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content
        )
        
        db.add(message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        
        return message
    
    @staticmethod
    def get_conversation_history(
        session_id: str,
        db: Session,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Get conversation message history"""
        
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            return []
        
        query = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp)
        
        if limit:
            query = query.limit(limit)
        
        messages = query.all()
        
        return [
            ChatMessage(role=msg.role, content=msg.content)
            for msg in messages
        ]
    
    @staticmethod
    def get_recent_messages(
        session_id: str,
        db: Session,
        n: int = 10
    ) -> List[dict]:
        """Get last N messages for context"""
        
        messages = ConversationService.get_conversation_history(session_id, db)
        
        # Return last N messages
        recent = messages[-n:] if len(messages) > n else messages
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent
        ]
    
    @staticmethod
    def update_lead_info(
        session_id: str,
        lead_data: LeadInfo,
        db: Session
    ) -> Lead:
        """Update or create lead information"""
        
        conversation = ConversationService.get_or_create_conversation(session_id, db)
        
        lead = db.query(Lead).filter(
            Lead.conversation_id == conversation.id
        ).first()
        
        if not lead:
            lead = Lead(conversation_id=conversation.id)
            db.add(lead)
        
        # Update fields
        for field, value in lead_data.model_dump(exclude_none=True).items():
            setattr(lead, field, value)
        
        lead.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(lead)
        
        return lead
    
    @staticmethod
    def get_lead_info(session_id: str, db: Session) -> Optional[LeadInfo]:
        """Get lead information for a conversation"""
        
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation or not conversation.lead:
            return None
        
        lead = conversation.lead
        
        return LeadInfo(
            name=lead.name,
            phone=lead.phone,
            email=lead.email,
            budget_min=lead.budget_min,
            budget_max=lead.budget_max,
            preferred_areas=lead.preferred_areas,
            property_type=lead.property_type,
            purpose=lead.purpose,
            timeline=lead.timeline,
            payment_preference=lead.payment_preference
        )
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())

# Singleton instance
conversation_service = ConversationService()