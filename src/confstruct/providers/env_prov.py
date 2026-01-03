import os

from .abc import ABCProvider


class EnvProvider(ABCProvider):
    def get_value(self, key: str) -> str | None:
        return os.getenv(key.upper())
