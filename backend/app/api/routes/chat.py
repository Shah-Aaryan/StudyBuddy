from fastapi import APIRouter, HTTPException, Depends
from app.services.gemini_service import GeminiChatbot
from app.models.schemas import ChatMessage, ChatResponse, ChatHistoryResponse,GeneralChatRequest,GeneralChatResponse
import logging

logger = logging.getLogger(__name__)

# Create router
chat_router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize chatbot (you could also use dependency injection)
chatbot = GeminiChatbot()

@chat_router.post("/ask", response_model=GeneralChatResponse)
async def general_chat_response(payload: GeneralChatRequest):
    """Handle general chat without user session tracking"""
    try:
        # Create a temp chat session
        temp_session = chatbot.model.start_chat(history=[])

        # Send message
        result = temp_session.send_message(payload.message)

        return GeneralChatResponse(
            response=result.text,
            status="success"
        )
    except Exception as e:
        logger.error(f"Error in general chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating response")

@chat_router.post("/", response_model=ChatResponse)
async def send_chat_message(chat_message: ChatMessage):
    """Send message to Gemini chatbot"""
    try:
        logger.info(f"Received message from user {chat_message.user_id}")
        
        response = await chatbot.send_message(
            user_id=chat_message.user_id,
            message=chat_message.message
        )
        
        logger.info(f"Generated response for user {chat_message.user_id}")
        return ChatResponse(
            user_id=chat_message.user_id,
            response=response,
            status="success"
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@chat_router.post("/clear/{user_id}")
async def clear_user_chat_history(user_id: str):
    """Clear chat history for a specific user"""
    try:
        chatbot.clear_chat_history(user_id)
        return {"message": f"Chat history cleared for user {user_id}", "status": "success"}
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")

@chat_router.get("/history/{user_id}", response_model=ChatHistoryResponse)
async def get_user_chat_history(user_id: str):
    """Get chat history for a specific user"""
    try:
        history = chatbot.get_chat_history(user_id)
        return ChatHistoryResponse(
            user_id=user_id,
            history=history,
            status="success"
        )
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@chat_router.get("/health")
async def chatbot_health_check():
    """Health check for chatbot service"""
    return {"status": "Chatbot service is running", "service": "gemini"}

@chat_router.get("/sessions")
async def get_active_sessions():
    """Get count of active chat sessions"""
    try:
        session_count = len(chatbot.chat_sessions)
        return {
            "active_sessions": session_count,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session information")