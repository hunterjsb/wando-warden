from warden.utils import to_snake_case

from typing import List
from yaml import load, dump
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

    @property
    def full_name(self) -> str:
        return to_snake_case(self.terminal.name + ' ' + self.name)


class Terminal:
    def __init__(self, name: str):
        self.name = name
        self.cameras: List[Camera] = []

    def add_camera(self, name: str, url: str) -> Camera:
        camera = Camera(name, url, self)
        self.cameras.append(camera)
        return camera


def load_terminals(yaml_file: str) -> List[Terminal]:
    with open(yaml_file, 'r') as file:
        data = load(file, Loader)

    terminals = []
    for terminal_data in data['terminals']:
        terminal = Terminal(terminal_data['name'])
        for cam in terminal_data['cameras']:
            terminal.add_camera(cam['name'], cam['url'])
        terminals.append(terminal)

    return terminals
