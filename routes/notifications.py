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
    userdata: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all undelivered in-app notifications for the current user.
    This includes both individual notifications and notifications sent to their groups.
    The notifications are automatically marked as delivered after being retrieved.
    """
    notification_service = NotificationService(db)
    notifications = await notification_service.get_user_notifications(userdata["sub"])
    return notifications
