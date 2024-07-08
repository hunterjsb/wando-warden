from typing import List
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print('warning: could not load c yaml libraries')
    from yaml import Loader, Dumper


class Camera:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url


class Terminal:
    def __init__(self, name: str, cameras: List[Camera]):
        self.name = name
        self.cameras = cameras


def load_terminals(yaml_file: str) -> List[Terminal]:
    with open(yaml_file, 'r') as file:
        data = load(file, Loader)

    terminals = []
    for terminal_data in data['terminals']:
        cameras = [Camera(cam['name'], cam['url']) for cam in terminal_data['cameras']]
        terminal = Terminal(terminal_data['name'], cameras)
        terminals.append(terminal)

    return terminals
