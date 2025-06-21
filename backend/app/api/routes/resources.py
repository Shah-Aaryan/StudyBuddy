from fastapi import APIRouter, HTTPException
from app.services.resource_recommender import resource_recommender
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/explanatory/{lesson_id}")
async def get_explanatory_resources(lesson_id: str, topic: str = ""):
    """Get explanatory resources for a lesson"""
    try:
        resource = await resource_recommender.get_explanatory_content(lesson_id, topic)
        return resource
    except Exception as e:
        logger.error(f"Error getting explanatory resources: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving resources")

@router.get("/games/{lesson_id}")
async def get_game_resources(lesson_id: str, topic: str = ""):
    """Get interactive game resources"""
    try:
        resource = await resource_recommender.get_interactive_game(lesson_id, topic)
        return resource
    except Exception as e:
        logger.error(f"Error getting game resources: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving games")

@router.get("/breaks")
async def get_break_activities(break_type: str = "breathing"):
    """Get mindful break activities"""
    try:
        resource = await resource_recommender.get_break_activity(break_type)
        return resource
    except Exception as e:
        logger.error(f"Error getting break activities: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving break activities")

@router.get("/content/adaptive")
async def get_adaptive_content(
    user_emotion: str,
    lesson_id: str,
    topic: str = "",
    difficulty: str = "medium"
):
    """Get adaptive content based on current emotion"""
    try:
        if user_emotion == "confused":
            resource = await resource_recommender.get_explanatory_content(lesson_id, topic)
        elif user_emotion == "frustrated":
            resource = await resource_recommender.get_simplified_content(lesson_id, difficulty)
        elif user_emotion == "bored":
            resource = await resource_recommender.get_interactive_game(lesson_id, topic)
        else:
            resource = await resource_recommender.get_interactive_content(lesson_id, topic)
        
        return resource
    except Exception as e:
        logger.error(f"Error getting adaptive content: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving adaptive content")