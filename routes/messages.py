from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from models.message import Message
from schemas.notification import NotificationRequest
from services.message_bus import MessageBus

router = APIRouter()

@router.post("/", response_model=NotificationRequest)
def create_message(notification: NotificationRequest, db: Session = Depends(get_db)):
    message_bus = MessageBus(db)
    new_message = message_bus.send_notification(notification)
    return new_message

@router.get("/{message_id}", response_model=NotificationRequest)
def get_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message