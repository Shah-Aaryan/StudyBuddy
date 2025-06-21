import base64
import numpy as np
import cv2
import librosa
from typing import Dict, Optional
from app.models.emotion_models import emotion_models
from app.models.schemas import EmotionData, EmotionResponse
import logging

logger = logging.getLogger(__name__)

class EmotionDetectionService:
    def __init__(self):
        self.emotion_weights = {
            'facial': 0.4,
            'voice': 0.35,
            'interaction': 0.25
        }
    
    async def process_emotion_data(self, data: EmotionData) -> EmotionResponse:
        """Process multimodal emotion data and return combined analysis"""
        
        facial_emotions = {}
        voice_emotions = {}
        interaction_score = 0.5
        
        # Process facial data
        if data.facial_frame:
            try:
                image_data = self._decode_image(data.facial_frame)
                facial_emotions = emotion_models.predict_facial_emotion(image_data)
            except Exception as e:
                logger.error(f"Error processing facial data: {e}")
        
        # Process voice data
        if data.audio_chunk:
            try:
                audio_data = self._decode_audio(data.audio_chunk)
                voice_emotions = emotion_models.predict_voice_emotion(audio_data)
            except Exception as e:
                logger.error(f"Error processing voice data: {e}")
        
        # Process interaction data
        if data.interaction_data:
            try:
                interaction_score = emotion_models.predict_interaction_engagement(data.interaction_data)
            except Exception as e:
                logger.error(f"Error processing interaction data: {e}")
        
        # Combine emotions
        combined_analysis = self._combine_emotions(
            facial_emotions, voice_emotions, interaction_score
        )
        
        return EmotionResponse(
            primary_emotion=combined_analysis['primary_emotion'],
            confidence=combined_analysis['confidence'],
            engagement_level=combined_analysis['engagement'],
            facial_emotions=facial_emotions,
            voice_emotions=voice_emotions,
            interaction_score=interaction_score,
            needs_intervention=combined_analysis['needs_intervention']
        )
    
    def _decode_image(self, base64_image: str) -> np.ndarray:
        """Decode base64 image to numpy array"""
        image_bytes = base64.b64decode(base64_image.split(',')[1] if ',' in base64_image else base64_image)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    
    def _decode_audio(self, base64_audio: str) -> np.ndarray:
        """Decode base64 audio to numpy array"""
        audio_bytes = base64.b64decode(base64_audio.split(',')[1] if ',' in base64_audio else base64_audio)
        # Assuming audio is in wav format
        audio_data, _ = librosa.load(audio_bytes, sr=22050)
        return audio_data
    
    def _combine_emotions(self, facial: Dict, voice: Dict, interaction: float) -> Dict:
        """Combine multimodal emotion predictions"""
        
        # Map emotions to common categories
        emotion_mapping = {
            'confused': ['confused', 'fear', 'surprise'],
            'frustrated': ['angry', 'disgust', 'fearful'],
            'bored': ['sad', 'neutral', 'calm'],
            'engaged': ['happy', 'surprise']
        }
        
        combined_scores = {
            'confused': 0.0,
            'frustrated': 0.0,
            'bored': 0.0,
            'engaged': 0.0
        }
        
        # Process facial emotions
        if facial:
            for category, emotions in emotion_mapping.items():
                score = sum(facial.get(emotion, 0) for emotion in emotions)
                combined_scores[category] += score * self.emotion_weights['facial']
        
        # Process voice emotions
        if voice:
            for category, emotions in emotion_mapping.items():
                score = sum(voice.get(emotion, 0) for emotion in emotions)
                combined_scores[category] += score * self.emotion_weights['voice']
        
        # Factor in interaction score
        if interaction < 0.3:
            combined_scores['bored'] += 0.3 * self.emotion_weights['interaction']
        elif interaction > 0.7:
            combined_scores['engaged'] += 0.3 * self.emotion_weights['interaction']
        
        # Determine primary emotion
        primary_emotion = max(combined_scores, key=combined_scores.get)
        confidence = combined_scores[primary_emotion]
        
        # Calculate overall engagement
        engagement = combined_scores['engaged'] - combined_scores['bored']
        engagement = max(0, min(1, engagement + 0.5))  # Normalize to 0-1
        
        # Determine if intervention is needed
        needs_intervention = (
            combined_scores['confused'] > 0.6 or
            combined_scores['frustrated'] > 0.5 or
            combined_scores['bored'] > 0.6
        )
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': confidence,
            'engagement': engagement,
            'needs_intervention': needs_intervention
        }

emotion_service = EmotionDetectionService()