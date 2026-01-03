from abc import ABC, abstractmethod


class ABCProvider(ABC):
    @abstractmethod
    def get_value(self, key: str) -> str: ...
