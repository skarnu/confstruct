## Validators

Confstruct doesn’t require a dedicated “base validator” class. Any type can act as a validator as long as it defines a `@classmethod __validate__(cls, value: Any) -> Any`.

### `__validate__` contract

- The validator type should inherit from the type you want to end up with.  
  Example: if you want the final value to behave like a string, subclass `str`.

- `__validate__` may return:
  - The “raw” validated value (e.g. a `str`). In this case, Confstruct will wrap it into your validator type for you.
  - An instance of the validator type itself (useful when you need custom initialization or extra internal state).

### Encoding (JSON, etc.)

To correctly serialize custom types back to JSON (and other formats), implement `__encode__(self) -> Any`.

- `__encode__` should return a JSON-serializable representation of the value (e.g. `str`, `int`, `dict`, `list`).
- Confstruct will use that returned value as the serialized form of your custom type.

### Minimal example

```python
from typing import Any

class Port(int):
    @classmethod
    def __validate__(cls, value: Any) -> int | "Port":
        v = int(value)
        if not (1 <= v <= 65535):
            raise TypeError("Port out of range")
        return v  # Confstruct will wrap into Port(v)

    def __encode__(self) -> int:
        return int(self)
```