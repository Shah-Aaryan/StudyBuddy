import pickle
import numpy as np
import cv2
import librosa
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class EmotionModelManager:
    def __init__(self):
        self.facial_model = None
        self.voice_model = None
        self.interaction_model = None
        self.load_models()
    
    def load_models(self):
        try:
            # Load facial emotion model
            with open('app/ml_models/facial_emotion_model.pkl', 'rb') as f:
                self.facial_model = pickle.load(f)
            
            # Load voice emotion model
            with open('app/ml_models/voice_emotion_model.pkl', 'rb') as f:
                self.voice_model = pickle.load(f)
            
            # Load interaction model
            with open('app/ml_models/interaction_model.pkl', 'rb') as f:
                self.interaction_model = pickle.load(f)
            
            logger.info("All emotion models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def preprocess_facial_data(self, image_data: np.ndarray) -> np.ndarray:
        """Preprocess facial image for emotion detection"""
        # Resize to expected input size (assuming 48x48 grayscale)
        if len(image_data.shape) == 3:
            gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_data
        
        resized = cv2.resize(gray, (48, 48))
        normalized = resized / 255.0
        return normalized.reshape(1, -1)
    
    def preprocess_audio_data(self, audio_data: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Extract audio features for emotion detection"""
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)
        
        # Extract spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
        spectral_centroids_mean = np.mean(spectral_centroids)
        
        # Extract zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)
        zcr_mean = np.mean(zcr)
        
        # Combine features
        features = np.concatenate([mfccs_mean, [spectral_centroids_mean, zcr_mean]])
        return features.reshape(1, -1)
    
    def preprocess_interaction_data(self, interaction_data: Dict) -> np.ndarray:
        """Preprocess interaction data for model input"""
        features = []
        
        # Mouse movement features
        mouse_movements = interaction_data.get('mouse_movements', [])
        if mouse_movements:
            speeds = [m.get('speed', 0) for m in mouse_movements]
            features.extend([
                np.mean(speeds),
                np.std(speeds),
                len(mouse_movements)
            ])
        else:
            features.extend([0, 0, 0])
        
        # Click patterns
        clicks = interaction_data.get('clicks', [])
        features.append(len(clicks))
        
        # Scroll behavior
        scrolls = interaction_data.get('scrolls', [])
        features.append(len(scrolls))
        
        # Time-based features
        features.extend([
            interaction_data.get('idle_time', 0),
            interaction_data.get('active_time', 0),
            interaction_data.get('tab_switches', 0)
        ])
        
        return np.array(features).reshape(1, -1)
    
    def predict_facial_emotion(self, image_data: np.ndarray) -> Dict[str, float]:
        """Predict emotion from facial image"""
        try:
            processed_data = self.preprocess_facial_data(image_data)
            prediction = self.facial_model.predict_proba(processed_data)[0]
            
            emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral', 'confused']
            return dict(zip(emotion_labels, prediction))
        except Exception as e:
            logger.error(f"Error in facial emotion prediction: {e}")
            return {}
    
    def predict_voice_emotion(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Predict emotion from voice audio"""
        try:
            processed_data = self.preprocess_audio_data(audio_data)
            prediction = self.voice_model.predict_proba(processed_data)[0]
            
            emotion_labels = ['calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised']
            return dict(zip(emotion_labels, prediction))
        except Exception as e:
            logger.error(f"Error in voice emotion prediction: {e}")
            return {}
    
    def predict_interaction_engagement(self, interaction_data: Dict) -> float:
        """Predict engagement level from interaction data"""
        try:
            processed_data = self.preprocess_interaction_data(interaction_data)
            engagement_score = self.interaction_model.predict(processed_data)[0]
            return float(engagement_score)
        except Exception as e:
            logger.error(f"Error in interaction prediction: {e}")
            return 0.5  # neutral engagement

# Global instance
emotion_models = EmotionModelManager()