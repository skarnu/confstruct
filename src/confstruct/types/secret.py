from functools import lru_cache


class SecretStr:
    """
    Lightweight secret string wrapper.

    The underlying value is stored as a plain string, but string
    representation is always masked. This type is designed to be
    extremely cheap to construct and copy.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = str(value)

    @classmethod
    @lru_cache(maxsize=128)
    def _get_validate_method(cls):
        """Cached accessor for the ``__validate__`` method.

        Used by the generic ``dec_hook`` to speed up repeated
        validations for the same type.
        """
        return cls.__validate__

    @classmethod
    def __validate__(cls, value, typ):
        """Validation hook used by ``dec_hook`` / ``msgspec``.

        Accepts:
        - Existing ``SecretStr`` (returned as-is).
        - Any value that can be converted to ``str``.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            return cls(value)
        return cls(str(value))

    def __str__(self) -> str:
        return "***"

    def __repr__(self) -> str:
        return "SecretStr('***')"

    @property
    def value(self) -> str:
        """Return the underlying secret value."""
        return self._value

    def __mspec_encode__(self) -> str:
        """Custom msgspec encoder: serializes as the underlying string."""
        return self._value

    def __mspec_copy__(self) -> SecretStr:
        """Custom msgspec copying hook used when cloning structures."""
        return self.__class__(self._value)
