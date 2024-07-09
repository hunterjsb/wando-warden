# Warden Camera Management System

Warden is a Python-based camera management system designed to capture, store, and process images from multiple cameras across different terminals. It supports both local storage and Amazon S3 for image persistence.****

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/hunterjsb/wando-warden.git
   cd wando-warden
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Edit the `terminals.yaml` file to configure your terminals and cameras.

2. Set up environment variables for sensitive information:
   - For local storage: `LOCAL_STORAGE_PATH`
   - For S3 storage: `S3_BUCKET_NAME`, `AWS_REGION`

## Usage

Run the main script with the following command:

```
python -m warden --terminals path/to/terminals.yaml --storage [local|s3] --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
```

### Arguments

- `--terminals`: Path to the YAML file containing terminal configurations (default: '../terminals.yaml')
- `--storage`: Choose between 'local' or 's3' storage (default: 's3')
- `--log-level`: Set the logging level (default: 'INFO')

### Examples

1. Run with default settings (S3 storage):
   ```
   python -m warden
   ```

2. Use local storage and debug logging:
   ```
   python -m warden --storage local --log-level DEBUG
   ```

3. Specify a different terminals file:
   ```
   python -m warden --terminals /path/to/my/terminals.yaml
   ```
   
### Truck Detection

The Warden system now supports truck detection using AWS Rekognition. To use this feature:

1. Ensure you have the necessary AWS permissions to use Rekognition.
2. Set the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your AWS credentials.
3. Use the `--detect-trucks` flag when running the script:
`python -m warden --detect-trucks`
4. This will detect trucks in the captured images, count them, calculate the average confidence of the detections, and store this information in a SQLite database.

The truck detection data is stored in a SQLite database. By default, it's saved as `truck_detections.db` in the current directory. See DB options below.
   
### Database Options for Truck Detection Results

The Warden system now supports multiple database options for storing truck detection results:

1. SQLite (default)
2. MySQL
3. PostgreSQL
4. DynamoDB

To specify the database type, use the `--db` flag:
`python -m warden --detect-trucks --db [sqlite|mysql|postgres|dynamodb]`

For each database type, you need to set the following environment variables:

- SQLite:
  - `SQLITE_DB_PATH`: Path to the SQLite database file (default: `truck_detections.db`)

- MySQL:
  - `MYSQL_HOST`: MySQL server host (default: `localhost`)
  - `MYSQL_USER`: MySQL username
  - `MYSQL_PASSWORD`: MySQL password
  - `MYSQL_DATABASE`: MySQL database name (default: `warden`)

- PostgreSQL:
  - `POSTGRES_HOST`: PostgreSQL server host (default: `localhost`)
  - `POSTGRES_USER`: PostgreSQL username
  - `POSTGRES_PASSWORD`: PostgreSQL password
  - `POSTGRES_DATABASE`: PostgreSQL database name (default: `warden`)

- DynamoDB:
  - `DYNAMODB_TABLE`: DynamoDB table name (default: `truck_detections`)
  - `AWS_REGION`: AWS region for DynamoDB (default: `us-east-1`)

Make sure to install the required dependencies for the database you choose:

- MySQL: `pip install mysql-connector-python`
- PostgreSQL: `pip install psycopg2-binary`
- DynamoDB: `pip install boto3` (already required for S3 and Rekognition)

Note: For DynamoDB, ensure that you have the necessary AWS permissions and credentials set up.

## Development

To extend or modify the Warden system:

1. Add new camera types in `terminal.py`
2. Implement new storage backends in `memory.py`
3. Enhance OCR capabilities in `ocr.py`

## License

This project is licensed under MIT-0. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.