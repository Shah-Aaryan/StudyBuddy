# services/notification_service.py
import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import WebSocket
import logging

from app.models.database import get_db, User, Notification, NotificationPreference
# from app.services.email_service import email_service
import requests

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.active_websockets: Dict[int, WebSocket] = {}
        self.fcm_server_key = "your-fcm-server-key"  # Configure in settings
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
    
    def add_websocket_connection(self, user_id: int, websocket: WebSocket):
        """Add websocket connection for real-time notifications"""
        self.active_websockets[user_id] = websocket
    
    def remove_websocket_connection(self, user_id: int):
        """Remove websocket connection"""
        if user_id in self.active_websockets:
            del self.active_websockets[user_id]
    
    async def send_realtime_notification(self, user_id: int, notification: Dict):
        """Send real-time notification via WebSocket"""
        if user_id in self.active_websockets:
            try:
                websocket = self.active_websockets[user_id]
                await websocket.send_text(json.dumps({
                    "type": "notification",
                    "data": notification
                }))
                return True
            except Exception as e:
                logger.error(f"Error sending real-time notification: {e}")
                # Remove dead connection
                self.remove_websocket_connection(user_id)
        return False
    
    async def send_push_notification(self, user_id: int, title: str, body: str, 
                                   data: Dict = None, db: Session = None):
        """Send push notification via FCM"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.fcm_token:
                return False
            
            # Check user preferences
            prefs = db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id
            ).first()
            
            if prefs and not prefs.push_notifications_enabled:
                return False
            
            payload = {
                "to": user.fcm_token,
                "notification": {
                    "title": title,
                    "body": body,
                    "icon": "/static/icons/app-icon.png",
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                },
                "data": data or {}
            }
            
            headers = {
                "Authorization": f"key={self.fcm_server_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.fcm_url, 
                                   data=json.dumps(payload), 
                                   headers=headers)
            
            if response.status_code == 200:
                # Store notification in database
                notification = Notification(
                    user_id=user_id,
                    title=title,
                    message=body,
                    notification_type="push",
                    data=data,
                    sent_at=datetime.utcnow()
                )
                db.add(notification)
                db.commit()
                return True
            else:
                logger.error(f"FCM error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    async def send_feedback_notification(self, user_id: int, feedback_type: str, 
                                       resource_url: str, db: Session):
        """Send feedback-specific notification"""
        messages = {
            "confused": {
                "title": "Need Help?",
                "body": "I noticed you might be confused. Check out this helpful resource!"
            },
            "frustrated": {
                "title": "Take a Deep Breath",
                "body": "Let's try a different approach. Here's something that might help."
            },
            "bored": {
                "title": "Let's Make It Fun!",
                "body": "Time to spice things up with an interactive activity!"
            },
            "engaged": {
                "title": "Great Work!",
                "body": "You're doing amazing! Keep up the excellent progress."
            }
        }
        
        message_config = messages.get(feedback_type, messages["confused"])
        
        # Send real-time notification first
        realtime_sent = await self.send_realtime_notification(user_id, {
            "title": message_config["title"],
            "message": message_config["body"],
            "type": "feedback",
            "resource_url": resource_url,
            "feedback_type": feedback_type
        })
        
        # Send push notification as backup
        if not realtime_sent:
            await self.send_push_notification(
                user_id, 
                message_config["title"], 
                message_config["body"],
                {"resource_url": resource_url, "type": "feedback"},
                db
            )
    
    async def send_progress_notification(self, user_id: int, achievement: str, db: Session):
        """Send progress/achievement notification"""
        await self.send_push_notification(
            user_id,
            "Achievement Unlocked! 🎉",
            f"Congratulations! You've {achievement}",
            {"type": "achievement", "achievement": achievement},
            db
        )
    
    async def send_reminder_notification(self, user_id: int, message: str, db: Session):
        """Send reminder notification"""
        await self.send_push_notification(
            user_id,
            "Learning Reminder",
            message,
            {"type": "reminder"},
            db
        )
    
    async def schedule_daily_reminders(self):
        """Schedule daily learning reminders"""
        try:
            db = next(get_db())
            
            # Get users who want daily reminders
            users_with_reminders = db.query(User).join(NotificationPreference).filter(
                NotificationPreference.daily_reminders == True,
                User.is_active == True
            ).all()
            
            for user in users_with_reminders:
                # Check if user has been inactive for more than 24 hours
                last_session = db.query(LearningSession).filter(
                    LearningSession.user_id == user.id
                ).order_by(LearningSession.start_time.desc()).first()
                
                if not last_session or \
                   (datetime.utcnow() - last_session.start_time) > timedelta(hours=24):
                    await self.send_reminder_notification(
                        user.id,
                        "Ready to learn something new today? 📚",
                        db
                    )
            
        except Exception as e:
            logger.error(f"Error scheduling daily reminders: {e}")
    
    async def get_user_notifications(self, user_id: int, limit: int = 50, 
                                   db: Session = None) -> List[Dict]:
        """Get user notifications"""
        if not db:
            db = next(get_db())
        
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "data": n.data,
                "read": n.read,
                "created_at": n.created_at,
                "sent_at": n.sent_at
            }
            for n in notifications
        ]
    
    async def mark_notification_read(self, notification_id: int, user_id: int, 
                                   db: Session = None):
        """Mark notification as read"""
        if not db:
            db = next(get_db())
        
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.read = True
            notification.read_at = datetime.utcnow()
            db.commit()

notification_service = NotificationService()