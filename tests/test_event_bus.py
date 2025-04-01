import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependencies.database import Base
from models.event import Event  # Example: your SQLAlchemy model for events
from schemas.event import EventRequest, EventType
from services.event_bus import EventBus

# Create a test database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

def sample_event_handler(event: Event):
    """
    Sample handler to be triggered when an event of a certain type is published.
    """
    print("Event Handler Triggered")
    print(f"ID: {event.id}")
    print(f"Event Type: {event.event_type}")
    print(f"Timestamp: {event.timestamp}")
    print(f"Payload: {event.payload}")
    print(f"Details: {event.details}")

def main():
    db = SessionLocal()

    try:
        event_bus = EventBus(db)
        event_bus.register_event_handler(EventType.ENDPOINT_CALL, sample_event_handler)

        event_request = EventRequest(
            event_type=EventType.ENDPOINT_CALL,
            timestamp="2025-03-22T00:00:00",
            payload="GET /api/data",
            details={"calls_count": 1, "avg_response_time": 150}
        )

        new_event = event_bus.publish_event(event_request)

        print("\nNew Event Published:")
        print(f"ID: {new_event.id}")
        print(f"Event Type: {new_event.event_type}")
        print(f"Payload: {new_event.payload}")
        print(f"Details: {new_event.details}")

        fetched_event = event_bus.get_event(new_event.id)

        print("\nFetched Event via get_event():")
        print(f"ID: {fetched_event.id}")
        print(f"Event Type: {fetched_event.event_type}")
        print(f"Payload: {fetched_event.payload}")
        print(f"Details: {fetched_event.details}")

        # ✅ Assertions to verify consistency
        assert fetched_event.id == new_event.id, "Event ID mismatch"
        assert fetched_event.event_type == new_event.event_type, "Event type mismatch"
        assert fetched_event.payload == new_event.payload, "Payload mismatch"
        assert fetched_event.details == new_event.details, "Details mismatch"

        print("\n✅ Event successfully stored and retrieved — data matches.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
