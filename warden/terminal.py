from typing import List, Optional
import io
from datetime import datetime
import logging

import requests
from PIL import Image
from yaml import load
from pytesseract import TesseractNotFoundError
import pytz
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print('warning: could not load c yaml libraries')
    from yaml import Loader, Dumper

from warden.memory import Memory
from warden.ocr import TimestampReader
from warden.utils import to_snake_case


class Camera:
    """A camera stationed at a specific Terminal"""
    def __init__(self, name: str, url: str, terminal: 'Terminal', timestamp_box: tuple[int, int, int, int]):
        self.name = name
        self.url = url
        self.terminal = terminal
        self.memory = terminal.memory

        # frame
        self.last_image: Optional[Image.Image] = None
        self.last_image_name = ''
        self._timestamp_box = timestamp_box  # coordinates are left, upper, right, bottom (PIL crop)

        self.last_timestamp: Optional[int] = None  # UNIX ms timestamp
        self.last_ts_approx = False  # Did we use datetime.now() to approximate the timestamp?

    @property
    def full_name(self) -> str:
        """Snake-cased camera name that includes the port, often used for filenames"""
        return to_snake_case(self.terminal.name + ' ' + self.name)

    @property
    def timestamp_box(self):
        """The timestamp on the image, usually in the bottom-left corner"""
        return self.last_image.crop(self._timestamp_box)

    def get(self) -> Image.Image:
        """Get the most recent image from the Camera"""
        resp = requests.get(self.url)
        resp.raise_for_status()
        image = Image.open(io.BytesIO(resp.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        self.last_image = image
        return image

    def save_last(self, timestamp_reader: TimestampReader = None):
        """Save the `last_image` to memory"""
        if not self.last_image:
            raise AttributeError("missing last image, cannot save")

        self.last_ts_approx = True
        self.last_timestamp = int(datetime.now(pytz.UTC).timestamp() * 1000)
        if timestamp_reader:
            try:
                self.last_timestamp = convert_est_to_utc_timestamp(timestamp_reader.read(self.timestamp_box))
                self.last_ts_approx = False
            except (ValueError, TesseractNotFoundError) as e:
                err_str = (f"encountered an error when extracting the timestamp, "
                           f"using current timestamp as _approx: {e}")
                logging.log(logging.WARN, err_str)
        self.last_image_name = f"{self.full_name}|{self.last_timestamp}|{self.last_ts_approx}.jpg"
        self.memory.save(self.last_image, self.last_image_name)


class Terminal:
    """A Terminal, like Wando or HLT, which might have multiple cameras"""
    def __init__(self, name: str, memory: Memory):
        self.name = name
        self.cameras: List[Camera] = []
        self.memory = memory

    def add_camera(self, name: str, url: str, timestamp_box: tuple[int, int, int, int]) -> Camera:
        camera = Camera(name, url, self, timestamp_box)
        self.cameras.append(camera)
        return camera


def load_terminals(yaml_file: str, memory: Memory) -> List[Terminal]:
    """Load in the terminal configurations from a yaml file"""
    with open(yaml_file, 'r') as file:
        data = load(file, Loader)

    terminals = []
    for terminal_data in data['terminals']:
        terminal = Terminal(terminal_data['name'], memory)
        for cam in terminal_data['cameras']:
            terminal.add_camera(cam['name'], cam['url'], cam['timestamp_box'])
        terminals.append(terminal)

    return terminals


def convert_est_to_utc_timestamp(est_timestamp_str):
    est_tz = pytz.timezone('America/New_York')  # EST timezone
    est_datetime = datetime.strptime(est_timestamp_str, '%Y-%m-%d %H:%M:%S')
    est_datetime = est_tz.localize(est_datetime)  # Localize the datetime to EST
    utc_datetime = est_datetime.astimezone(pytz.UTC)  # Convert to UTC
    return int(utc_datetime.timestamp() * 1000)
