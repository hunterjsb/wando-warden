import re


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
