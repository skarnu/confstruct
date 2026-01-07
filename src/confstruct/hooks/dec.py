import inspect
from functools import lru_cache
from types import UnionType
from typing import Any, Union, get_args, get_origin


@lru_cache(maxsize=1024)
def _get_validate_method(typ: type) -> callable:  # pyright: ignore[reportGeneralTypeIssues]
    """
    Return the cached ``__validate__`` method for a type, if any.

    Handles both direct __validate__ and __validate__ on __origin__ (PEP 695 generics).
    """
    # Try direct __validate__ first
    validate = getattr(typ, "__validate__", None)
    if validate is not None:
        return validate

    # Try __validate__ on __origin__ for PEP 695 generic types
    origin = getattr(typ, "__origin__", None)
    if origin is not None:
        validate = getattr(origin, "__validate__", None)
        if validate is not None:
            return validate

    return None


@lru_cache(maxsize=256)
def _get_type_info(typ: Any) -> tuple[Any, tuple[Any, ...]]:
    """
    Get origin and arguments for a typing annotation (cached).

    This wraps ``typing.get_origin`` and ``typing.get_args`` which are
    relatively expensive on hot paths.
    """
    origin = get_origin(typ)
    if origin is None:
        return typ, ()
    return origin, get_args(typ)


@lru_cache(maxsize=128)
def _get_origin_only(typ: Any) -> Any:
    """
    Fast origin lookup for a typing annotation (cached).
    """
    return get_origin(typ)


def _check_simple_type(value: Any, typ: Any) -> bool:
    """Check a value against a non-parameterized (simple) type."""
    try:
        return isinstance(value, typ)
    except TypeError:
        return isinstance(value, type) and type(value).__name__ == typ.__name__


@lru_cache(maxsize=1024)
def isinstance_typed_cached(value_type: Any, typ: Any) -> bool:
    """Cached, type-based variant of ``isinstance_typed``.

    Useful when the value's type is known and checked repeatedly.
    """
    return isinstance_typed(value_type, typ)


def _check_union_type(value: Any, args: tuple[Any, ...]) -> bool:
    """Check a value against a ``Union`` type."""
    return any(isinstance_typed(value, t) for t in args)


def _check_list_type(value: Any, args: tuple[Any, ...]) -> bool:
    """Check a value against a ``list[T]`` annotation."""
    if not isinstance(value, list):
        return False

    if not args:
        return True

    item_type = args[0]
    return all(isinstance_typed(item, item_type) for item in value)


def _check_dict_type(value: Any, args: tuple[Any, ...]) -> bool:
    """Check a value against a ``dict[K, V]`` annotation."""
    if not isinstance(value, dict):
        return False

    if not args:
        return True

    key_type, val_type = args
    return all(isinstance_typed(k, key_type) and isinstance_typed(v, val_type) for k, v in value.items())


def _check_tuple_type(value: Any, args: tuple[Any, ...]) -> bool:
    """Check a value against a ``tuple`` annotation."""
    if not isinstance(value, tuple):
        return False

    if not args:
        return True

    if len(args) == 2 and args[1] is ...:
        return all(isinstance_typed(item, args[0]) for item in value)

    if len(args) != len(value):
        return False

    return all(isinstance_typed(v, t) for v, t in zip(value, args, strict=True))


def isinstance_typed(value: Any, typ: Any) -> bool:
    """
    Recursively check a value against a typing annotation.

    Supports:
    - Simple types (``int``, ``str``, etc.).
    - ``Union`` / ``|`` types.
    - Collections (``list[T]``, ``dict[K, V]``, ``tuple[...]``).
    - Nested annotations.
    """
    origin = _get_origin_only(typ)

    if origin is None:
        return _check_simple_type(value, typ)

    origin, args = _get_type_info(typ)

    if origin is Union or origin is UnionType:
        return _check_union_type(value, args)

    if origin is list:
        return _check_list_type(value, args)

    if origin is dict:
        return _check_dict_type(value, args)

    if origin is tuple:
        return _check_tuple_type(value, args)

    return isinstance(value, origin)


# Cached set of simple types for the hot path in ``dec_hook``.
_SIMPLE_TYPES = {int, str, float, bool, bytes, list, dict, tuple}


def dec_hook[M](typ: type[M], value: Any) -> M:
    """
    Custom decoding hook for ``msgspec`` with validation support.

    Integrates with types that expose a ``__validate__`` method
    (such as ``SecretStr`` and ``ListOf[...]``) while keeping simple
    cases extremely fast.

    Args:
        typ: Target type.
        value: Raw value to convert.

    Returns:
        Converted value of the requested type.

    Raises:
        TypeError: If conversion fails for all attempted strategies.
    """
    if typ in _SIMPLE_TYPES:
        return typ(value)  # type: ignore[call-arg]

    # Try __validate__ method (works for custom types and PEP 695 generics)
    validate_method = _get_validate_method(typ)
    if validate_method is not None:
        try:
            return validate_method(value, typ)  # type: ignore[misc]
        except (TypeError, ValueError):
            pass

    try:
        return typ(value)  # type: ignore[call-arg]
    except (TypeError, ValueError) as e:
        error_msg = f"Cannot convert {type(value).__name__} to {typ}"
        raise TypeError(error_msg) from e


def clear_type_caches() -> None:
    """
    Clear all internal type-related caches.

    Useful in tests or environments where type definitions change at runtime.
    """
    _get_type_info.cache_clear()
    _get_origin_only.cache_clear()
