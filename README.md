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