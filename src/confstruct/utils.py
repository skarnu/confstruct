from functools import lru_cache
from typing import Any

import msgspec


@lru_cache(maxsize=128)
def get_struct_fields(obj_type: type) -> tuple[msgspec.structs.Field, ...]:
    """Return msgspec struct fields for the given type (cached)."""
    return msgspec.structs.fields(obj_type)


@lru_cache(maxsize=128)
def get_required_field_names_lower(obj_type: type) -> tuple[str, ...]:
    """Return lowercase names of all required fields for the given struct type."""
    return tuple(field.name.lower() for field in get_struct_fields(obj_type) if field.default is msgspec.NODEFAULT)


@lru_cache(maxsize=128)
def get_field_defaults(obj_type: type) -> dict[str, Any]:
    """Return mapping of field names to their default values (cached)."""
    fields = get_struct_fields(obj_type)
    return {field.name: field.default for field in fields if field.default is not msgspec.NODEFAULT}
