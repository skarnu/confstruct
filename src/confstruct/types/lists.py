from typing import Any


class ListOf(list):
    __item_type__: type

    def __class_getitem__(cls, item_type: type):  # pyright: ignore[reportIncompatibleMethodOverride]
        name = f"{cls.__name__}[{getattr(item_type, '__name__', str(item_type))}]"
        return type(name, (cls,), {"__item_type__": item_type})

    @classmethod
    def __validate__(cls, value: Any):
        if isinstance(value, str):
            parts = []
            t = cls.__item_type__
            for p in value.split(","):
                p = p.strip()
                if not p:
                    continue
                parts.append(t(p))
            return cls(parts)
        if isinstance(value, list):
            return cls(value)
        raise TypeError("Expected str or list")
