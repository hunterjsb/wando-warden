import argparse
import logging
import os

from warden.terminal import load_terminals
from warden.detection import detect_trucks
from warden.config import setup_logging, get_photo_memory, get_db_memory


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

    photo_mem = get_photo_memory(args.storage)
    db_mem = get_db_memory(args.db)
    terminals = load_terminals(args.terminals, photo_mem)

    for terminal in terminals:
        logger.info(f"Processing Terminal: {terminal.name}")
        for camera in terminal.cameras:
            camera.get()
            camera.save_last(with_timestamp=True)
            logger.info(f"Processed CAMERA: {camera.full_name}_{camera.last_timestamp}")

            if args.detect_trucks:
                truck_count, avg_confidence = detect_trucks(camera.last_image_name,
                                                            os.environ.get('S3_BUCKET_NAME', 'wando-warden'))
                logger.info(f"Detected {truck_count} trucks with average confidence {avg_confidence:.2f}")
                db_mem.save((truck_count, avg_confidence), f"{camera.full_name}|{camera.last_timestamp}|"
                                                           f"{camera.last_ts_approx}")


if __name__ == "__main__":
    main()
