import json
from typing import Any, TypeVar, get_args

T = TypeVar("T")


class ListOf[T]:
    """
    Lightweight list-like type with flexible parsing rules.

    ``ListOf[T]`` is primarily intended for configuration values coming from
    environment variables or JSON:

    - Accepts real Python lists.
    - Accepts JSON-style list strings (``"[1, 2, 3]"``).
    - Accepts comma-separated strings (``"1,2,3"``).
    """

    __slots__ = ("_inner_type", "_type_str")

    def __init__(self, inner_type: type[T]) -> None:
        self._inner_type = inner_type
        self._type_str = str(inner_type)

    def _get_converter(self, value_type: type) -> callable:  # pyright: ignore[reportGeneralTypeIssues]
        """Return a fast converter for simple value types."""
        if value_type in (int, str, float, bool):
            return value_type
        return lambda x: x

    @classmethod
    def __validate__(cls, value: Any, typ: Any):  # noqa: C901
        """Validation hook used by ``dec_hook`` / ``msgspec``.

        Attempts to coerce the input into a ``list[T]`` according to the
        rules described in the class docstring.
        """
        if isinstance(value, list):
            args = get_args(typ)
            if args:
                inner_type = args[0]

                if inner_type in (int, str, float, bool):
                    try:
                        return [inner_type(item) for item in value]
                    except (TypeError, ValueError):
                        pass
            return value

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
                            return [inner_type(item) for item in items]
                        except (TypeError, ValueError):
                            pass
                return items

        return value

    @classmethod
    def __mspec_decode__(cls, value: Any, typ: Any):
        """Hook used by ``msgspec`` for custom decoding."""
        return cls.__validate__(value, typ)
