"""
WebSocket endpoints for real-time updates
"""

import asyncio
import json
import logging
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.notification_service import NotificationService
from app.api.v1.auth import get_current_user_from_token
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Global notification service instance
notification_service = NotificationService()


@router.websocket("/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time updates
    
    Connects with JWT token and joins household-specific room for updates
    """
    # Authenticate user from token
    try:
        from app.utils.security import verify_token
        
        payload = verify_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid authentication")
            return
            
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
            
        # Get user and verify they're active
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await websocket.close(code=1008, reason="User not found")
            return
            
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return
        
    # Check if user belongs to a household
    if not user.household_id:
        await websocket.close(code=1008, reason="User not in a household")
        return
        
    household_id = str(user.household_id)
    
    # Store user info on websocket for later use
    websocket.user_id = user_id
    websocket.household_id = household_id
    
    # Connect to WebSocket
    await notification_service.connect_websocket(household_id, websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "message": f"Connected to household {household_id}",
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Keep connection alive and handle messages
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message, user, db)
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": asyncio.get_event_loop().time()
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
        notification_service.disconnect_websocket(household_id, websocket)
        
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        notification_service.disconnect_websocket(household_id, websocket)


async def handle_websocket_message(
    websocket: WebSocket,
    message: Dict[str, Any],
    user: User,
    db: AsyncSession
):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping with pong
        await websocket.send_json({
            "type": "pong",
            "timestamp": asyncio.get_event_loop().time()
        })
        
    elif message_type == "subscribe":
        # Subscribe to specific event types
        event_types = message.get("events", [])
        await websocket.send_json({
            "type": "subscribed",
            "events": event_types,
            "timestamp": asyncio.get_event_loop().time()
        })
        
    elif message_type == "inventory_update":
        # Broadcast inventory update to household
        await notification_service.send_household_update(
            household_id=str(user.household_id),
            event_type="inventory_updated",
            data={
                "action": message.get("action"),
                "item_id": message.get("item_id"),
                "item_name": message.get("item_name"),
                "updated_by": user.username
            },
            exclude_user_id=str(user.id)
        )
        
    elif message_type == "meal_plan_update":
        # Broadcast meal plan update
        await notification_service.send_household_update(
            household_id=str(user.household_id),
            event_type="meal_plan_updated",
            data={
                "action": message.get("action"),
                "plan_id": message.get("plan_id"),
                "updated_by": user.username
            },
            exclude_user_id=str(user.id)
        )
        
    elif message_type == "shopping_list_update":
        # Broadcast shopping list update
        await notification_service.send_household_update(
            household_id=str(user.household_id),
            event_type="shopping_list_updated",
            data={
                "action": message.get("action"),
                "list_id": message.get("list_id"),
                "updated_by": user.username
            },
            exclude_user_id=str(user.id)
        )
        
    else:
        # Unknown message type
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "timestamp": asyncio.get_event_loop().time()
        })


@router.post("/broadcast/{household_id}")
async def broadcast_to_household(
    household_id: str,
    message: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """
    HTTP endpoint to broadcast message to household via WebSocket
    
    This allows backend services to send real-time updates
    """
    # Verify user belongs to the household
    if str(current_user.household_id) != household_id:
        raise HTTPException(
            status_code=403,
            detail="User does not belong to this household"
        )
        
    event_type = message.get("type", "broadcast")
    data = message.get("data", {})
    
    await notification_service.send_household_update(
        household_id=household_id,
        event_type=event_type,
        data=data
    )
    
    return {"message": "Broadcast sent successfully"}


@router.get("/connections")
async def get_websocket_connections():
    """Get current WebSocket connection statistics"""
    stats = {
        "total_households": len(notification_service.active_connections),
        "total_connections": sum(len(conns) for conns in notification_service.active_connections.values()),
        "households": {
            household_id: len(connections)
            for household_id, connections in notification_service.active_connections.items()
        }
    }
    
    return stats


# Cleanup on shutdown
async def cleanup_websockets():
    """Cleanup all WebSocket connections on shutdown"""
    await notification_service.cleanup()
    logger.info("WebSocket cleanup completed")