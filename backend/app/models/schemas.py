from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import datetime

class SessionStartRequest(BaseModel):
    user_id: int

class WeeklyReport(BaseModel):
    report_type: str
    period: str
    user_id: int
    summary: Dict
    emotion_analysis: Dict
    intervention_analysis: Dict
    progress_metrics: Dict
    learning_patterns: Dict
    achievements: List[Dict]
    recommendations: List[str]

class MonthlyReport(BaseModel):
    report_type: str
    period: str
    user_id: int
    summary: Dict
    weekly_breakdown: Dict
    emotion_trends: Dict
    learning_trends: Dict
    goal_progress: Dict
    achievements: List[Dict]
    insights: List[str]

class YearlyReport(BaseModel):
    report_type: str
    period: str
    user_id: int
    summary: Dict
    monthly_breakdown: Dict
    learning_milestones: List[Dict]
    emotion_journey: Dict
    achievements: List[Dict]
    year_over_year: Dict
    insights: List[str]

class InteractionData(BaseModel):
    session_id: int
    movements: int
    clicks: int
    scrolling: int

class EmotionData(BaseModel):
    facial_frame: Optional[str] = None
    audio_chunk: Optional[str] = None
    interaction_data: Optional[InteractionData] = None
    timestamp: str


class EmotionResponse(BaseModel):
    primary_emotion: str
    confidence: float
    engagement_level: float
    facial_emotions: Dict[str, float]
    voice_emotions: Dict[str, float]
    interaction_score: float
    needs_intervention: bool

class InterventionRequest(BaseModel):
    emotion: str
    confidence: float
    context: Dict

class InterventionResponse(BaseModel):
    type: str  # video, game, break, chatbot
    resource: Dict
    message: str
    priority: int

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class SessionCreate(BaseModel):
    course_id: str
    lesson_id: str

class SessionResponse(BaseModel):
    id: int
    course_id: str
    lesson_id: str
    start_time: datetime
    duration_minutes: Optional[float]
    completion_percentage: float
    average_engagement: Optional[float]
    intervention_count: int

class AnalyticsResponse(BaseModel):
    total_sessions: int
    average_engagement: float
    emotion_distribution: Dict[str, float]
    intervention_effectiveness: Dict[str, float]
    learning_patterns: Dict