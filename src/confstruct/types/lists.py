from typing import Any, get_args, get_origin


class ListOf[T](list):
    @classmethod
    def __validate__(cls, value: Any, typ: Any) -> list[T]:
        origin = get_origin(typ) or typ
        args = get_args(typ)

        if not (origin is list or issubclass(origin, list)):
            raise TypeError(f"Expected list-like, got {typ!r}")

        t = args[0] if args else str

        if isinstance(value, str):
            parts = [p.strip() for p in value.split(",") if p.strip()]
            return cls([t(p) for p in parts])

        if isinstance(value, list):
            return cls(value)

        raise TypeError("Expected str or list")
