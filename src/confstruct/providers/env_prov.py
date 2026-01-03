import os

from .abc import ABCProvider


class EnvProvider(ABCProvider):
    def get_value(self, key: str) -> str:
        val = os.getenv(key.upper())
        if not val:
            raise ValueError(f"{key.upper()!r} not found in environ")
        return val
