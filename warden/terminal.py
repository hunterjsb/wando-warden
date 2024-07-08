from warden.utils import to_snake_case
from warden.memory import Memory, LocalPhotoMemory

from typing import List, Optional
import io

import requests
from PIL import Image
from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print('warning: could not load c yaml libraries')
    from yaml import Loader, Dumper


class Camera:
    def __init__(self, name: str, url: str, terminal: 'Terminal'):
        self.name = name
        self.url = url
        self.terminal = terminal
        self.memory = terminal.memory
        self.last_image: Optional[Image.Image] = None

    @property
    def full_name(self) -> str:
        return to_snake_case(self.terminal.name + ' ' + self.name)

    def get(self) -> Image.Image:
        resp = requests.get(self.url)
        resp.raise_for_status()
        image = Image.open(io.BytesIO(resp.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        self.last_image = image
        return image


class Terminal:
    def __init__(self, name: str, memory: Memory):
        self.name = name
        self.cameras: List[Camera] = []
        self.memory = memory

    def add_camera(self, name: str, url: str) -> Camera:
        camera = Camera(name, url, self)
        self.cameras.append(camera)
        return camera


def load_terminals(yaml_file: str, memory: Memory) -> List[Terminal]:
    with open(yaml_file, 'r') as file:
        data = load(file, Loader)

    terminals = []
    for terminal_data in data['terminals']:
        terminal = Terminal(terminal_data['name'], memory)
        for cam in terminal_data['cameras']:
            terminal.add_camera(cam['name'], cam['url'])
        terminals.append(terminal)

    return terminals
