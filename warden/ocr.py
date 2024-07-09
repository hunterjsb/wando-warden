import re

import pytesseract


def extract_timestamp(image):
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
