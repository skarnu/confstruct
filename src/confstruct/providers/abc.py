from abc import ABC, abstractmethod
from typing import Any


class ABCProvider(ABC):
    @abstractmethod
    def get_value(self, key: str) -> Any | None: ...
