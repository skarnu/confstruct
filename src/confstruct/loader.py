from collections.abc import Callable
from typing import Any, get_args, get_origin

import msgspec

from confstruct.hooks import dec_hook
from confstruct.providers import ABCProvider, EnvProvider
from confstruct.utils import get_field_defaults, get_required_field_names_lower, get_struct_fields


def _convert_env_value(value: Any, field_type: Any) -> Any:  # noqa: PLR0911
    """Ultra-fast environment value conversion."""
    if not isinstance(value, str):
        return value

    if field_type is bool:
        v = value.lower()
        return v in ("true", "1", "yes", "on")

    if field_type is int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return value

    if field_type is float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    if field_type is str:
        return str(value)

    return value


def _extreme_fast_json_load[M](obj: type[M], data: dict[str, Any]) -> M:
    """Extreme-fast JSON loading with zero overhead."""
    fields = get_struct_fields(obj)
    required = set(get_required_field_names_lower(obj))

    data_keys = set(data.keys())

    if not required.issubset(data_keys):
        missing = required - data_keys
        raise ValueError(f"Required field {next(iter(missing))!r} not found")

    kwargs = {}
    get_field_defaults(obj)

    for field in fields:
        field_name = field.name
        field_type = field.type
        field_lower = field_name.lower()

        if field_lower in data:
            value = data[field_lower]

            if field_type is int:
                kwargs[field_name] = int(value)
            elif field_type is float:
                kwargs[field_name] = float(value)
            elif field_type is str:
                kwargs[field_name] = str(value)
            elif field_type is bool:
                v = str(value).lower()
                kwargs[field_name] = v in ("true", "1", "yes", "on")
            else:
                try:
                    kwargs[field_name] = dec_hook(field_type, value)
                except Exception:  # noqa: BLE001
                    kwargs[field_name] = value
        elif field.default is not msgspec.NODEFAULT:
            kwargs[field_name] = field.default

    return obj(**kwargs)


def load[M](
    obj: type[M],
    provider: ABCProvider | None = None,
    dec_hook: Callable[[type, Any], Any] = dec_hook,
    strict: bool = False,
) -> M:
    """Load configuration with extreme performance optimizations."""
    provider = provider or EnvProvider()

    if hasattr(provider, "get_all") and not isinstance(provider, EnvProvider):
        data = provider.get_all()
        return _extreme_fast_json_load(obj, data)

    if hasattr(provider, "get_all"):
        data = provider.get_all()

        required = set(get_required_field_names_lower(obj))
        data_keys = set(data.keys())
        if not required.issubset(data_keys):
            missing = required - data_keys
            raise ValueError(f"Required field {next(iter(missing))!r} not found")

        if isinstance(provider, EnvProvider):
            fields = get_struct_fields(obj)
            for field in fields:
                field_lower = field.name.lower()
                if field_lower in data:
                    data[field.name] = _convert_env_value(data.pop(field_lower), field.type)
                elif field.default is not msgspec.NODEFAULT:
                    data[field.name] = field.default
                else:
                    data.pop(field_lower, None)

    else:
        fields = get_struct_fields(obj)
        data = {}
        for field in fields:
            value = provider.get_value(field.name)
            if value is not None:
                if isinstance(provider, EnvProvider):
                    value = _convert_env_value(value, field.type)
                data[field.name] = value
            elif field.default is msgspec.NODEFAULT:
                raise ValueError(f"Required field {field.name!r} not found")

    try:
        if strict:
            return msgspec.convert(data, obj, dec_hook=dec_hook, strict=True)
        return msgspec.convert(data, obj, dec_hook=dec_hook)
    except msgspec.ValidationError as e:
        raise ValueError(f"Validation failed: {e}") from e
