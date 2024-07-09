import re

import pytesseract
from PIL import Image


def extract_timestamp(image: Image.Image):
    """
    Takes in a cropped timestamp image and outputs the interpreted text.
    Raises a ValueError if it cannot extract a valid timestamp.
    """
    # Use psm 7 for single line of text
    custom_config = r'--oem 3 --psm 7'
    text = pytesseract.image_to_string(image, config=custom_config)

    # Use regex to find timestamp
    timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    match = re.search(timestamp_pattern, text)

    if match:
        return match.group()
    else:
        raise ValueError(f"Timestamp not found. Raw text: {text.strip()}")


def to_snake_case(name: str) -> str:
    # Convert to lowercase
    name = name.lower()
    # Replace spaces and underscores with a single underscore
    name = re.sub(r'[\s_]+', '_', name)
    # Remove any characters that are not alphanumeric or underscore
    name = re.sub(r'[^a-z0-9_]', '', name)
    # Remove leading or trailing underscores
    name = name.strip('_')
    return name
