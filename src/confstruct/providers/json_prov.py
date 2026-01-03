import msgspec

from .abc import ABCProvider


class JSONProvider(ABCProvider):
    def __init__(self, value: dict[str, str] | bytes | str) -> None:
        if not isinstance(value, (bytes, str)):
            self._value = value
        else:
            self._value = msgspec.json.decode(value, type=dict[str, str])
        self.normalize()

    def normalize(self):
        results = {}
        for key, value in self._value.items():
            results[key.lower()] = value
        self._value = results

    def get_value(self, key: str) -> str | None:
        return self._value.get(key.lower())
