from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ABCProvider(Protocol):
    """
    Protocol for configuration providers.

    A provider supplies key-value pairs which are later converted into a
    ``msgspec.Struct`` by the loader.
    """

    def get_value(self, key: str) -> Any | None:
        """
        Return the value associated with a key, or ``None`` if not found.
        """
        ...

    def get_values(self, keys: list[str]) -> Mapping[str, Any]:
        """
        Return values for multiple keys in a single call.

        The default implementation simply calls ``get_value`` repeatedly,
        but concrete providers can override this to provide a more efficient
        batch implementation.
        """
        return {key: self.get_value(key) for key in keys}
