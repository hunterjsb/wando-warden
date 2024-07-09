from warden.memory.base import Memory
from warden.memory.image import LocalPhotoMemory, S3PhotoMemory

try:
    from warden.memory.sql import SQLiteMemory
except ImportError:
    SQLiteMemory = None

from warden.memory.sql import MySQLMemory, PostgreSQLMemory, DynamoDBMemory
