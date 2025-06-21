from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.report_service import report_service

router = APIRouter()

@router.get("/weekly/{user_id}")
async def get_weekly_report(user_id: int, week_offset: int = 0, db: Session = Depends(get_db)):
    try:
        report = await report_service.generate_weekly_report(user_id, db, week_offset)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly/{user_id}")
async def get_monthly_report(user_id: int, month_offset: int = 0, db: Session = Depends(get_db)):
    try:
        report = await report_service.generate_monthly_report(user_id, db, month_offset)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/yearly/{user_id}")
async def get_yearly_report(user_id: int, year: int = None, db: Session = Depends(get_db)):
    try:
        report = await report_service.generate_yearly_report(user_id, db, year)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))