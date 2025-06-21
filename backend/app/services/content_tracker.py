# services/content_tracker.py
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import logging

from app.models.database import get_db, ContentInteraction, VideoContent, User
from app.models.schemas import ContentEvent
from app.config.settings import settings

logger = logging.getLogger(__name__)

class ContentTracker:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.active_sessions = {}  # Track active content sessions
        
        # LLM prompt for content analysis
        self.content_analysis_prompt = PromptTemplate(
            input_variables=["video_title", "video_description", "user_emotion", "difficulty_level"],
            template="""
            Analyze this educational content and recommend 3 similar videos that would help a student who is {user_emotion}:
            
            Current Video: {video_title}
            Description: {video_description}
            Student's Current Emotion: {user_emotion}
            Current Difficulty Level: {difficulty_level}
            
            Please provide recommendations in this JSON format:
            {{
                "recommendations": [
                    {{
                        "title": "Recommended video title",
                        "description": "Why this video helps",
                        "difficulty": "easier/same/harder",
                        "search_query": "YouTube search query",
                        "reasoning": "Why this helps with {user_emotion}"
                    }}
                ]
            }}
            """
        )
    
    async def track_content_event(self, user_id: int, event: ContentEvent, db: Session):
        """Track content interaction events"""
        try:
            # Store interaction in database
            interaction = ContentInteraction(
                user_id=user_id,
                content_id=event.content_id,
                content_type=event.content_type,
                event_type=event.event_type,
                timestamp=event.timestamp,
                duration_seconds=event.duration_seconds,
                progress_percentage=event.progress_percentage,
                metadata=event.metadata
            )
            db.add(interaction)
            db.commit()
            
            # Update active session tracking
            session_key = f"{user_id}_{event.content_id}"
            if event.event_type == "start":
                self.active_sessions[session_key] = {
                    "start_time": event.timestamp,
                    "content_id": event.content_id,
                    "user_id": user_id,
                    "content_type": event.content_type,
                    "metadata": event.metadata
                }
            elif event.event_type in ["complete", "stop"]:
                if session_key in self.active_sessions:
                    session = self.active_sessions[session_key]
                    total_duration = (event.timestamp - session["start_time"]).total_seconds()
                    
                    # Update content engagement analytics
                    await self._update_content_analytics(
                        user_id, event.content_id, total_duration, 
                        event.progress_percentage, db
                    )
                    
                    del self.active_sessions[session_key]
            
            # Extract content topic if video
            if event.content_type == "video" and event.metadata:
                await self._analyze_video_content(user_id, event, db)
                
        except Exception as e:
            logger.error(f"Error tracking content event: {e}")
    
    async def _analyze_video_content(self, user_id: int, event: ContentEvent, db: Session):
        """Analyze video content and extract topics using LLM"""
        try:
            video_title = event.metadata.get("title", "")
            video_description = event.metadata.get("description", "")
            
            if not video_title:
                return
            
            # Use LLM to extract topics and concepts
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational content analyst. Extract the main topics, concepts, and learning objectives from educational video metadata."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this educational video:\nTitle: {video_title}\nDescription: {video_description}\n\nExtract:\n1. Main topics (3-5 keywords)\n2. Subject area\n3. Difficulty level (beginner/intermediate/advanced)\n4. Learning objectives\n\nReturn as JSON."
                    }
                ]
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Store or update video content analysis
            video_content = db.query(VideoContent).filter(
                VideoContent.content_id == event.content_id
            ).first()
            
            if not video_content:
                video_content = VideoContent(
                    content_id=event.content_id,
                    title=video_title,
                    description=video_description,
                    topics=analysis.get("main_topics", []),
                    subject_area=analysis.get("subject_area", ""),
                    difficulty_level=analysis.get("difficulty_level", "intermediate"),
                    learning_objectives=analysis.get("learning_objectives", []),
                    analyzed_at=datetime.utcnow()
                )
                db.add(video_content)
            else:
                # Update existing analysis
                video_content.topics = analysis.get("main_topics", [])
                video_content.subject_area = analysis.get("subject_area", "")
                video_content.difficulty_level = analysis.get("difficulty_level", "intermediate")
                video_content.learning_objectives = analysis.get("learning_objectives", [])
                video_content.analyzed_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error analyzing video content: {e}")
    
    async def get_content_recommendations(self, user_id: int, current_emotion: str, 
                                        current_content_id: str, db: Session) -> List[Dict]:
        """Get LLM-powered content recommendations based on current emotion and content"""
        try:
            # Get current content details
            current_content = db.query(VideoContent).filter(
                VideoContent.content_id == current_content_id
            ).first()
            
            if not current_content:
                return []
            
            # Get user's emotion context
            user_emotion_context = self._get_emotion_context(current_emotion)
            
            # Generate recommendations using LLM
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an adaptive learning assistant. Based on a student's current emotional state and the content they're viewing, recommend similar educational content that would help them succeed."""
                    },
                    {
                        "role": "user",
                        "content": self.content_analysis_prompt.format(
                            video_title=current_content.title,
                            video_description=current_content.description,
                            user_emotion=user_emotion_context,
                            difficulty_level=current_content.difficulty_level
                        )
                    }
                ]
            )
            
            recommendations = json.loads(response.choices[0].message.content)
            
            # Enhance recommendations with YouTube search
            enhanced_recommendations = []
            for rec in recommendations.get("recommendations", []):
                # Search for actual video URLs
                video_urls = await self._search_youtube_videos(rec["search_query"])
                
                enhanced_rec = {
                    **rec,
                    "video_urls": video_urls[:3],  # Top 3 results
                    "recommendation_reason": rec["reasoning"],
                    "generated_at": datetime.utcnow().isoformat()
                }
                enhanced_recommendations.append(enhanced_rec)
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error getting content recommendations: {e}")
            return []
    
    def _get_emotion_context(self, emotion: str) -> str:
        """Convert emotion to learning context"""
        emotion_contexts = {
            "confused": "struggling to understand the concept and needs clearer, simpler explanations",
            "frustrated": "feeling overwhelmed and needs encouraging, step-by-step guidance",
            "bored": "losing interest and needs engaging, interactive content",
            "engaged": "actively learning and ready for additional challenging material"
        }
        return emotion_contexts.get(emotion, "actively learning")
    
    async def _search_youtube_videos(self, query: str) -> List[str]:
        """Search YouTube for educational videos (mock implementation)"""
        # In a real implementation, you would use YouTube Data API
        # For now, return mock URLs based on search query
        mock_urls = [
            f"https://youtube.com/watch?v=mock1_{hash(query) % 1000}",
            f"https://youtube.com/watch?v=mock2_{hash(query) % 1000}",
            f"https://youtube.com/watch?v=mock3_{hash(query) % 1000}"
        ]
        return mock_urls
    
    async def _update_content_analytics(self, user_id: int, content_id: str, 
                                      duration: float, completion: float, db: Session):
        """Update content engagement analytics"""
        try:
            # Update user's content engagement patterns
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # Update learning analytics
                if not user.learning_analytics:
                    user.learning_analytics = {}
                
                analytics = user.learning_analytics
                analytics["total_watch_time"] = analytics.get("total_watch_time", 0) + duration
                analytics["content_completions"] = analytics.get("content_completions", 0) + (1 if completion > 0.8 else 0)
                analytics["last_activity"] = datetime.utcnow().isoformat()
                
                user.learning_analytics = analytics
                db.commit()
                
        except Exception as e:
            logger.error(f"Error updating content analytics: {e}")
    
    async def get_user_content_patterns(self, user_id: int, db: Session) -> Dict:
        """Analyze user's content consumption patterns"""
        try:
            # Get user's interactions
            interactions = db.query(ContentInteraction).filter(
                ContentInteraction.user_id == user_id
            ).all()
            
            if not interactions:
                return {}
            
            # Analyze patterns
            total_interactions = len(interactions)
            completed_content = len([i for i in interactions 
                                   if i.event_type == "complete"])
            
            content_types = {}
            for interaction in interactions:
                content_type = interaction.content_type
                content_types[content_type] = content_types.get(content_type, 0) + 1
            
            preferred_content_type = max(content_types, key=content_types.get) if content_types else "video"
            
            return {
                "total_interactions": total_interactions,
                "completion_rate": completed_content / total_interactions if total_interactions > 0 else 0,
                "preferred_content_type": preferred_content_type,
                "content_type_distribution": content_types,
                "analysis_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content patterns: {e}")
            return {}

content_tracker = ContentTracker()