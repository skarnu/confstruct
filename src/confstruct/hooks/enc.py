from typing import Any


def enc_hook(obj: Any):
    if hasattr(obj, "__encode__"):
        return obj.__encode__()
    parents = type(obj).mro()
    if len(parents) == 1:
        raise NotImplementedError
    return parents[0](obj)
