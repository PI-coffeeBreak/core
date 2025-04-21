from fastapi import APIRouter, Depends, WebSocket
from dependencies.auth import get_current_user
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.notifications import NotificationService
from services.websocket_service import WebSocketService, WebSocketConnection
from schemas.notification import NotificationResponse
from typing import List
import logging

logger = logging.getLogger("coffeebreak.notifications")
router = APIRouter()

# Initialize WebSocket handlers
websocket_service = WebSocketService()
notification_service = NotificationService()

@websocket_service.on_receive("notifications")
async def handle_notification_message(connection: WebSocketConnection, message: dict):
    logger.debug(f"Received notification message: {message}")
    try:
        notification_service = NotificationService(None)  # DB will be set in the service
        action = message.get("action")
        
        if action == "get_public_announcements":
            # Public announcements don't require authentication
            notifications = await notification_service.get_broadcast_notifications()
            await connection.send({
                "type": "notification_update",
                "status": "success",
                "action": "public_announcements",
                "notifications": [n.to_dict() for n in notifications]
            })
            return

        # All other actions require authentication
        if not connection.is_authenticated():
            await connection.send({
                "type": "notification_update",
                "status": "error",
                "message": "Authentication required for this action"
            })
            return

        if action == "mark_read":
            # Mark notifications as read
            notification_ids = message.get("notification_ids", [])
            await notification_service.mark_notifications_read(connection.user_id, notification_ids)
            
            # Send confirmation back to the client
            await connection.send({
                "type": "notification_update",
                "status": "success",
                "action": "mark_read",
                "notification_ids": notification_ids
            })
        
        elif action == "get_unread":
            # Get unread notifications
            notifications = await notification_service.get_user_notifications(connection.user_id)
            
            # Send notifications to the client
            await connection.send({
                "type": "notification_update",
                "status": "success",
                "action": "unread_notifications",
                "notifications": [n.to_dict() for n in notifications]
            })
        
        else:
            logger.warning(f"Unknown notification action: {action}")
            await connection.send({
                "type": "notification_update",
                "status": "error",
                "message": "Unknown action"
            })
            
    except Exception as e:
        logger.error(f"Error handling notification message: {str(e)}")
        await connection.send({
            "type": "notification_update",
            "status": "error",
            "message": "Internal server error"
        })

@websocket_service.on_subscribe("notifications")
async def handle_notification_subscription(connection: WebSocketConnection):
    """Handle new subscription to notifications topic"""
    logger.debug(f"New subscription to notifications topic from connection {connection.connection_id}")
    
    # Add connection to NotificationService
    notification_service.add_connection(connection)

@websocket_service.on_unsubscribe("notifications")
async def handle_notification_unsubscribe(connection: WebSocketConnection):
    """Handle unsubscription from notifications topic"""
    logger.debug(f"Unsubscribed from notifications topic: {connection.connection_id}")
    # Remove connection from NotificationService
    notification_service.remove_connection(connection)


@router.get("/in-app", response_model=List[NotificationResponse])
async def get_in_app_notifications(
    userdata: dict | None = Depends(
        get_current_user(force_auth=False)),
    db: Session = Depends(get_db)
):
    """
    Get notifications based on authentication status:
    - For authenticated users: returns all undelivered notifications (individual, group, and broadcast)
    - For unauthenticated users: returns only broadcast notifications
    Notifications are marked as delivered only for authenticated users.
    """
    notification_service = NotificationService(db)

    if userdata is None:
        # Return only broadcast notifications for unauthenticated users
        return await notification_service.get_broadcast_notifications()

    # Return all notifications for authenticated users
    return await notification_service.get_user_notifications(userdata["sub"])
