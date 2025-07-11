import base64, io, json, logging
from typing import Dict
import cv2, librosa, numpy as np, soundfile as sf

from app.models.emotion_models import emotion_models
from app.models.schemas import EmotionData, EmotionResponse

logger = logging.getLogger(__name__)


class EmotionDetectionService:
    def __init__(self):
        self.emotion_weights = {"facial": 0.4, "voice": 0.35, "interaction": 0.25}

    async def process_emotion_data(self, data: EmotionData) -> EmotionResponse:
        facial_emotions: Dict[str, float] = {}
        voice_emotions: Dict[str, float] = {}
        interaction_score: float = 0.5

        if data.facial_frame:
            try:
                image = self._decode_image(data.facial_frame)
                facial_emotions = emotion_models.predict_facial_emotion(image)
            except Exception as e:
                logger.error("facial error %s", e)

        if data.audio_chunk:
            try:
                audio = self._decode_audio(data.audio_chunk)
                voice_emotions = emotion_models.predict_voice_emotion(audio)
            except Exception as e:
                logger.error("audio error %s", e)

        if data.interaction_data:
            try:
                interaction_score = emotion_models.predict_interaction_engagement(
                    data.interaction_data
                )
            except Exception as e:
                logger.error("interaction error %s", e)

        combined = self._combine_emotions(
            facial_emotions, voice_emotions, interaction_score
        )

        return EmotionResponse(
            primary_emotion=combined["primary_emotion"],
            confidence=combined["confidence"],
            engagement_level=combined["engagement"],
            facial_emotions=facial_emotions,
            voice_emotions=voice_emotions,
            interaction_score=interaction_score,
            needs_intervention=combined["needs_intervention"],
        )

    def _decode_image(self, b64: str) -> np.ndarray:
        byt = base64.b64decode(b64.split(",")[1] if "," in b64 else b64)
        img = cv2.imdecode(np.frombuffer(byt, np.uint8), cv2.IMREAD_COLOR)
        return img

    def _decode_audio(self, b64: str) -> np.ndarray:
        raw = base64.b64decode(b64.split(",")[1] if "," in b64 else b64)
        audio, sr = sf.read(io.BytesIO(raw))
        if sr != 22050:
            audio = librosa.resample(audio.astype(float), orig_sr=sr, target_sr=22050)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        return audio

    def _combine_emotions(
        self, facial: Dict[str, float], voice: Dict[str, float], interaction: float
    ) -> Dict[str, float]:
        mapper = {
            "confused": ["confused", "fear", "surprise"],
            "frustrated": ["angry", "disgust", "fearful"],
            "bored": ["sad", "neutral", "calm"],
            "engaged": ["happy", "surprise"],
        }

        scores = {k: 0.0 for k in mapper}

        if facial:
            for cat, ems in mapper.items():
                scores[cat] += (
                    sum(facial.get(e, 0.0) for e in ems) * self.emotion_weights["facial"]
                )

        if voice:
            for cat, ems in mapper.items():
                scores[cat] += (
                    sum(voice.get(e, 0.0) for e in ems) * self.emotion_weights["voice"]
                )

        if interaction < 0.3:
            scores["bored"] += 0.3 * self.emotion_weights["interaction"]
        elif interaction > 0.7:
            scores["engaged"] += 0.3 * self.emotion_weights["interaction"]

        primary = max(scores, key=scores.get)
        confidence = scores[primary]
        engagement = max(0.0, min(1.0, scores["engaged"] - scores["bored"] + 0.5))
        needs = (
            scores["confused"] > 0.6
            or scores["frustrated"] > 0.5
            or scores["bored"] > 0.6
        )

        return {
            "primary_emotion": primary,
            "confidence": confidence,
            "engagement": engagement,
            "needs_intervention": needs,
        }


emotion_service = EmotionDetectionService()
