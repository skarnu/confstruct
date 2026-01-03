from typing import Any


def dec_hook(typ: type, value: Any) -> Any:
    if hasattr(typ, "__validate__"):
        val = typ.__validate__(value, typ)
        if isinstance(val, typ):
            return val
        return typ(val)
    return typ(value)
