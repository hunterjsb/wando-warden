import re


def to_snake_case(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[\s_]+', '_', name)
    name = re.sub(r'[^a-z0-9_]', '', name)
    name = name.strip('_')
    return name
