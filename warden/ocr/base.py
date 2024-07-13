from abc import ABC, abstractmethod

from PIL.Image import Image


class TimestampReader(ABC):
    def __init__(self):
        self.fmt: str = '%Y-%m-%d %H:%M:%S'

    @property
    def pattern(self) -> str:
        format_map = {
            '%Y': r'\d{4}',  # Year (4 digits)
            '%y': r'\d{2}',  # Year (2 digits)
            '%m': r'\d{2}',  # Month
            '%d': r'\d{2}',  # Day
            '%H': r'\d{2}',  # Hour (24-hour format)
            '%I': r'\d{2}',  # Hour (12-hour format)
            '%M': r'\d{2}',  # Minute
            '%S': r'\d{2}'   # Second
        }

        pattern = self.fmt
        for strftime_code, regex in format_map.items():
            pattern = pattern.replace(strftime_code, regex)

        return pattern

    @abstractmethod
    def read(self, image: Image) -> str:
        pass
