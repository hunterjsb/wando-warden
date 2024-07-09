import os
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional
from io import BytesIO

from PIL import Image
import boto3
from botocore.exceptions import ClientError

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


class S3PhotoMemory(Memory[Image.Image]):
    """Save and load images to/from Amazon S3"""
    def __init__(self, bucket_name: str, aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None, region_name: Optional[str] = None):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3',
                               aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key,
                               region_name=region_name)

    def save(self, obj: Image.Image, name: str) -> None:
        if not name.lower().endswith(('.png', '.jpg', '.jpeg')):
            name += '.jpg'

        # Convert image to bytes
        buffer = BytesIO()
        obj.save(buffer, format='JPEG')
        buffer.seek(0)

        # Upload to S3
        try:
            self.s3.upload_fileobj(buffer, self.bucket_name, name)
        except ClientError as e:
            print(f"An error occurred while uploading to S3: {e}")
            raise

    def load(self, name: str) -> Image.Image:
        buffer = BytesIO()
        try:
            self.s3.download_fileobj(self.bucket_name, name, buffer)
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                raise FileNotFoundError(f"The object {name} does not exist in bucket {self.bucket_name}")
            else:
                print(f"An error occurred while downloading from S3: {e}")
                raise

        buffer.seek(0)
        return Image.open(buffer)
