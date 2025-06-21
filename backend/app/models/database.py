from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from app.config.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    sessions = relationship("LearningSession", back_populates="user")
    emotions = relationship("EmotionLog", back_populates="user")

class LearningSession(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(String)
    lesson_id = Column(String)
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime)
    duration_minutes = Column(Float)
    completion_percentage = Column(Float, default=0.0)
    average_engagement = Column(Float)
    intervention_count = Column(Integer, default=0)
    
    user = relationship("User", back_populates="sessions")
    emotions = relationship("EmotionLog", back_populates="session")
    interventions = relationship("Intervention", back_populates="session")

class EmotionLog(Base):
    __tablename__ = "emotion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("learning_sessions.id"))
    timestamp = Column(DateTime, server_default=func.now())
    
    # Emotion scores
    facial_emotions = Column(JSON)  # {happy: 0.2, sad: 0.1, confused: 0.7, ...}
    voice_emotions = Column(JSON)
    interaction_score = Column(Float)
    
    # Combined analysis
    primary_emotion = Column(String)
    confidence_score = Column(Float)
    engagement_level = Column(Float)
    
    user = relationship("User", back_populates="emotions")
    session = relationship("LearningSession", back_populates="emotions")

class Intervention(Base):
    __tablename__ = "interventions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"))
    timestamp = Column(DateTime, server_default=func.now())
    trigger_emotion = Column(String)
    intervention_type = Column(String)  # video, game, break, chatbot
    resource_id = Column(String)
    user_response = Column(String)  # accepted, dismissed, completed
    effectiveness_score = Column(Float)
    
    session = relationship("LearningSession", back_populates="interventions")
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    type = Column(String, default="general")  # e.g., progress, reminder, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Optional: relationship to User
    user = relationship("User", backref="notifications")
class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="notification_preferences")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()