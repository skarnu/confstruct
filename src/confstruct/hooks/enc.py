from typing import Any


def _fallback_encode(obj: Any) -> str:
    return str(obj)


def enc_hook(obj: Any):
    if callable(getattr(obj, "__encode__", None)):
        return obj.__encode__()
    return _fallback_encode(obj)

