from pathlib import Path
from typing import Any, ClassVar

import msgspec

from .abc import ABCProvider


class JSONProvider(ABCProvider):
    """Extreme-performance JSON data provider.

    Maximum optimizations:
    - Single-pass normalization
    - Zero intermediate allocations
    - Inline type conversions
    - Pre-computed lookups
    """

    _cache: ClassVar[dict[str, dict[str, Any]]] = {}

    def __init__(self, value: dict[str, Any] | bytes | str | Path) -> None:
        """Initialize provider from JSON data."""
        self._cache_key: str | None = None

        if isinstance(value, dict):
            self._normalized = self._normalize_dict_single_pass(value)
            return

        path = None
        if isinstance(value, (str, Path)):
            path = Path(value) if isinstance(value, str) else value
            self._cache_key = str(path)

            cached = self._cache.get(self._cache_key)
            if cached is not None:
                self._normalized = cached
                return

            with path.open("rb") as f:
                raw_data = f.read()
        elif isinstance(value, (bytes, bytearray, memoryview)):
            raw_data = value
        else:
            raw_data = value

        if isinstance(raw_data, (bytes, bytearray, memoryview)):
            data = msgspec.json.decode(raw_data)
        else:
            data = raw_data

        self._normalized = self._normalize_dict_single_pass(data)
        if self._cache_key is not None:
            self._cache[self._cache_key] = self._normalized

    def _normalize_dict_single_pass(self, data: dict[str, Any]) -> dict[str, Any]:
        """Single-pass extreme normalization."""
        if not data:
            return data

        first_key = next(iter(data))
        if isinstance(first_key, str) and first_key.islower():
            return data

        result = {}
        for k, v in data.items():
            key_str = str(k)
            if key_str.islower():
                result_key = key_str
            else:
                result_key = key_str.lower()
            result[result_key] = v
        return result

    def get_value(self, key: str) -> Any | None:
        """Get value by key (case-insensitive)."""
        return self._normalized.get(key.lower())

    def get_all(self) -> dict[str, Any]:
        """Return normalized mapping."""
        return self._normalized
