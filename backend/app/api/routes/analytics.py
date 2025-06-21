from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional

from app.models.database import get_db, EmotionLog, LearningSession, Intervention
from app.models.schemas import AnalyticsResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard/{user_id}", response_model=AnalyticsResponse)
async def get_user_analytics(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a user"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get basic session stats
        sessions = db.query(LearningSession).filter(
            and_(
                LearningSession.user_id == user_id,
                LearningSession.start_time >= start_date
            )
        ).all()
        
        total_sessions = len(sessions)
        average_engagement = sum(s.average_engagement or 0 for s in sessions) / max(total_sessions, 1)
        
        # Get emotion distribution
        emotions = db.query(
            EmotionLog.primary_emotion,
            func.count(EmotionLog.id).label('count')
        ).filter(
            and_(
                EmotionLog.user_id == user_id,
                EmotionLog.timestamp >= start_date
            )
        ).group_by(EmotionLog.primary_emotion).all()
        
        total_emotions = sum(e.count for e in emotions)
        emotion_distribution = {
            e.primary_emotion: e.count / max(total_emotions, 1)
            for e in emotions
        }
        
        # Get intervention effectiveness
        interventions = db.query(
            Intervention.intervention_type,
            func.avg(Intervention.effectiveness_score).label('avg_effectiveness')
        ).join(Intervention.session).filter(
            and_(
                Intervention.session.has(user_id=user_id),
                Intervention.timestamp >= start_date,
                Intervention.effectiveness_score.isnot(None)
            )
        ).group_by(Intervention.intervention_type).all()
        
        intervention_effectiveness = {
            i.intervention_type: float(i.avg_effectiveness or 0)
            for i in interventions
        }
        
        # Learning patterns analysis
        learning_patterns = await _analyze_learning_patterns(user_id, sessions, db)
        
        return AnalyticsResponse(
            total_sessions=total_sessions,
            average_engagement=average_engagement,
            emotion_distribution=emotion_distribution,
            intervention_effectiveness=intervention_effectiveness,
            learning_patterns=learning_patterns
        )
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")

async def _analyze_learning_patterns(user_id: int, sessions: list, db: Session) -> dict:
    """Analyze learning patterns for insights"""
    if not sessions:
        return {}
    
    # Time-based patterns
    session_times = [s.start_time.hour for s in sessions]
    peak_hour = max(set(session_times), key=session_times.count) if session_times else 0
    
    # Session duration patterns
    durations = [s.duration_minutes for s in sessions if s.duration_minutes]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Completion patterns
    completion_rates = [s.completion_percentage for s in sessions if s.completion_percentage]
    avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
    
    # Engagement trends (last 7 days vs previous 7 days)
    recent_sessions = [s for s in sessions if s.start_time >= datetime.utcnow() - timedelta(days=7)]
    older_sessions = [s for s in sessions if s.start_time < datetime.utcnow() - timedelta(days=7)]
    
    recent_engagement = sum(s.average_engagement or 0 for s in recent_sessions) / max(len(recent_sessions), 1)
    older_engagement = sum(s.average_engagement or 0 for s in older_sessions) / max(len(older_sessions), 1)
    
    engagement_trend = "improving" if recent_engagement > older_engagement else "declining"
    
    return {
        "peak_learning_hour": peak_hour,
        "average_session_duration": round(avg_duration, 2),
        "average_completion_rate": round(avg_completion, 2),
        "engagement_trend": engagement_trend,
        "total_learning_time": sum(durations),
        "consistency_score": len(set(s.start_time.date() for s in sessions)) / 30.0  # days active in last 30 days
    }

@router.get("/emotions/timeline/{user_id}")
async def get_emotion_timeline(
    user_id: int,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get emotion timeline for visualization"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        emotions = db.query(EmotionLog).filter(
            and_(
                EmotionLog.user_id == user_id,
                EmotionLog.timestamp >= start_time
            )
        ).order_by(EmotionLog.timestamp).all()
        
        timeline = [
            {
                "timestamp": e.timestamp.isoformat(),
                "emotion": e.primary_emotion,
                "confidence": e.confidence_score,
                "engagement": e.engagement_level
            }
            for e in emotions
        ]
        
        return {"timeline": timeline}
    except Exception as e:
        logger.error(f"Error getting emotion timeline: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving timeline")