import json
from typing import Any, TypeVar, get_args

T = TypeVar("T")


class ListOf(list):
    """
    Lightweight list-like type with flexible parsing rules.

    ``ListOf[T]`` is primarily intended for configuration values coming from
    environment variables or JSON:

    - Accepts real Python lists.
    - Accepts JSON-style list strings (``"[1, 2, 3]"``).
    - Accepts comma-separated strings (``"1,2,3"``).
    """

    def __class_getitem__(cls, item):
        """Support for generic syntax ListOf[T]."""
        return cls

    @classmethod
    def __validate__(cls, value: Any, typ: Any):  # noqa: C901
        """Validation hook used by ``dec_hook`` / ``msgspec``.

        Attempts to coerce the input into a ``ListOf[T]`` according to the
        rules described in the class docstring.
        """
        if isinstance(value, cls):
            # Already a ListOf, return as-is
            return value
            
        if isinstance(value, list):
            args = get_args(typ)
            converted = []
            if args:
                inner_type = args[0]

                if inner_type in (int, str, float, bool):
                    try:
                        converted = [inner_type(item) for item in value]
                    except (TypeError, ValueError):
                        converted = value
                else:
                    converted = value
            else:
                converted = value
            
            return cls(converted)

        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return cls.__validate__(parsed, typ)
                except json.JSONDecodeError:
                    pass

            items = [item.strip() for item in value.split(",") if item.strip()]
            if items:
                args = get_args(typ)
                if args:
                    inner_type = args[0]
                    if inner_type in (int, str):
                        try:
                            return cls([inner_type(item) for item in items])
                        except (TypeError, ValueError):
                            pass
                return cls(items)

        return cls(value) if isinstance(value, list) else value

    @classmethod
    def __mspec_decode__(cls, value: Any, typ: Any):
        """Hook used by ``msgspec`` for custom decoding."""
        return cls.__validate__(value, typ)
