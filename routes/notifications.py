from fastapi import APIRouter, Depends, WebSocket, HTTPException
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

@websocket_service.on_receive("notifications")
async def handle_notification_message(connection: WebSocketConnection, message: dict):
    logger.debug(f"Received notification message: {message}")
    try:
        notification_service = NotificationService(None)
        action = message.get("action")

        if action == "mark_read":
            notification_ids = message.get("notification_ids", [])
            await notification_service.mark_notifications_read(connection.user_id, notification_ids)
            await connection.send({
                "action": "mark_read",
                "status": "success",
                "notification_ids": notification_ids
            })
        
        elif action == "get_unread":
            notifications = await notification_service.get_user_notifications(connection.user_id)
            # Convert notifications to NotificationResponse format
            notification_responses = [NotificationResponse.model_validate(n).model_dump() for n in notifications]
            await connection.send({
                "action": "unread_notifications",
                "status": "success",
                "notifications": notification_responses
            })
        
        else:
            logger.warning(f"Unknown notification action: {action}")
            await connection.send({
                "status": "error",
                "message": "Unknown action"
            })
            
    except Exception as e:
        logger.error(f"Error handling notification message: {str(e)}")
        await connection.send({
            "status": "error",
            "message": "Internal server error"
        })

@websocket_service.on_subscribe("notifications")
async def handle_notification_subscription(connection: WebSocketConnection):
    """Handle new subscription to notifications topic"""
    logger.debug(f"New subscription to notifications topic from connection {connection.connection_id}")
    NotificationService().add_connection(connection)

@websocket_service.on_unsubscribe("notifications")
async def handle_notification_unsubscribe(connection: WebSocketConnection):
    """Handle unsubscription from notifications topic"""
    logger.debug(f"Unsubscribed from notifications topic: {connection.connection_id}")
    NotificationService().remove_connection(connection)

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    userdata: dict = Depends(get_current_user(force_auth=False)),
    db: Session = Depends(get_db)
):
    """Get all unread notifications for the user (authenticated or anonymous)"""
    notification_service = NotificationService(db)
    return await notification_service.get_user_notifications(userdata["sub"])

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    userdata: dict = Depends(get_current_user(force_auth=False)),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read"""
    notification_service = NotificationService(db)
    await notification_service.mark_notifications_read(userdata["sub"], [notification_id])
    return {"status": "success", "message": "Notification marked as read"}

@router.post("/read-all")
async def mark_all_notifications_read(
    userdata: dict = Depends(get_current_user(force_auth=False)),
    db: Session = Depends(get_db)
):
    """Mark all unread notifications as read"""
    notification_service = NotificationService(db)
    # Get all unread notifications first
    notifications = await notification_service.get_user_notifications(userdata["sub"])
    notification_ids = [n.id for n in notifications]
    # Mark them all as read
    if notification_ids:
        await notification_service.mark_notifications_read(userdata["sub"], notification_ids)
    return {
        "status": "success", 
        "message": "All notifications marked as read",
        "count": len(notification_ids)
    }
