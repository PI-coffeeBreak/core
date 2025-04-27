import hashlib
import uuid
import os
from typing import Optional, List, BinaryIO, Type
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from models.media import Media
from repository.media import BaseMediaRepo
from dependencies.auth import get_current_user
from constants.errors import MediaErrors
from exceptions.media import (
    MediaError,
    MediaNotFoundError,
    MediaAlreadyExistsError,
    MediaFileTooLargeError,
    MediaInvalidExtensionError,
    MediaNoExtensionError,
    MediaRequiresOpError,
    MediaNoRewriteError,
    MediaNoDeleteError,
    MediaHasFileError
)


class MediaService:
    """
    Service for managing media files
    """
    _repository: Optional[Type[BaseMediaRepo]] = None

    @classmethod
    def set_repository(cls, repository_factory):
        """Set the repository factory to be used by the service"""
        cls._repository = repository_factory()

    @classmethod
    def _get_repository(cls) -> BaseMediaRepo:
        """Get repository instance, raising error if not configured"""
        if cls._repository is None:
            raise RuntimeError("Media repository not configured")
        return cls._repository

    @staticmethod
    def _compute_hash(data: BinaryIO) -> str:
        """Compute SHA-256 hash of file data"""
        sha256 = hashlib.sha256()
        for chunk in iter(lambda: data.read(4096), b''):
            sha256.update(chunk)
        data.seek(0)  # Reset file pointer
        return sha256.hexdigest()

    @staticmethod
    def _validate_file(media: Media, file: BinaryIO, filename: str) -> None:
        """
        Validate file size and extension

        Args:
            media: Media entity with validation rules
            file: File data to validate
            filename: Original filename to check extension

        Raises:
            HTTPException: If validation fails
        """
        # Validate file size if max_size is set
        if media.max_size:
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(0)  # Reset pointer
            if size > media.max_size:
                raise MediaFileTooLargeError(media.max_size)

        # Validate extension if valid_extensions is set
        if media.valid_extensions:
            _, ext = os.path.splitext(filename)
            if not ext:
                raise MediaNoExtensionError()
            if ext.lower() not in [ext.lower() for ext in media.valid_extensions]:
                raise MediaInvalidExtensionError(media.valid_extensions)

    @classmethod
    def register(
        cls,
        db: Session,
        max_size: Optional[int] = None,
        allows_rewrite: bool = True,
        valid_extensions: List[str] = None,
        alias: Optional[str] = None
    ) -> Media:
        """
        Not called by any endpoint. Should be called where needed.
        Register a new media entity, i.e., only the metadata, not the file itself.

        Args:
            db: Database session
            max_size: Maximum allowed file size in bytes
            allows_rewrite: Whether file can be replaced
            valid_extensions: List of allowed file extensions (e.g. ['.jpg', '.png'])
            alias: Optional alias for the media

        Returns:
            Created Media entity
        """
        media = Media(
            uuid=str(uuid.uuid4()),
            max_size=max_size,
            hash=None,
            alias=alias,
            valid_extensions=valid_extensions or [],
            allow_rewrite=allows_rewrite
        )
        db.add(media)
        db.commit()
        db.refresh(media)
        return media

    @classmethod
    def create(cls, db: Session, uuid: str, data: BinaryIO, filename: str, user: Optional[dict] = None) -> Media:
        """
        Create the new media file itself and save it to the repository.

        Args:
            db: Database session
            uuid: Media UUID
            data: File data
            filename: Original filename for extension validation
            user: Optional user info for authorization

        Returns:
            Updated Media entity

        Raises:
            HTTPException: If validation fails
        """
        media = db.query(Media).filter(Media.uuid == uuid).first()
        if not media:
            raise MediaNotFoundError()

        if media.hash is not None:
            raise MediaAlreadyExistsError()

        if media.op_required and (not user or 'media_op' not in user.get('roles', [])):
            raise MediaRequiresOpError()

        # Validate file size and extension
        cls._validate_file(media, data, filename)

        # Set alias as filename if not already set
        if not media.alias:
            media.alias = filename

        # Compute and save hash
        file_hash = cls._compute_hash(data)
        media.hash = file_hash

        try:
            # Save file first
            cls._get_repository().save(file_hash, data)

            try:
                # Then try to commit database changes
                db.commit()
                return media
            except Exception as db_error:
                # If database commit fails, remove the saved file
                try:
                    cls._get_repository().remove(file_hash)
                except Exception:
                    pass  # Ignore cleanup errors
                db.rollback()
                raise db_error
        except Exception as e:
            db.rollback()
            raise MediaError(str(e), 500)

    @classmethod
    def read(cls, db: Session, uuid: str) -> tuple[Media, BinaryIO]:
        """
        Read media file

        Args:
            db: Database session
            uuid: Media UUID

        Returns:
            Tuple of (Media entity, file data)

        Raises:
            HTTPException: If media not found or has no data
        """
        media = db.query(Media).filter(Media.uuid == uuid).first()
        if not media or not media.hash:
            raise MediaNotFoundError()

        try:
            data = cls._get_repository().read(media.hash)
            return media, data
        except FileNotFoundError:
            raise MediaNotFoundError()
        except Exception as e:
            raise MediaError(str(e), 500)

    @classmethod
    def create_or_replace(cls, db: Session, uuid: str, data: BinaryIO, filename: str, user: Optional[dict] = None) -> Media:
        """
        Create or replace the media file itself and save it to the repository.
        Similar to create, but allows replacing existing files.

        Args:
            db: Database session
            uuid: Media UUID
            data: New file data
            filename: Original filename for extension validation
            user: Optional user info for authorization

        Returns:
            Updated Media entity

        Raises:
            HTTPException: If validation fails
        """
        media = db.query(Media).filter(Media.uuid == uuid).first()
        if not media:
            raise MediaNotFoundError()

        if not media.allow_rewrite:
            raise MediaNoRewriteError()

        if media.op_required and (not user or 'media_op' not in user.get('roles', [])):
            raise MediaRequiresOpError()

        # Validate file size and extension
        cls._validate_file(media, data, filename)

        # Set alias as filename if not already set
        if not media.alias:
            media.alias = filename

        # Store old state for rollback
        old_hash = media.hash

        # Compute new hash
        new_hash = cls._compute_hash(data)
        media.hash = new_hash

        try:
            # Save new file first
            cls._get_repository().save(new_hash, data)

            try:
                # Try to commit database changes
                db.commit()

                # If successful, remove old file if it exists
                if old_hash:
                    try:
                        cls._get_repository().remove(old_hash)
                    except FileNotFoundError:
                        pass  # Ignore if old file doesn't exist

                return media
            except Exception as db_error:
                # If database commit fails:
                # 1. Remove the new file
                try:
                    cls._get_repository().remove(new_hash)
                except Exception:
                    pass  # Ignore cleanup errors

                # 2. Restore database state
                db.rollback()
                raise db_error
        except Exception as e:
            # Restore database state
            db.rollback()
            raise MediaError(str(e), 500)

    @classmethod
    def remove(cls, db: Session, uuid: str, user: Optional[dict] = None) -> None:
        """
        Remove the media file itself from the repository.
        This does not delete the media entity from the database.

        Args:
            db: Database session
            uuid: Media UUID
            user: Optional user info for authorization

        Raises:
            HTTPException: If validation fails
        """
        media = db.query(Media).filter(Media.uuid == uuid).first()
        if not media:
            raise MediaNotFoundError()

        if not media.allow_rewrite:
            raise MediaNoDeleteError()

        if media.op_required and (not user or 'media_op' not in user.get('roles', [])):
            raise MediaRequiresOpError()

        if media.hash:
            try:
                cls._get_repository().remove(media.hash)
                media.hash = None
                db.commit()
            except FileNotFoundError:
                pass  # Ignore if file doesn't exist
            except Exception as e:
                db.rollback()
                raise MediaError(str(e), 500)

    @classmethod
    def unregister(cls, db: Session, uuid: str, force: bool = False) -> None:
        """
        Also not available in an endpoint. Should be called where needed.
        Unregister a media entity from the database and its file if it exists, i.e., delete the metadata and the file itself.

        Args:
            db: Database session
            uuid: Media UUID
            force: Whether to force deletion even if file exists

        Raises:
            HTTPException: If validation fails
        """
        media = db.query(Media).filter(Media.uuid == uuid).first()
        if not media:
            raise MediaNotFoundError()

        if media.hash and not force:
            raise MediaHasFileError()

        try:
            if media.hash:
                try:
                    cls._get_repository().remove(media.hash)
                except FileNotFoundError:
                    pass  # Ignore if file doesn't exist

            db.delete(media)
            db.commit()
        except Exception as e:
            db.rollback()
            raise MediaError(str(e), 500)
