# Warden Terminal Camera Truck Detection

wando-warden can watch terminal cameras (such as those at Wando Welch), read the timestamp from the image, and count the number of trucks.

![wando-maingate](https://github.com/hunterjsb/wando-warden/assets/69213737/9e76295c-f2f1-4e44-8978-61d2d6dfbbe1)


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

2. Set up environment variables for sensitive information. See .env.example.

## Usage

Run the streamlit app dashboard with:
```commandline
streamlit run app.py
```

Run the main script with the following command:

```commandline
python -m warden --detect-trucks
```

### Arguments

- `--terminals`: Path to the YAML file containing terminal configurations (default: '../terminals.yaml')
- `--storage`: Choose between 'local' or 's3' storage (default: 's3')
- `--log-level`: Set the logging level (default: 'INFO')
- `--db`: Database to store object detection results (default: ')

### CLI Examples

1. Run with default settings (S3 for photos, DynamoDB for results):
   ```
   python -m warden
   ```

2. Use local photo storage and debug logging:
   ```
   python -m warden --storage local --log-level DEBUG
   ```

3. Detect trucks and store the results in a postgresql db:
   ```
   python -m warden --db postgres --detect-trucks
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

For each database type, you need to set the appropriate environment variables, the names are found in .env.example.

Note: For DynamoDB, ensure that you have the necessary AWS permissions and credentials set up.

## Development

To extend or modify the Warden system:

1. Add new camera types in `terminal.py`
2. Implement new storage backends in `memory.py`
3. Enhance OCR capabilities in `ocr.py`
4. Adjust labels and object detection settings in `detection.py`
5. Edit default configuration values in `config.py`

## License

This project is licensed under MIT-0. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.
