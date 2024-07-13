import re

import pytesseract
from PIL import Image

from .base import TimestampReader


class Tesseract(TimestampReader):
    def __init__(self):
        super().__init__()

    def read(self, image: Image) -> str:
        """
        Takes in a cropped timestamp image and outputs the interpreted text.
        Raises a ValueError if it cannot extract a valid timestamp.
        """
        # Use psm 7 for single line of text
        custom_config = r'--oem 3 --psm 7'
        text = pytesseract.image_to_string(image, config=custom_config)

        # Use regex to find timestamp
        match = re.search(self.pattern, text)

        if match:
            return match.group()
        else:
            raise ValueError(f"Timestamp not found. Raw text: {text.strip()}")

