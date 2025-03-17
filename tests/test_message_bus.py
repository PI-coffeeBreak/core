import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.database import Base
from models.message import Message, RecipientType
from schemas.notification import NotificationRequest
from services.message_bus import MessageBus

# Create a test database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

def message_handler(message: Message):
    print("Message Handler Triggered")
    print(f"ID: {message.id}")
    print(f"Type: {message.type}")
    print(f"Recipient Type: {message.recipient_type}")
    print(f"Recipient: {message.recipient}")
    print(f"Payload: {message.payload}")
    print(f"Priority: {message.priority}")
    print(f"Delivered: {message.delivered}")

def main():
    # Create a new database session
    db = SessionLocal()
    
    try:
        # Instantiate the MessageBus
        message_bus = MessageBus(db)
        
        # Register the message handler
        message_bus.register_message_handler("info", message_handler)
        
        # Create a NotificationRequest
        notification = NotificationRequest(
            type="info",
            recipient_type=RecipientType.SINGLE,
            recipient=1,
            payload="This is a test message",
            priority=5
        )
        
        # Send the notification
        new_message = message_bus.send_notification(notification)
        
        # Print the new message
        print("\nNew Message:")
        print(f"ID: {new_message.id}")
        print(f"Type: {new_message.type}")
        print(f"Recipient Type: {new_message.recipient_type}")
        print(f"Recipient: {new_message.recipient}")
        print(f"Payload: {new_message.payload}")
        print(f"Priority: {new_message.priority}")
        print(f"Delivered: {new_message.delivered}")
        
        # Simulate receiving the message
        received_message = message_bus.receive(new_message)
        
        # Print the received message
        print("\nReceived Message:")
        print(f"ID: {received_message.id}")
        print(f"Type: {received_message.type}")
        print(f"Recipient Type: {received_message.recipient_type}")
        print(f"Recipient: {received_message.recipient}")
        print(f"Payload: {received_message.payload}")
        print(f"Priority: {received_message.priority}")
        print(f"Delivered: {received_message.delivered}")
    finally:
        db.close()

if __name__ == "__main__":
    main()