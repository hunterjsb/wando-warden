import os
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from PIL import Image

T = TypeVar('T')


class Memory(ABC, Generic[T]):
    """Base class, implement save and load for different ways to persist data"""
    @abstractmethod
    def save(self, obj: T, name: str) -> None:
        pass

    @abstractmethod
    def load(self, name: str) -> T:
        pass


class LocalPhotoMemory(Memory[Image.Image]):
    """Save and load images to the local filesystem"""
    def __init__(self, directory: str):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def save(self, obj: Image.Image, name: str) -> None:
        if not name.lower().endswith(('.png', '.jpg', '.jpeg')):
            name += '.jpg'

        file_path = os.path.join(self.directory, name)
        obj.save(file_path)

    def load(self, name: str) -> Image.Image:
        file_path = os.path.join(self.directory, name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No file found at {file_path}")

        return Image.open(file_path)
