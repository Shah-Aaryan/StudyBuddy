import pickle
import joblib
import numpy as np
import cv2
import librosa
import os
import numbers
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

STATE_MAP = {"active": 2.0, "idle": 1.0, "about_to_leave": 0.0}
print("🟢 Using STATE_MAP:", STATE_MAP)
ENGAGEMENT_SCORE_MAP = {
    "engaged": 0.9,
    "confused": 0.6,
    "frustrated": 0.3,
    "about_to_leave": 0.1,   # ← tweak scores any way you like
}

class EmotionModelManager:
    def __init__(self):
        self.facial_model = None
        self.voice_model = None
        self.interaction_model = None
        self.interaction_scaler = None
        self.feature_names = []
        self.load_models()
    
    def load_models(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))  # go up from app/models to app/
            model_dir = os.path.join(base_dir, 'ml_models')         

            with open(os.path.join(model_dir, 'facial_emotion_model.pkl'), 'rb') as f:
                self.facial_model = pickle.load(f)
            with open(os.path.join(model_dir, 'voice_emotion_model.pkl'), 'rb') as f:
                self.voice_model = pickle.load(f)
            with open(os.path.join(model_dir, 'clean_user_behavior_model.pkl'), 'rb') as f:
                model_dict = joblib.load(f)
                self.interaction_model = model_dict['model']
                self.interaction_scaler = model_dict['scaler']
                self.feature_names = model_dict['feature_names']

            logger.info("✅ All emotion models loaded successfully")

        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            raise

    def preprocess_facial_data(self, image_data: np.ndarray) -> np.ndarray:
        if len(image_data.shape) == 3:
            gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_data
        resized = cv2.resize(gray, (48, 48))
        normalized = resized / 255.0
        if np.mean(gray) < 1:
            logger.warning("⚠️ Frame is very dark or blank")
        return normalized.reshape(1, -1)

    def preprocess_audio_data(self, audio_data: np.ndarray, sr: int = 22050) -> np.ndarray:
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)

        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
        spectral_centroids_mean = np.mean(spectral_centroids)

        zcr = librosa.feature.zero_crossing_rate(audio_data)
        zcr_mean = np.mean(zcr)

        features = np.concatenate([mfccs_mean, [spectral_centroids_mean, zcr_mean]])
        return features.reshape(1, -1)

    def preprocess_interaction_data(self, interaction_data: Dict[str, Any]) -> np.ndarray:
        if hasattr(interaction_data, "dict"):
            interaction_data = interaction_data.dict()
        elif hasattr(interaction_data, "model_dump"):
            interaction_data = interaction_data.model_dump()

        if isinstance(interaction_data, dict) and "interaction_data" in interaction_data:
            interaction_data = interaction_data["interaction_data"]

        numeric_only: Dict[str, float] = {}
        for k, v in interaction_data.items():
            if isinstance(v, numbers.Number) and not isinstance(v, bool):
                numeric_only[k] = float(v)
            elif isinstance(v, (str, np.str_)) and v in STATE_MAP:
                numeric_only[k] = STATE_MAP[v]

        feature_vector = [numeric_only.get(name, 0.0) for name in self.feature_names]
        logger.debug(f"🧠 Interaction features after cleaning: {feature_vector}")
        print("🧪 preprocess_interaction_data invoked with keys:", list(interaction_data.keys()))
        return np.array(feature_vector, dtype=np.float32).reshape(1, -1)


    def predict_facial_emotion(self, image_data: np.ndarray) -> Dict[str, float]:
        try:
            if not self.facial_model:
                raise ValueError("Facial model not loaded")
            processed = self.preprocess_facial_data(image_data)
            prediction = self.facial_model.predict_proba(processed)[0]
            labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral', 'confused']
            return dict(zip(labels, prediction))
            logger.debug("📸 Facial model output: %s", prediction)
        except Exception as e:
            logger.error(f"Error in facial emotion prediction: {e}")
            return {}

    def predict_voice_emotion(self, audio_data: np.ndarray) -> Dict[str, float]:
        try:
            if not self.voice_model:
                raise ValueError("Voice model not loaded")
            processed = self.preprocess_audio_data(audio_data)
            prediction = self.voice_model.predict_proba(processed)[0]
            labels = ['calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised']
            return dict(zip(labels, prediction))
            logger.debug("🎙️ Voice model output: %s", prediction)
        except Exception as e:
            logger.error(f"Error in voice emotion prediction: {e}")
            return {}

    def predict_interaction_engagement(self, interaction_data: Any) -> float:
        try:
            if not self.interaction_model:
                raise ValueError("Interaction model not loaded")

            # ---- unwrap Pydantic/dataclass payloads --------------------------------
            if hasattr(interaction_data, "model_dump"):
                payload = interaction_data.model_dump()
            elif hasattr(interaction_data, "dict"):
                payload = interaction_data.dict()
            else:
                payload = dict(interaction_data) if not isinstance(interaction_data, dict) else interaction_data

            # ---- feature engineering -----------------------------------------------
            features = self.preprocess_interaction_data(payload)

            # ---- decide whether we need external scaling ---------------------------
            if self.interaction_scaler is not None:
                # Separate scaler was saved in the pkl bundle
                features_used = self.interaction_scaler.transform(features)
            else:
                # Model is probably a Pipeline (scaler embedded) – use raw features
                features_used = features

            # ---- predict and map to score ------------------------------------------
            label = self.interaction_model.predict(features_used)[0]   # -> 'confused'
            score = ENGAGEMENT_SCORE_MAP.get(str(label), 0.5)          # default neutral

            logger.debug(f"📊 Engagement label={label} -> score={score}")
            return score
            logger.debug("🖱️ Engagement label = %s → score = %s", label, score)
        except Exception as e:
            logger.error(f"Error in interaction prediction: {e}")
            return 0.5

# Global instance
emotion_models = EmotionModelManager()
