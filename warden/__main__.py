import argparse
import logging
import os
from typing import Union

from warden.terminal import load_terminals
from warden.memory import LocalPhotoMemory, S3PhotoMemory


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_memory(storage_type: str) -> Union[LocalPhotoMemory, S3PhotoMemory]:
    if storage_type == 'local':
        return LocalPhotoMemory(os.environ.get('LOCAL_STORAGE_PATH', '../images'))
    elif storage_type == 's3':
        return S3PhotoMemory(
            bucket_name=os.environ.get('S3_BUCKET_NAME', 'wando-warden'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")


def main() -> None:
    parser = argparse.ArgumentParser(description='Warden Camera Management')
    parser.add_argument('--terminals', default='../terminals.yaml', help='Path to terminals YAML file')
    parser.add_argument('--storage', choices=['local', 's3'], default='s3', help='Storage type (local or s3)')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    args = parser.parse_args()

    setup_logging(getattr(logging, args.log_level.upper()))
    logger = logging.getLogger(__name__)

    try:
        mem = get_memory(args.storage)
        terminals = load_terminals(args.terminals, mem)

        for terminal in terminals:
            logger.info(f"Processing Terminal: {terminal.name}")
            for camera in terminal.cameras:
                try:
                    camera.get()
                    camera.save_last(with_timestamp=True)
                    logger.info(f"Processed CAMERA: {camera.full_name} @ {camera.last_timestamp}")
                except Exception as e:
                    logger.error(f"Error processing camera {camera.full_name}: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
