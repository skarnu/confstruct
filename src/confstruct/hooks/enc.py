import json
from typing import Any


def _fallback_encode(obj: Any) -> str:
    """Safely convert object to string."""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return str(obj)


def enc_hook(obj: Any) -> Any:
    """Encoding hook for object serialization.

    Args:
        obj: Object to serialize

    Returns:
        JSON-compatible representation
    """
    encode_method = getattr(obj, "__encode__", None)
    if callable(encode_method):
        try:
            return encode_method()
        except (TypeError, ValueError):
            return _fallback_encode(obj)

    return _fallback_encode(obj)
