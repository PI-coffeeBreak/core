from typing import List
from sqlalchemy.orm import Session
from models.activity import Activity, ActivityType
from models.activity_owner import ActivityOwner
from schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityTypeCreate
)
from services.media import MediaService
from utils.media import is_valid_url, is_valid_uuid, slugify
from uuid import uuid4
from exceptions.activity import (
    ActivityNotFoundError,
    ActivityNoImageError,
    ActivityValidationError
)
from exceptions.activity_type import (
    ActivityTypeNotFoundError,
    ActivityTypeValidationError
)
from constants.activity import MAX_NAME_LENGTH, MAX_DESCRIPTION_LENGTH
from constants.errors import ActivityErrors, ActivityTypeErrors
from constants.extensions import ImageExtension


class ActivityService:
    """Service for managing activities"""
    _instance = None
    _db = None

    def __new__(cls, db: Session = None):
        if cls._instance is None:
            cls._instance =  super(ActivityService, cls).__new__(cls)
            if db is not None:
                cls._db = db
        return cls._instance

    def __init__(self, db: Session = None):
        if db is not None:
            self._db = db

    @property
    def db(self) -> Session:
        if self._db is None:
            raise RuntimeError("Database session not initialized")
        return self._db

    # Activity type methods
    def get_activity_types(self) -> List[ActivityType]:
        """Get all activity types"""
        return self.db.query(ActivityType).all()

    def get_activity_type(self, type_id: int) -> ActivityType:
        """Get activity type by ID"""
        activity_type = self.db.query(ActivityType).filter(ActivityType.id == type_id).first()
        if not activity_type:
            raise ActivityTypeNotFoundError(type_id)
        return activity_type

    def create_activity_type(self, activity_type: ActivityTypeCreate) -> ActivityType:
        """Create a new activity type"""
        # Validate activity type data
        errors = self._validate_activity_type(activity_type)
        if errors:
            raise ActivityTypeValidationError(errors)

        db_activity_type = ActivityType(**activity_type.model_dump())
        self.db.add(db_activity_type)
        self.db.commit()
        self.db.refresh(db_activity_type)
        return db_activity_type

    def update_activity_type(self, type_id: int, activity_type: ActivityTypeCreate) -> ActivityType:
        """Update an existing activity type"""
        db_activity_type = self.get_activity_type(type_id)

        # Validate activity type data
        errors = self._validate_activity_type(activity_type)
        if errors:
            raise ActivityTypeValidationError(errors)

        for key, value in activity_type.model_dump().items():
            setattr(db_activity_type, key, value)

        self.db.commit()
        self.db.refresh(db_activity_type)
        return db_activity_type

    def delete_activity_type(self, type_id: int) -> None:
        """Delete an activity type"""
        db_activity_type = self.get_activity_type(type_id)
        self.db.delete(db_activity_type)
        self.db.commit()

    def _validate_activity_type(self, activity_type: ActivityTypeCreate) -> List[str]:
        """Validate activity type data"""
        errors = []
        
        if not activity_type.type:
            errors.append(ActivityTypeErrors.NAME_REQUIRED)
        elif len(activity_type.type) > MAX_NAME_LENGTH:
            errors.append(ActivityTypeErrors.NAME_TOO_LONG.format(max_length=MAX_NAME_LENGTH))

        return errors

    def get_all(self) -> List[Activity]:
        """Get all activities"""
        return self.db.query(Activity).all()

    def get_by_id(self, activity_id: int) -> Activity:
        """Get activity by ID"""
        activity = self.db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            raise ActivityNotFoundError(activity_id)
        return activity

    def _create_single_activity(self, activity: ActivityCreate) -> Activity:
        """Create a single activity with image handling"""
        # Validate activity data
        errors = self._validate_activity(activity)
        if errors:
            raise ActivityValidationError(errors)

        # Handle image
        image = activity.image
        if not image or not is_valid_url(image):
            media = MediaService.register(
                db=self.db,
                max_size=ImageExtension.MAX_SIZE,
                allows_rewrite=True,
                valid_extensions=ImageExtension.ALLOWED,
                alias=f"{slugify(activity.name)}-{uuid4()}"
            )
            image = media.uuid

        db_activity = Activity(**activity.model_dump(exclude={"image"}), image=image)
        self.db.add(db_activity)
        return db_activity

    def create(self, activity: ActivityCreate) -> Activity:
        """Create a new activity"""
        db_activity = self._create_single_activity(activity)
        self.db.commit()
        self.db.refresh(db_activity)
        return db_activity

    def create_many(self, activities: List[ActivityCreate]) -> List[Activity]:
        """Create multiple activities"""
        db_activities = []
        for activity in activities:
            db_activity = self._create_single_activity(activity)
            db_activities.append(db_activity)

        self.db.commit()
        for activity in db_activities:
            self.db.refresh(activity)
        return db_activities

    def update(self, activity_id: int, activity: ActivityUpdate) -> Activity:
        """Update an existing activity"""
        db_activity = self.get_by_id(activity_id)

        # Validate activity data
        errors = self._validate_activity(activity)
        if errors:
            raise ActivityValidationError(errors)

        update_data = activity.model_dump(exclude_unset=True)
        new_image = update_data.get("image")

        if new_image:
            if is_valid_uuid(db_activity.image) and is_valid_url(new_image):
                MediaService.unregister(self.db, db_activity.image, force=True)
            elif is_valid_uuid(db_activity.image) and not is_valid_url(new_image):
                update_data.pop("image", None)
            elif is_valid_url(db_activity.image) and not is_valid_url(new_image):
                media = MediaService.register(
                    db=self.db,
                    max_size=ImageExtension.MAX_SIZE,
                    allows_rewrite=True,
                    valid_extensions=ImageExtension.ALLOWED,
                    alias=f"{slugify(db_activity.name)}-{uuid4()}"
                )
                update_data["image"] = media.uuid

        for key, value in update_data.items():
            setattr(db_activity, key, value)

        self.db.commit()
        self.db.refresh(db_activity)
        return db_activity

    def delete(self, activity_id: int) -> None:
        """Delete an activity"""
        db_activity = self.get_by_id(activity_id)

        if is_valid_uuid(db_activity.image):
            MediaService.unregister(self.db, db_activity.image, force=True)

        self.db.delete(db_activity)
        self.db.commit()

    def remove_image(self, activity_id: int) -> Activity:
        """Remove activity image"""
        db_activity = self.get_by_id(activity_id)

        if not db_activity.image:
            raise ActivityNoImageError(activity_id)

        if is_valid_uuid(db_activity.image):
            MediaService.unregister(self.db, db_activity.image, force=True)
        elif not is_valid_url(db_activity.image):
            raise ActivityNoImageError(activity_id)

        db_activity.image = None
        self.db.commit()
        self.db.refresh(db_activity)
        return db_activity

    def _validate_activity(self, activity: ActivityCreate | ActivityUpdate) -> List[str]:
        """Validate activity data"""
        errors = []
        
        if not activity.name:
            errors.append(ActivityErrors.NAME_REQUIRED)
        elif len(activity.name) > MAX_NAME_LENGTH:
            errors.append(ActivityErrors.NAME_TOO_LONG.format(max_length=MAX_NAME_LENGTH))

        if activity.description and len(activity.description) > MAX_DESCRIPTION_LENGTH:
            errors.append(ActivityErrors.DESCRIPTION_TOO_LONG.format(max_length=MAX_DESCRIPTION_LENGTH))

        if activity.date and activity.duration and activity.date.timestamp() + activity.duration * 60 <= activity.date.timestamp():
            errors.append(ActivityErrors.START_TIME_AFTER_END)

        return errors

    def add_owner(self, activity_id: int, user_id: str) -> ActivityOwner:
        """Add an owner to an activity"""
        activity = self.get_by_id(activity_id)
        
        # Check if owner already exists
        existing_owner = self.db.query(ActivityOwner).filter(
            ActivityOwner.activity_id == activity_id,
            ActivityOwner.user_id == user_id
        ).first()
        
        if existing_owner:
            return existing_owner
            
        owner = ActivityOwner(activity_id=activity_id, user_id=user_id)
        self.db.add(owner)
        self.db.commit()
        self.db.refresh(owner)
        return owner

    def remove_owner(self, activity_id: int, user_id: str) -> ActivityOwner:
        """Remove an owner from an activity"""
        owner = self.db.query(ActivityOwner).filter(
            ActivityOwner.activity_id == activity_id,
            ActivityOwner.user_id == user_id
        ).first()
        
        if not owner:
            raise ActivityNotFoundError(activity_id)
            
        self.db.delete(owner)
        self.db.commit()
        return owner

    def get_owners(self, activity_id: int) -> List[ActivityOwner]:
        """Get all owners of an activity"""
        activity = self.get_by_id(activity_id)
        return self.db.query(ActivityOwner).filter(ActivityOwner.activity_id == activity_id).all() 