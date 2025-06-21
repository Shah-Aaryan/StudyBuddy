from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.notification_service import notification_service

router = APIRouter()

@router.post("/send-progress")
async def send_progress_notification(user_id: int, achievement: str, db: Session = Depends(get_db)):
    try:
        await notification_service.send_progress_notification(user_id, achievement, db)
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-reminder")
async def send_reminder_notification(user_id: int, message: str, db: Session = Depends(get_db)):
    try:
        await notification_service.send_reminder_notification(user_id, message, db)
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))