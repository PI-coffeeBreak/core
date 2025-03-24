from sqlalchemy.orm import Session
from models.message import Message, RecipientType
from schemas.notification import NotificationRequest

class MessageBus:
    _instance = None

    def __new__(cls, db: Session = None):
        if cls._instance is None:
            cls._instance = super(MessageBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db: Session = None):
        if self._initialized:
            return
        self.db = db
        self.handlers = {}
        self._initialized = True

    def register_message_handler(self, type: str, callback):
        if type not in self.handlers:
            self.handlers[type] = []
        self.handlers[type].append(callback)
    
    def unregister_message_handler(self, type: str, callback):
        if type in self.handlers:
            self.handlers[type].remove(callback)

    def send_notification(self, notification: NotificationRequest):
        if self.db is None:
            raise ValueError("MessageBus not initialized with a database session")
        
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
        if self.db is None:
            raise ValueError("MessageBus not initialized with a database session")

        message.delivered = True
        self.db.commit()
        self.db.refresh(message)
        return message