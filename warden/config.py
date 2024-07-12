import logging
import os
from typing import Union

from warden.memory import LocalPhotoMemory, S3PhotoMemory, MySQLMemory, PostgreSQLMemory, DynamoDBMemory, SQLiteMemory


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_photo_memory(storage_type: str) -> Union[LocalPhotoMemory, S3PhotoMemory]:
    if storage_type == 'local':
        return LocalPhotoMemory(os.environ.get('LOCAL_STORAGE_PATH', './images'))
    elif storage_type == 's3':
        return S3PhotoMemory(
            bucket_name=os.environ.get('S3_BUCKET_NAME', 'wando-warden'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")


def get_db_memory(db_type: str) -> Union[SQLiteMemory, MySQLMemory, PostgreSQLMemory, DynamoDBMemory]:
    if db_type == 'sqlite':
        if SQLiteMemory.import_failed:
            raise ImportError('sqlite could not be imported')
        return SQLiteMemory(os.environ.get('SQLITE_DB_PATH', 'truck_detections.db'))
    elif db_type == 'mysql':
        return MySQLMemory(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DATABASE', 'warden')
        )
    elif db_type == 'postgres':
        return PostgreSQLMemory(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            database=os.environ.get('POSTGRES_DATABASE', 'warden')
        )
    elif db_type == 'dynamodb':
        return DynamoDBMemory(
            table_name=os.environ.get('DYNAMODB_TABLE', 'ww_truck_detections'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
