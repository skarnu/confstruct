import os
from typing import ClassVar

from .abc import ABCProvider


class EnvProvider(ABCProvider):
    """
    High-performance environment variable provider with caching.

    Environment values are read once and cached for subsequent lookups, which
    makes it suitable for hot configuration paths.
    """

    _env_cache: ClassVar[dict[str, str] | None] = None
    _env_cache_case_sensitive: ClassVar[bool] = True

    def __init__(self, prefix: str = "", case_sensitive: bool = False) -> None:
        """
        Create a new environment provider.

        Args:
            prefix: Optional prefix added to every requested key.
            case_sensitive: When ``False`` (default), lookups are case-insensitive.
        """
        self.prefix = prefix
        self.case_sensitive = case_sensitive

        self._init_cache()

    def _init_cache(self) -> None:
        """Initialize or refresh the process-wide environment cache."""
        if EnvProvider._env_cache is None or EnvProvider._env_cache_case_sensitive != self.case_sensitive:
            if self.case_sensitive:
                EnvProvider._env_cache = dict(os.environ)
            else:
                EnvProvider._env_cache = {k.upper(): v for k, v in os.environ.items()}

            EnvProvider._env_cache_case_sensitive = self.case_sensitive

    def get_value(self, key: str) -> str | None:
        """
        Get a single environment variable.

        Args:
            key: Environment variable name without prefix.

        Returns:
            The value or ``None`` if not found.
        """
        full_key = f"{self.prefix}{key}"

        if not self.case_sensitive:
            full_key = full_key.upper()

        return EnvProvider._env_cache.get(full_key)  # type: ignore[union-attr]

    def get_values(self, keys: list[str]) -> dict[str, str | None]:
        """
        Get multiple environment variables at once.

        Args:
            keys: List of variable names without prefix.

        Returns:
            Mapping from key to value (or ``None`` if missing).
        """
        return {key: self.get_value(key) for key in keys}

    def get_all(self) -> dict[str, str]:
        """Get all environment variables as a normalized dictionary.

        Keys are normalized to lowercase for case-insensitive matching.
        Optimized for providers that can return all data at once.

        Returns:
            Dictionary with lowercase keys mapping to environment variable values.
        """
        cache = EnvProvider._env_cache
        if cache is None:
            return {}

        if self.case_sensitive:
            return {k.lower(): v for k, v in cache.items()}
        else:
            return {k.lower(): v for k, v in cache.items()}

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the internal environment cache.

        Primarily useful in tests.
        """
        cls._env_cache = None
        cls._env_cache_case_sensitive = True
