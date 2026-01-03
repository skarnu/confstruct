import json
from collections.abc import Callable
from typing import Any

import msgspec

from confstruct.hooks import dec_hook
from confstruct.providers import ABCProvider, EnvProvider


def load[M: msgspec.Struct](
    obj: type[M],
    provider: ABCProvider | None = None,
    dec_hook: Callable[[type, Any], Any] = dec_hook,
    strict: bool = False,
) -> M:
    if not provider:
        provider = EnvProvider()
    data: dict[str, Any] = {}
    for field in msgspec.structs.fields(obj):
        val = provider.get_value(field.name) or field.default
        if not val:
            raise ValueError(f"Cannot find value for field {field.name!r}")
        data[field.name] = val

    payload = json.dumps(data).encode("utf-8")
    return msgspec.json.decode(payload, type=obj, dec_hook=dec_hook, strict=strict)
