from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Tuple

T = TypeVar('T')


class Memory(ABC, Generic[T]):
    """Base class, implement save and load for different ways to persist data"""
    @abstractmethod
    def save(self, obj: T, name: str) -> None:
        pass

    @abstractmethod
    def load(self, name: str) -> T:
        pass


class DatabaseMemory(Memory[Tuple[int, float]], ABC):
    @abstractmethod
    def _create_table(self):
        pass

    @abstractmethod
    def save(self, obj: Tuple[int, float], name: str) -> None:
        pass

    @abstractmethod
    def load(self, name: str) -> Tuple[int, float]:
        pass

