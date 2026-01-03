from typing import Any, get_args


class ListOf(list):
    @classmethod
    def __validate__(cls, value: Any, typ: type):
        t = get_args(typ)[0]
        if isinstance(value, str):
            parts = [p.strip() for p in value.split(",") if p.strip()]
            return cls([t(p) for p in parts])
        if isinstance(value, list):
            return cls(value)
        raise TypeError("Expected str or list")
