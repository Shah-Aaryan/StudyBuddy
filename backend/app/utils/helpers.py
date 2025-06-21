import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Union
import base64
import numpy as np

def generate_session_id() -> str:
    """Generate unique session ID"""
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """Hash password for storage"""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def calculate_engagement_score(
    mouse_movements: int,
    clicks: int,
    scroll_events: int,
    idle_time: float,
    active_time: float
) -> float:
    """Calculate engagement score from interaction data"""
    if active_time == 0:
        return 0.0
    
    # Normalize metrics
    movement_score = min(mouse_movements / 100, 1.0)  # Cap at 100 movements
    click_score = min(clicks / 20, 1.0)  # Cap at 20 clicks
    scroll_score = min(scroll_events / 10, 1.0)  # Cap at 10 scrolls
    
    # Time-based score
    time_ratio = active_time / (active_time + idle_time)
    
    # Weighted combination
    engagement = (
        movement_score * 0.3 +
        click_score * 0.2 +
        scroll_score * 0.2 +
        time_ratio * 0.3
    )
    
    return round(engagement, 3)

def encode_audio_features(audio_data: np.ndarray) -> str:
    """Encode audio features for storage"""
    return base64.b64encode(audio_data.tobytes()).decode()

def decode_audio_features(encoded_data: str) -> np.ndarray:
    """Decode audio features from storage"""
    bytes_data = base64.b64decode(encoded_data)
    return np.frombuffer(bytes_data, dtype=np.float32)

def calculate_intervention_priority(emotion: str, confidence: float) -> int:
    """Calculate intervention priority (0-3, 3 being highest)"""
    priority_map = {
        'frustrated': 3,
        'confused': 2,
        'bored': 1,
        'engaged': 0
    }
    
    base_priority = priority_map.get(emotion, 1)
    
    # Adjust based on confidence
    if confidence > 0.8:
        return min(3, base_priority + 1)
    elif confidence < 0.5:
        return max(0, base_priority - 1)
    
    return base_priority