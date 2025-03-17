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

def test_singleton_behavior():
    # Create a new database session
    db1 = SessionLocal()
    db2 = SessionLocal()
    
    try:
        # Instantiate the MessageBus multiple times
        message_bus1 = MessageBus(db1)
        message_bus2 = MessageBus(db2)
        
        # Check if both instances are the same
        assert message_bus1 is message_bus2, "MessageBus instances are not the same"
        
        # Register a message handler in the first instance
        def sample_handler(message: Message):
            print("Handled message:", message.payload)
        
        message_bus1.register_message_handler("info", sample_handler)
        
        # Check if the handler is available in the second instance
        assert "info" in message_bus2.handlers, "Handler not found in the second instance"
        assert sample_handler in message_bus2.handlers["info"], "Handler not registered in the second instance"
        
        print("Singleton behavior test passed.")
    finally:
        db1.close()
        db2.close()

if __name__ == "__main__":
    test_singleton_behavior()