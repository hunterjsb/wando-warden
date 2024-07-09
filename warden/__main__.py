import re

from warden.terminal import load_terminals
from warden.memory import LocalPhotoMemory

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
        return f"Timestamp not found. Raw text: {text.strip()}"


mem = LocalPhotoMemory("../images")
terminals = load_terminals('../terminals.yaml', mem)
for terminal in terminals:
    print(f"Terminal: {terminal.name}")
    for camera in terminal.cameras:
        camera.get()
        print(f"CAMERA {camera.full_name}; ts {extract_timestamp(camera.timestamp_box)}\n")
