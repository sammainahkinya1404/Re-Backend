# backend/services/lead_service.py
from sqlalchemy.orm import Session
from models.database import Lead
from typing import List, Dict, Optional

class LeadService:
    
    @staticmethod
    def extract_lead_info_from_conversation(messages: List[Dict]) -> Dict:
        """
        Extract lead qualification data from conversation messages
        This is a simple version - you could enhance with NLP/LLM extraction
        """
        
        lead_info = {}
        conversation_text = " ".join([msg["content"].lower() for msg in messages if msg["role"] == "user"])
        
        # Budget extraction (simple keyword matching)
        budget_keywords = ["budget", "afford", "price range", "ksh", "kes"]
        if any(kw in conversation_text for kw in budget_keywords):
            # You could use regex or LLM to extract actual numbers
            lead_info["budget_mentioned"] = True
        
        # Area preferences
        areas = ["kitengela", "ruiru", "syokimau", "juja", "ngong", "athi river"]
        mentioned_areas = [area for area in areas if area in conversation_text]
        if mentioned_areas:
            lead_info["preferred_areas"] = mentioned_areas
        
        # Property type
        if "land" in conversation_text or "plot" in conversation_text:
            lead_info["property_type"] = "land"
        elif "apartment" in conversation_text or "flat" in conversation_text:
            lead_info["property_type"] = "apartment"
        elif "house" in conversation_text or "townhouse" in conversation_text:
            lead_info["property_type"] = "house"
        
        # Investment purpose
        if "invest" in conversation_text or "rental" in conversation_text or "rent out" in conversation_text:
            lead_info["purpose"] = "investment"
        elif "live" in conversation_text or "own stay" in conversation_text or "family" in conversation_text:
            lead_info["purpose"] = "residence"
        
        return lead_info
    
    @staticmethod
    def get_all_leads(db: Session, status: Optional[str] = None) -> List[Lead]:
        """Get all leads, optionally filtered by status"""
        
        query = db.query(Lead)
        
        if status:
            query = query.filter(Lead.status == status)
        
        return query.order_by(Lead.updated_at.desc()).all()
    
    @staticmethod
    def update_lead_status(lead_id: int, status: str, db: Session) -> Lead:
        """Update lead status"""
        
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if lead:
            lead.status = status
            db.commit()
            db.refresh(lead)
        
        return lead

# Singleton instance
lead_service = LeadService()