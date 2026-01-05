"""
Notification service for sending alerts and updates
Supports WebSocket, push notifications, and email
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.user import User, Household

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        # WebSocket connections by household
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # Push notification tokens by user
        self.push_tokens: Dict[str, List[str]] = {}
        
    # WebSocket Management
    
    async def connect_websocket(self, household_id: str, websocket: WebSocket):
        """Connect a WebSocket for real-time updates"""
        await websocket.accept()
        
        if household_id not in self.active_connections:
            self.active_connections[household_id] = []
            
        self.active_connections[household_id].append(websocket)
        logger.info(f"WebSocket connected for household {household_id}")
        
    def disconnect_websocket(self, household_id: str, websocket: WebSocket):
        """Disconnect a WebSocket"""
        if household_id in self.active_connections:
            try:
                self.active_connections[household_id].remove(websocket)
                logger.info(f"WebSocket disconnected for household {household_id}")
            except ValueError:
                pass
                
            if not self.active_connections[household_id]:
                del self.active_connections[household_id]
                
    async def send_household_update(
        self,
        household_id: str,
        event_type: str,
        data: Dict[str, Any],
        exclude_user_id: Optional[str] = None
    ):
        """Send update to all connected clients in a household"""
        if household_id not in self.active_connections:
            return
            
        message = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        disconnected = []
        for websocket in self.active_connections[household_id]:
            try:
                # Check if this connection should be excluded (e.g., sender)
                if exclude_user_id and hasattr(websocket, "user_id") and websocket.user_id == exclude_user_id:
                    continue
                    
                await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(websocket)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                disconnected.append(websocket)
                
        # Remove disconnected clients
        for websocket in disconnected:
            self.disconnect_websocket(household_id, websocket)
            
    # Push Notifications
    
    def register_push_token(self, user_id: str, token: str, platform: str = "fcm"):
        """Register push notification token for a user"""
        if user_id not in self.push_tokens:
            self.push_tokens[user_id] = []
            
        token_data = {"token": token, "platform": platform}
        if token_data not in self.push_tokens[user_id]:
            self.push_tokens[user_id].append(token_data)
            logger.info(f"Push token registered for user {user_id}")
            
    def unregister_push_token(self, user_id: str, token: str):
        """Unregister push notification token"""
        if user_id in self.push_tokens:
            self.push_tokens[user_id] = [
                t for t in self.push_tokens[user_id] if t["token"] != token
            ]
            
            if not self.push_tokens[user_id]:
                del self.push_tokens[user_id]
                
    async def send_push_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ):
        """Send push notification to user"""
        if user_id not in self.push_tokens:
            return
            
        notification = {
            "title": title,
            "body": body,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {},
            "priority": priority
        }
        
        # Send to all registered tokens for this user
        for token_data in self.push_tokens[user_id]:
            try:
                if token_data["platform"] == "fcm":
                    await self._send_fcm_notification(token_data["token"], notification)
                elif token_data["platform"] == "apns":
                    await self._send_apns_notification(token_data["token"], notification)
            except Exception as e:
                logger.error(f"Failed to send push notification: {e}")
                
    async def _send_fcm_notification(self, token: str, notification: Dict[str, Any]):
        """Send Firebase Cloud Messaging notification"""
        # This would integrate with Firebase Admin SDK
        # For now, just log the action
        logger.info(f"FCM notification sent to {token}: {notification['title']}")
        
    async def _send_apns_notification(self, token: str, notification: Dict[str, Any]):
        """Send Apple Push Notification"""
        # This would integrate with APNS
        # For now, just log the action
        logger.info(f"APNS notification sent to {token}: {notification['title']}")
        
    # High-level Notification Methods
    
    async def send_household_notification(
        self,
        household_id: str,
        title: str,
        message: str,
        notification_type: str,
        data: Optional[Dict[str, Any]] = None,
        exclude_user_id: Optional[str] = None
    ):
        """Send notification to all household members"""
        # Send WebSocket update
        await self.send_household_update(
            household_id,
            notification_type,
            {"title": title, "message": message, **(data or {})},
            exclude_user_id
        )
        
        # Send push notifications (would need to get user IDs from household)
        # This would query the database for household members
        
    async def send_expiration_alert(
        self,
        user_id: str,
        items: List[Dict[str, Any]]
    ):
        """Send expiration alert for items"""
        if not items:
            return
            
        title = f"{len(items)} items expiring soon!"
        
        if len(items) == 1:
            body = f"{items[0]['name']} expires in {items[0]['days']} days"
        else:
            body = f"Items include: {', '.join([item['name'] for item in items[:3]])}"
            if len(items) > 3:
                body += f" and {len(items) - 3} more"
                
        await self.send_push_notification(
            user_id,
            title,
            body,
            data={"type": "expiration_alert", "items": items},
            priority="high"
        )
        
    async def send_low_stock_alert(
        self,
        user_id: str,
        items: List[Dict[str, Any]]
    ):
        """Send low stock alert"""
        if not items:
            return
            
        title = f"Low stock alert"
        body = f"Running low on: {', '.join([item['name'] for item in items[:3]])}"
        
        await self.send_push_notification(
            user_id,
            title,
            body,
            data={"type": "low_stock_alert", "items": items}
        )
        
    async def send_achievement_unlocked(
        self,
        user_id: str,
        achievement_name: str,
        achievement_description: str
    ):
        """Send achievement unlocked notification"""
        await self.send_push_notification(
            user_id,
            "Achievement Unlocked! 🏆",
            f"{achievement_name}: {achievement_description}",
            data={
                "type": "achievement_unlocked",
                "achievement_name": achievement_name,
                "achievement_description": achievement_description
            },
            priority="high"
        )
        
    async def send_meal_plan_reminder(
        self,
        user_id: str,
        meal_name: str,
        meal_time: str
    ):
        """Send meal plan reminder"""
        await self.send_push_notification(
            user_id,
            f"Time for {meal_name}!",
            f"Your {meal_time} is scheduled for now",
            data={"type": "meal_reminder", "meal_name": meal_name}
        )
        
    async def send_shopping_list_reminder(
        self,
        user_id: str,
        list_name: str,
        item_count: int
    ):
        """Send shopping list reminder"""
        await self.send_push_notification(
            user_id,
            "Shopping Reminder",
            f"You have {item_count} items on your {list_name}",
            data={"type": "shopping_reminder", "list_name": list_name}
        )
        
    # Scheduled Notifications
    
    async def schedule_daily_notifications(self):
        """Schedule daily notification checks"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Check for expiring items (run at 9 AM)
                if current_time.hour == 9:
                    await self._check_expiring_items()
                    
                # Check for meal plan reminders (run every hour)
                await self._check_meal_reminders()
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in scheduled notifications: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
                
    async def _check_expiring_items(self):
        """Check for items expiring soon and send alerts"""
        # This would query the database for all users/households
        # and send notifications for expiring items
        logger.info("Checking for expiring items...")
        
    async def _check_meal_reminders(self):
        """Check for meal plan reminders"""
        # This would check scheduled meals and send reminders
        logger.info("Checking for meal reminders...")
        
    # Cleanup
    
    async def cleanup(self):
        """Cleanup resources"""
        # Close all WebSocket connections
        for household_id, connections in self.active_connections.items():
            for websocket in connections:
                try:
                    await websocket.close()
                except Exception:
                    pass
                    
        self.active_connections.clear()
        logger.info("Notification service cleaned up")