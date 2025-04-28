from abc import ABC, abstractmethod
import os
import shutil
from typing import BinaryIO
from constants.local_media_repo import MEDIA_REPO_PATH, MEDIA_SYMBOLS_PER_LEVEL, MEDIA_TREE_DEPTH


class BaseMediaRepo(ABC):
    """
    Abstract base class for media repositories
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @abstractmethod
    def save(self, hash: str, data: BinaryIO) -> None:
        """Save media data with given hash"""
        pass

    @abstractmethod
    def read(self, hash: str) -> BinaryIO:
        """Read media data for given hash"""
        pass

    @abstractmethod
    def remove(self, hash: str) -> None:
        """Remove media data for given hash"""
        pass


class LocalMediaRepo(BaseMediaRepo):
    """
    Local filesystem implementation of media repository
    """

    def __init__(self, root_path: str):
        self.root_path = root_path
        os.makedirs(root_path, exist_ok=True)

    def _get_dirs_from_hash(self, hash: str) -> list[str]:
        """Get directory structure from hash"""
        dirs = []
        for i in range(0, MEDIA_TREE_DEPTH * MEDIA_SYMBOLS_PER_LEVEL, MEDIA_SYMBOLS_PER_LEVEL):
            dirs.append(hash[i:i+MEDIA_SYMBOLS_PER_LEVEL])
        return dirs

    def _get_file_path(self, hash: str) -> str:
        """Get the full path for a file based on its hash"""
        dirs = self._get_dirs_from_hash(hash)
        return os.path.join(self.root_path, *dirs, hash)

    def _ensure_dir_exists(self, hash: str) -> None:
        """Ensure the directory structure exists for given hash"""
        dirs = self._get_dirs_from_hash(hash)
        os.makedirs(os.path.join(self.root_path, *dirs), exist_ok=True)

    def save(self, hash: str, data: BinaryIO) -> None:
        """
        Save media data to local filesystem

        Args:
            hash: File hash to use as identifier
            data: File-like object containing the data to save
        """
        self._ensure_dir_exists(hash)
        file_path = self._get_file_path(hash)

        with open(file_path, 'wb') as f:
            shutil.copyfileobj(data, f)

    def read(self, hash: str) -> BinaryIO:
        """
        Read media data from local filesystem

        Args:
            hash: File hash to read

        Returns:
            File-like object containing the media data

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self._get_file_path(hash)
        return open(file_path, 'rb')

    def remove(self, hash: str) -> None:
        """
        Remove media data from local filesystem

        Args:
            hash: File hash to remove

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self._get_file_path(hash)
        os.remove(file_path)
