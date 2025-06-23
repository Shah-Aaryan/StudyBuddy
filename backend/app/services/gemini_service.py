import google.generativeai as genai
import os
from typing import List, Dict
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GeminiChatbot:
    def __init__(self):
        api_key =  settings.gemini_api_key
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat_sessions = {}
    
    def start_chat_session(self, user_id: str):
        """Start a new chat session for a user"""
        self.chat_sessions[user_id] = self.model.start_chat(history=[])
        return self.chat_sessions[user_id]
    
    def get_chat_session(self, user_id: str):
        """Get existing chat session or create new one"""
        if user_id not in self.chat_sessions:
            return self.start_chat_session(user_id)
        return self.chat_sessions[user_id]
    
    async def send_message(self, user_id: str, message: str) -> str:
        """Send message to Gemini and get response"""
        try:
            chat_session = self.get_chat_session(user_id)
            response = chat_session.send_message(message)
            return response.text
        except Exception as e:
            logger.error(f"Error sending message to Gemini: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def clear_chat_history(self, user_id: str):
        """Clear chat history for a user"""
        if user_id in self.chat_sessions:
            del self.chat_sessions[user_id]
            logger.info(f"Cleared chat history for user: {user_id}")
    
    def get_chat_history(self, user_id: str) -> List[Dict]:
        """Get chat history for a user"""
        if user_id in self.chat_sessions:
            return [
                {"role": msg.role, "content": msg.parts[0].text}
                for msg in self.chat_sessions[user_id].history
            ]
        return []