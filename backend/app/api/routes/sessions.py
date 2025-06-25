from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from app.models.database import get_db, LearningSession, User
from app.models.schemas import SessionStartRequest

router = APIRouter()

@router.post("/start", tags=["Sessions"])
def start_learning_session(payload: SessionStartRequest, db: Session = Depends(get_db)):
    try:
        print("➡️ Received session start request with:", payload.dict())
        user_id = payload.user_id

        # ✅ Validate user
        result = db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Create session with default course/lesson to avoid null errors
        new_session = LearningSession(
            user_id=user_id,
            start_time=datetime.utcnow(),
            completion_percentage=0.0,
            intervention_count=0,
            course_id="default",
            lesson_id="default"
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        print("✅ Session created with ID:", new_session.id)
        return {"session_id": new_session.id}

    except Exception as e:
        print("❌ Error in start_learning_session:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
