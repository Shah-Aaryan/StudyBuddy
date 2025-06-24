from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database (loaded from .env)
    DATABASE_URL: str

    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Model paths
    FACIAL_MODEL_PATH: str = "app/ml_models/facial_emotion_model.pkl"
    VOICE_MODEL_PATH: str = "app/ml_models/voice_emotion_model.pkl"
    INTERACTION_MODEL_PATH: str = "app/ml_models/interaction_model.pkl"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Feedback Coach"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Emotion Detection Thresholds
    CONFUSION_THRESHOLD: float = 0.7
    FRUSTRATION_THRESHOLD: float = 0.6
    BOREDOM_THRESHOLD: float = 0.65

    #gemini
    gemini_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()