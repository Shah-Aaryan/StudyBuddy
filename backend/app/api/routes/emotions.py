from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import logging

from app.models.database import get_db, EmotionLog, LearningSession
from app.models.schemas import EmotionData, EmotionResponse
from app.services.emotion_detection import emotion_service
from app.services.feedback_engine import feedback_engine
from app.models.schemas import InterventionRequest

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Receive emotion data
            data = await websocket.receive_text()
            emotion_data = EmotionData.parse_raw(data)
            
            # Process emotion data
            emotion_response = await emotion_service.process_emotion_data(emotion_data)
            
            # Store in database
            emotion_log = EmotionLog(
                user_id=user_id,
                session_id=emotion_data.interaction_data.get('session_id'),
                facial_emotions=emotion_response.facial_emotions,
                voice_emotions=emotion_response.voice_emotions,
                interaction_score=emotion_response.interaction_score,
                primary_emotion=emotion_response.primary_emotion,
                confidence_score=emotion_response.confidence,
                engagement_level=emotion_response.engagement_level
            )
            db.add(emotion_log)
            db.commit()
            
            # Send response back
            await websocket.send_text(emotion_response.json())
            
            # Check if intervention is needed
            if emotion_response.needs_intervention:
                intervention_request = InterventionRequest(
                    emotion=emotion_response.primary_emotion,
                    confidence=emotion_response.confidence,
                    context=emotion_data.interaction_data
                )
                
                intervention = await feedback_engine.generate_intervention(
                    intervention_request, user_id
                )
                
                # Send intervention
                await websocket.send_text(json.dumps({
                    "type": "intervention",
                    "data": intervention.dict()
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        await websocket.close()

@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotion(
    emotion_data: EmotionData,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Analyze emotion data via REST API"""
    try:
        emotion_response = await emotion_service.process_emotion_data(emotion_data)
        
        # Store in database
        emotion_log = EmotionLog(
            user_id=user_id,
            session_id=emotion_data.interaction_data.get('session_id'),
            facial_emotions=emotion_response.facial_emotions,
            voice_emotions=emotion_response.voice_emotions,
            interaction_score=emotion_response.interaction_score,
            primary_emotion=emotion_response.primary_emotion,
            confidence_score=emotion_response.confidence,
            engagement_level=emotion_response.engagement_level
        )
        db.add(emotion_log)
        db.commit()
        
        return emotion_response
    except Exception as e:
        logger.error(f"Error analyzing emotion: {e}")
        raise HTTPException(status_code=500, detail="Error processing emotion data")