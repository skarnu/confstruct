## Getting Started with Confstruct

Confstruct provides a simple and efficient way to load configuration into `msgspec.Struct` models, with special support for custom types like `SecretStr` that enhance type safety and security.

### Installation

Install confstruct from GitHub using `uv`:

```bash
uv add "confstruct @ https://github.com/skarnu/confstruct.git"
```

Or using `pip`:

```bash
pip install "confstruct @ https://github.com/skarnu/confstruct.git"
```

### Define a Configuration Model

Create a `msgspec.Struct` that describes your application's configuration schema. For sensitive values like passwords or API keys, use `SecretStr` instead of plain `str` to prevent accidental leaking in logs or string representations.

```python
import msgspec
from confstruct import load
from confstruct.types import SecretStr

class Config(msgspec.Struct):
    host: str
    port: int = 8000
    debug: bool = False
    password: SecretStr
```

### Load Configuration

By default, `load()` uses `EnvProvider`, which reads configuration from environment variables.

```python
# Load configuration from environment variables
config = load(Config)

# Access configuration values
print(config.host)          # "localhost"
print(config.port)          # 8000
print(config.password)      # SecretStr('***')
print(config.password.value)  # Actual password (when needed)
```

#### Example with Environment Variables

Set environment variables before loading:

```bash
export HOST=localhost
export PORT=8000
export DEBUG=true
export PASSWORD=mysecretpass
```

Then in Python:

```python
config = load(Config)
print(config.host)   # "localhost"
print(config.port)   # 8000 (converted from string to int)
print(config.debug)  # True (converted from string to bool)
```

### Using Different Providers

Confstruct supports multiple configuration sources through providers. Switch providers by passing `provider=` to `load()`:

```python
from confstruct import load
from confstruct.providers import EnvProvider, DotenvProvider, JSONProvider

# From .env file
config = load(Config, provider=DotenvProvider(dotenv_path=".env"))

# From JSON file
config = load(Config, provider=JSONProvider("config.json"))

# From dictionary
config = load(Config, provider=JSONProvider({"host": "localhost", "port": 8000}))
```

For more details, see [Configuration Providers](./providers.md).

### Type Conversion

Confstruct automatically converts environment variable strings to the appropriate Python types:

- **`int`** — Parsed via `int(value)`
- **`float`** — Parsed via `float(value)`
- **`bool`** — `"true"`, `"1"`, `"yes"`, `"on"` (case-insensitive) → `True`; all others → `False`
- **`str`** — Used as-is
- **Custom types** — Validated via `__validate__` method (see [Custom Validators](./validators.md))

### Default Values

Fields with default values are optional:

```python
class Config(msgspec.Struct):
    host: str                          # Required
    port: int = 8000                   # Optional, defaults to 8000
    password: SecretStr = SecretStr("") # Optional, defaults to empty SecretStr
```

When a required field is missing, `load()` raises `ValueError`:

```python
try:
    config = load(Config)
except ValueError as e:
    print(f"Missing configuration: {e}")
```

### Strict Mode

Enable strict validation to reject unknown fields and enforce stricter type checking:

```python
config = load(Config, strict=True)
```

### Custom Decoding Hook

For advanced use cases, provide a custom decoding hook to handle specialized types:

```python
def my_dec_hook(typ, value):
    # Custom logic for specific types
    return value

config = load(Config, dec_hook=my_dec_hook)
```

### Case-Insensitive Field Matching

By default, field names are matched case-insensitively. An environment variable `HOST`, `Host`, or `host` will all match a field named `host`:

```python
# All of these match the `host` field:
# HOST=localhost
# Host=localhost
# host=localhost
```

This behavior is controlled by the provider's `case_sensitive` parameter (see [Providers](./providers.md)).

### Performance Optimization

Confstruct is highly optimized for performance:

- **Caching** — Field metadata is cached after first use
- **Single-pass normalization** — Keys are normalized in a single pass
- **Zero intermediate allocations** — Minimal memory overhead
- **Batch operations** — Providers can optimize bulk lookups

These optimizations make confstruct suitable for hot configuration paths and high-performance applications.