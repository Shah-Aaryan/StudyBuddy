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
        """Extract audio features for emotion detection (match training script)"""
        import librosa
        import numpy as np
        # MFCC
        mfccs = np.mean(librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=40), axis=1)
        # Chroma
        chroma = np.mean(librosa.feature.chroma_stft(y=audio_data, sr=sr), axis=1)
        # Mel Spectrogram
        mel = np.mean(librosa.feature.melspectrogram(y=audio_data, sr=sr), axis=1)
        # Spectral Contrast
        contrast = np.mean(librosa.feature.spectral_contrast(y=audio_data, sr=sr), axis=1)
        # Tonnetz
        tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(audio_data), sr=sr), axis=1)
        # Zero Crossing Rate
        zcr = [np.mean(librosa.feature.zero_crossing_rate(y=audio_data))]
        # RMS
        rms = [np.mean(librosa.feature.rms(y=audio_data))]
        # Tempo
        tempo = [librosa.beat.tempo(y=audio_data, sr=sr)[0]]
        # YIN (fundamental frequency)
        try:
            yin = [np.mean(librosa.yin(audio_data, fmin=50, fmax=300, sr=sr))]
        except Exception:
            yin = [0.0]
        features = np.hstack([
            mfccs, chroma, mel, contrast, tonnetz, zcr, rms, tempo, yin
        ])
        return features.reshape(1, -1)
    
    def preprocess_interaction_data(self, interaction_data: Dict) -> np.ndarray:
        """Preprocess interaction data to match training script features"""
        # Extract features as per training script
        idle_time = interaction_data.get('idle_time_seconds', 0)
        tab_switches_per_minute = interaction_data.get('tab_switches_per_minute', 0)
        mouse_movement_variance = interaction_data.get('mouse_movement_variance', 0)
        video_scrub_count = interaction_data.get('video_scrub_count', 0)
        video_replay_count = interaction_data.get('video_replay_count', 0)
        session_duration_minutes = interaction_data.get('session_duration_minutes', 0)
        click_frequency = interaction_data.get('click_frequency', 0)
        scroll_speed_variance = interaction_data.get('scroll_speed_variance', 0)
        page_dwell_time = interaction_data.get('page_dwell_time', 0)
        error_encounters = interaction_data.get('error_encounters', 0)
        features = [
            idle_time,
            tab_switches_per_minute,
            mouse_movement_variance,
            video_scrub_count,
            video_replay_count,
            session_duration_minutes,
            click_frequency,
            scroll_speed_variance,
            page_dwell_time,
            error_encounters
        ]
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