import os
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from PIL import Image

T = TypeVar('T')


class Memory(ABC, Generic[T]):
    @abstractmethod
    def save(self, obj: T, name: str) -> None:
        pass

    @abstractmethod
    def load(self, name: str) -> T:
        pass


class LocalPhotoMemory(Memory[Image.Image]):
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


# Usage example
if __name__ == "__main__":
    from PIL import Image

    # Create a sample image
    sample_image = Image.new('RGB', (100, 100), color='red')

    # Initialize the LocalPhotoMemory
    photo_memory = LocalPhotoMemory("../images")
    photo_memory.save(sample_image, "red_square")
    loaded_image = photo_memory.load("red_square.jpg")
    loaded_image.show()

    # You can also try loading a non-existent image to see the error handling
    try:
        photo_memory.load("non_existent.jpg")
    except FileNotFoundError as e:
        print(f"Error: {e}")
