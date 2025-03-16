from sqlalchemy.orm import Session
from models.message import Message, RecipientType
from schemas.notification import NotificationRequest

class MessageBus:
    def __init__(self, db: Session):
        self.db = db
        self.handlers = {}

    def register_message_handler(self, type: str, callback):
        if type not in self.handlers:
            self.handlers[type] = []
        self.handlers[type].append(callback)

    def send_notification(self, notification: NotificationRequest):
        recipient_type = RecipientType(notification.recipient_type)
        new_message = Message(
            type=notification.type,
            recipient_type=recipient_type,
            recipient=notification.recipient,
            payload=notification.payload,
            priority=notification.priority
        )
        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)
        
        if notification.type in self.handlers:
            for callback in self.handlers[notification.type]:
                callback(new_message)

        return new_message

    def receive(self, message: Message):
        message.delivered = True
        self.db.commit()
        self.db.refresh(message)
        return message