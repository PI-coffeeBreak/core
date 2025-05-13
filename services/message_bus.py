from sqlalchemy.orm import Session
from models.message import Message, RecipientType
from schemas.notification import NotificationRequest
from exceptions.message import MessageNotInitializedError, MessageInvalidRecipientTypeError
import asyncio


class MessageBus:
    _instance = None
    _handlers = {}

    def __new__(cls, db: Session = None):
        if cls._instance is None:
            cls._instance = super(MessageBus, cls).__new__(cls)
        return cls._instance

    def __init__(self, db: Session = None):
        self.db = db
        # handlers são compartilhados entre todas as instâncias
        self.handlers = self._handlers

    async def register_message_handler(self, type: str, callback):
        if type not in self.handlers:
            self.handlers[type] = []
        self.handlers[type].append(callback)

    async def unregister_message_handler(self, type: str, callback):
        if type in self.handlers:
            self.handlers[type].remove(callback)

    async def send_notification(self, notification: NotificationRequest):
        if self.db is None:
            raise MessageNotInitializedError()

        try:
            recipient_type = RecipientType(notification.recipient_type)
        except ValueError:
            raise MessageInvalidRecipientTypeError(notification.recipient_type)

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
                if asyncio.iscoroutinefunction(callback):
                    await callback(notification)
                else:
                    callback(notification)

        return new_message

    async def receive(self, message: Message):
        if self.db is None:
            raise MessageNotInitializedError()

        message.delivered = True
        self.db.commit()
        self.db.refresh(message)
        return message
