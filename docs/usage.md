## Usage

Confstruct provides a small, predictable way to load configuration into `msgspec.Struct` models, with validation-friendly field types like `SecretStr`.

### Install

```bash
uv add "confstruct @ https://github.com/skarnu/confstruct.git" # from GitHub
```

### Define a config model

Create a `msgspec.Struct` that describes your configuration schema. For secrets, use `SecretStr` so the value can be stored safely and handled explicitly.

```python
import msgspec
from confstruct import load
from confstruct.types import SecretStr


class Config(msgspec.Struct):
    password: SecretStr
```

### Load configuration

By default, `load()` uses `EnvProvider`, meaning values are read from environment variables.

```python
config = load(Config)  # Default provider: EnvProvider
```
>[!TIP]
>Read more about providers [here](./providers.md)

At this point, `config` is a typed `Config` instance, and `password` is a `SecretStr` (not a plain `str`), so you can keep your config model strongly typed and validation-ready.