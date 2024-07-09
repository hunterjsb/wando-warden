from warden.memory import Memory
from warden.ocr import extract_timestamp, to_snake_case

from typing import List, Optional
import io
from datetime import datetime

import requests
from PIL import Image
from yaml import load
import pytz
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print('warning: could not load c yaml libraries')
    from yaml import Loader, Dumper


class Camera:
    """A camera stationed at a specific Terminal"""
    def __init__(self, name: str, url: str, terminal: 'Terminal', timestamp_box: tuple[int, int, int, int]):
        self.name = name
        self.url = url
        self.terminal = terminal
        self.memory = terminal.memory

        # TODO refactor this into `Frame` dataclass
        self.last_image: Optional[Image.Image] = None
        self.last_image_name = ''
        self.last_timestamp: Optional[str] = None

        self._timestamp_box = timestamp_box  # coordinates are left, upper, right, bottom (PIL crop)

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

    def save_last(self, with_timestamp=True):
        """Save the `last_image` to memory"""
        if not self.last_image:
            raise AttributeError("missing last image, cannot save")

        ts = 'latest'
        if with_timestamp:
            try:
                ts = extract_timestamp(self.timestamp_box).replace(' ', '_')
            except ValueError as e:
                print(f"ERROR {e}; using current timestamp as approx")
                est = pytz.timezone('US/Eastern')
                ts = datetime.now(est).strftime('%Y-%m-%d_%H:%M:%S_approx')
            self.last_timestamp = ts
        self.last_image_name = f"{self.full_name}_{ts}"
        self.memory.save(self.last_image, f"{self.full_name}_{ts}")


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
