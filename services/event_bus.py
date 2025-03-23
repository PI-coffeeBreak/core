from sqlalchemy.orm import Session
from typing import Callable, Dict, List
from datetime import datetime
from models.event import Event  # Model Event in the database
from schemas.event import EventRequest, EventType

class EventBus:
    _instance = None

    def __new__(cls, db: Session):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db: Session):
        if self._initialized:
            return
        self.db = db
        self.handlers: Dict[str, List[Callable]] = {}  # Handlers for different event types
        self._initialized = True

    def register_event_handler(self, event_type: EventType, callback: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(callback)

    def _save_event(self, event: EventRequest):
        # Create event log and persist in the DB
        new_event = Event(
            event_type=event.event_type,
            timestamp=event.timestamp,
            payload=event.payload,
            details=event.details
        )
        self.db.add(new_event)
        self.db.commit()
        self.db.refresh(new_event)
        return new_event

    def publish_event(self, event: EventRequest):
        # Persist event
        event_record = self._save_event(event)
        
        # Call the registered handlers
        if event.event_type in self.handlers:
            for callback in self.handlers[event.event_type]:
                callback(event_record)

        return event_record

    def get_event(self, event_id: str):
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception(f"Event with id {event_id} not found.")
        return event
