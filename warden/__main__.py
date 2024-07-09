import argparse
import logging
import os
import time
from typing import Union

from warden.terminal import load_terminals
from warden.memory import LocalPhotoMemory, S3PhotoMemory, MySQLMemory, PostgreSQLMemory, DynamoDBMemory, SQLiteMemory
from warden.detection import detect_trucks


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
            table_name=os.environ.get('DYNAMODB_TABLE', 'truck_detections'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Warden Camera Management')
    parser.add_argument('--terminals', default='./terminals.yaml', help='Path to terminals YAML file')
    parser.add_argument('--storage', choices=['local', 's3'], default='s3', help='Storage type (local or s3)')
    parser.add_argument('--db', choices=['sqlite', 'mysql', 'postgres', 'dynamodb'], default='dynamodb',
                        help='Database type for truck detection results')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    parser.add_argument('--detect-trucks', action='store_true', help='Perform truck detection')
    args = parser.parse_args()

    setup_logging(getattr(logging, args.log_level.upper()))
    logger = logging.getLogger(__name__)

    try:
        photo_mem = get_photo_memory(args.storage)
        db_mem = get_db_memory(args.db)
        terminals = load_terminals(args.terminals, photo_mem)

        for terminal in terminals:
            logger.info(f"Processing Terminal: {terminal.name}")
            for camera in terminal.cameras:
                try:
                    camera.get()
                    camera.save_last(with_timestamp=True)
                    logger.info(f"Processed CAMERA: {camera.full_name}_{camera.last_timestamp}")

                    if args.detect_trucks:
                        truck_count, avg_confidence = detect_trucks(camera.last_image_name,
                                                                    os.environ.get('S3_BUCKET_NAME', 'wando-warden'))
                        logger.info(f"Detected {truck_count} trucks with average confidence {avg_confidence:.2f}")
                        db_mem.save((truck_count, avg_confidence), f"{camera.full_name}|{camera.last_timestamp}")

                except Exception as e:
                    logger.error(f"Error processing camera {camera.full_name}: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
