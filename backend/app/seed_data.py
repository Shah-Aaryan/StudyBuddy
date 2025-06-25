import asyncio
from datetime import datetime, timedelta
from app.config.session import async_session_maker
from app.models.database import User, LearningSession, EmotionLog, Intervention
from app.utils.helpers import hash_password  # Assumes your hash_password function exists
from sqlalchemy import select

async def seed():
    async with async_session_maker() as session:
        # Fetch existing user with ID 4
        user = await session.scalar(select(User).where(User.id == 4))

        now = datetime.utcnow()
        learning_sessions = []

        # Add 7 new learning sessions
        for i in range(7):
            start = now - timedelta(days=i)
            end = start + timedelta(minutes=60)
            ls = LearningSession(
                user_id=user.id,
                course_id="course_analytics",
                lesson_id=f"lesson_extra_{i+1}",  # Make lesson_id unique to avoid conflict
                start_time=start,
                end_time=end,
                duration_minutes=60,
                average_engagement=0.6 + i * 0.05,
                completion_percentage=70 + i * 5,
                intervention_count=1
            )
            session.add(ls)
            learning_sessions.append(ls)

        await session.flush()

        # Add 21 new emotion logs
        for i in range(21):
            ls_for_log = learning_sessions[i % 7]
            emotion_log = EmotionLog(
                user_id=user.id,
                session_id=ls_for_log.id,
                facial_emotions={"happy": 0.6, "sad": 0.2},
                voice_emotions={"neutral": 0.7},
                interaction_score=0.6 + (i % 3) * 0.1,
                primary_emotion=["happy", "sad", "bored", "confused"][i % 4],
                confidence_score=0.9,
                engagement_level=0.7 + (i % 3) * 0.05,
                timestamp=now - timedelta(days=i // 3, hours=i % 3)
            )
            session.add(emotion_log)

        # Add 5 new interventions
        for i in range(5):
            intervention = Intervention(
                session_id=learning_sessions[i].id,
                timestamp=now - timedelta(days=i),
                trigger_emotion="confused",
                intervention_type="video",
                resource_id=f"video_extra_{i+1}",
                user_response="completed",
                effectiveness_score=0.75 + 0.05 * (i % 3)
            )
            session.add(intervention)

        await session.commit()
        print("✅ Added more data to existing user 4!")

if __name__ == "__main__":
    asyncio.run(seed())
