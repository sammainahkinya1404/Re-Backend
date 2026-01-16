# backend/api/leads.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.schemas import LeadInfo
from database.session import get_conversation_db
from services.conversation_service import conversation_service
from services.lead_service import lead_service
from typing import List, Optional

router = APIRouter(prefix="/leads", tags=["leads"])

@router.post("/{session_id}")
async def update_lead(
    session_id: str,
    lead_data: LeadInfo,
    db: Session = Depends(get_conversation_db)
):
    """
    Update lead information for a conversation
    """
    
    try:
        lead = conversation_service.update_lead_info(
            session_id=session_id,
            lead_data=lead_data,
            db=db
        )
        
        return {
            "message": "Lead information updated",
            "lead_id": lead.id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=Optional[LeadInfo])
async def get_lead(
    session_id: str,
    db: Session = Depends(get_conversation_db)
):
    """
    Get lead information for a conversation
    """
    
    lead_info = conversation_service.get_lead_info(session_id, db)
    
    return lead_info

@router.get("/")
async def list_leads(
    status: Optional[str] = None,
    db: Session = Depends(get_conversation_db)
):
    """
    List all leads, optionally filtered by status
    """
    
    leads = lead_service.get_all_leads(db, status=status)
    
    return {
        "count": len(leads),
        "leads": [
            {
                "id": lead.id,
                "name": lead.name,
                "phone": lead.phone,
                "email": lead.email,
                "budget_range": f"KES {lead.budget_min}-{lead.budget_max}" if lead.budget_min else None,
                "preferred_areas": lead.preferred_areas,
                "status": lead.status,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at
            }
            for lead in leads
        ]
    }

@router.patch("/{lead_id}/status")
async def update_lead_status(
    lead_id: int,
    status: str,
    db: Session = Depends(get_conversation_db)
):
    """
    Update lead status (new, qualified, viewing, negotiating, closed)
    """
    
    lead = lead_service.update_lead_status(lead_id, status, db)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "message": "Lead status updated",
        "lead_id": lead.id,
        "new_status": lead.status
    }