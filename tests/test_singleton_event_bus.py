import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.database import Base
from models.event import Event
from schemas.event import EventRequest, EventType
from services.event_bus import EventBus

# Create a test database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

def test_singleton_behavior():
    # Create database sessions
    db1 = SessionLocal()
    db2 = SessionLocal()

    try:
        # Instantiate EventBus multiple times
        event_bus1 = EventBus(db1)
        event_bus2 = EventBus(db2)

        # Check if both instances are the same
        assert event_bus1 is event_bus2, "EventBus instances are not the same"

        # Register a sample event handler in the first instance
        def sample_event_handler(event: Event):
            print("Handled event:", event.payload)

        event_bus1.register_event_handler(EventType.ENDPOINT_CALL, sample_event_handler)

        # Check if the handler is available in the second instance
        handlers_for_call = event_bus2.handlers.get(EventType.ENDPOINT_CALL)
        assert handlers_for_call is not None, "Handlers for ENDPOINT_CALL not found in the second instance"
        assert sample_event_handler in handlers_for_call, "Handler not registered in the second instance"

        print("Singleton behavior test passed.")
    finally:
        db1.close()
        db2.close()

if __name__ == "__main__":
    test_singleton_behavior()
