from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, Intervention
from app.models.schemas import InterventionRequest, InterventionResponse
from app.services.feedback_engine import feedback_engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/intervention", response_model=InterventionResponse)
async def request_intervention(
    request: InterventionRequest,
    user_id: int,
    session_id: int,
    db: Session = Depends(get_db)
):
    """Request intervention based on detected emotion"""
    try:
        intervention = await feedback_engine.generate_intervention(request, user_id)
        
        # Store intervention in database
        intervention_record = Intervention(
            session_id=session_id,
            trigger_emotion=request.emotion,
            intervention_type=intervention.type,
            resource_id=intervention.resource.get('id', ''),
            user_response='pending'
        )
        db.add(intervention_record)
        db.commit()
        
        return intervention
    except Exception as e:
        logger.error(f"Error generating intervention: {e}")
        raise HTTPException(status_code=500, detail="Error generating intervention")

@router.post("/intervention/{intervention_id}/response")
async def record_intervention_response(
    intervention_id: int,
    response: str,  # accepted, dismissed, completed
    effectiveness: float = None,
    db: Session = Depends(get_db)
):
    """Record user response to intervention"""
    try:
        intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention not found")
        
        intervention.user_response = response
        if effectiveness is not None:
            intervention.effectiveness_score = effectiveness
        
        db.commit()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error recording intervention response: {e}")
        raise HTTPException(status_code=500, detail="Error recording response")

@router.get("/intervention/history/{user_id}")
async def get_intervention_history(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get intervention history for a user"""
    try:
        interventions = db.query(Intervention).join(
            Intervention.session
        ).filter(
            Intervention.session.has(user_id=user_id)
        ).order_by(Intervention.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "id": i.id,
                "timestamp": i.timestamp,
                "trigger_emotion": i.trigger_emotion,
                "intervention_type": i.intervention_type,
                "user_response": i.user_response,
                "effectiveness_score": i.effectiveness_score
            }
            for i in interventions
        ]
    except Exception as e:
        logger.error(f"Error getting intervention history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving history")