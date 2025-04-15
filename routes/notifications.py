from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.notifications import NotificationService
from schemas.notification import NotificationResponse
from typing import List

router = APIRouter()


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
