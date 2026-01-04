from types import UnionType
from typing import Any, Union, get_args, get_origin


def isinstance_typed(value: Any, typ: Any) -> bool:  # noqa: PLR0911
    origin = get_origin(typ)

    if origin is None:
        try:
            return isinstance(value, typ)
        except TypeError:
            return False

    args = get_args(typ)

    if origin is Union or origin is UnionType:
        return any(isinstance_typed(value, t) for t in args)

    if origin is list:
        if not isinstance(value, list):
            return False
        if not args:
            return True
        (item_type,) = args
        return all(isinstance_typed(item, item_type) for item in value)

    return isinstance(value, origin)



def dec_hook(typ: type, value: Any) -> Any:
    if hasattr(typ, "__validate__"):
        val = typ.__validate__(value, typ)
        if isinstance_typed(val, typ):
            return val
        return typ(val)
    return typ(value)
