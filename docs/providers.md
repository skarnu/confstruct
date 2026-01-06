## Configuration Providers

Providers are the foundation of Confstruct's flexibility. A provider is responsible for retrieving raw configuration values (typically as strings or dictionaries) that are then validated and converted into your `msgspec.Struct` model.

### Provider Protocol

Every provider implements the `ABCProvider` protocol with at minimum:

```python
class MyProvider:
    def get_value(self, key: str) -> Any | None:
        """Return the value for a given key, or None if not found."""
        pass

    def get_all(self) -> dict[str, Any]:
        """Optional: Return all configuration at once (more efficient)."""
        pass
```

### Built-in Providers

Confstruct ships with three production-ready providers:

#### 1. EnvProvider

Reads configuration from environment variables with optional caching and case-insensitive matching.

**Features:**
- Automatic environment variable caching for performance
- Case-insensitive key matching (default)
- Optional key prefix
- Process-wide cache that can be cleared for testing

**Usage:**

```python
from confstruct import load
from confstruct.providers import EnvProvider

# Default: case-insensitive, no prefix
config = load(MyConfig, provider=EnvProvider())

# Case-sensitive matching
config = load(MyConfig, provider=EnvProvider(case_sensitive=True))

# With prefix (prepends to all lookups)
config = load(MyConfig, provider=EnvProvider(prefix="APP_"))
```

**Example:**

```bash
export HOST=localhost
export PORT=8000
export DEBUG=true
```

```python
from confstruct.providers import EnvProvider

provider = EnvProvider()
print(provider.get_value("HOST"))     # "localhost"
print(provider.get_value("host"))     # "localhost" (case-insensitive)
```

**Cache Management:**

The `EnvProvider` caches environment variables for performance. Clear it in tests:

```python
from confstruct.providers import EnvProvider

EnvProvider.clear_cache()
```

#### 2. DotenvProvider

Extends `EnvProvider` to load environment variables from a `.env` file before reading them.

**Features:**
- Automatically loads variables from `.env` file
- Inherits all `EnvProvider` features
- Can override existing environment variables
- Useful for local development

**Usage:**

```python
from confstruct import load
from confstruct.providers import DotenvProvider

config = load(MyConfig, provider=DotenvProvider())

# Specify custom .env file path
config = load(MyConfig, provider=DotenvProvider(dotenv_path="config/.env"))

# Override existing environment variables
config = load(MyConfig, provider=DotenvProvider(override=True))

# With prefix
config = load(MyConfig, provider=DotenvProvider(prefix="APP_"))
```

**Example `.env` file:**

```
HOST=localhost
PORT=8000
DEBUG=true
DATABASE_URL=postgresql://user:pass@localhost/db
```

Then in Python:

```python
from confstruct.providers import DotenvProvider

provider = DotenvProvider(dotenv_path=".env")
print(provider.get_value("HOST"))            # "localhost"
print(provider.get_value("DATABASE_URL"))    # "postgresql://..."
```

#### 3. JSONProvider

Loads configuration from JSON data sources with single-pass normalization and caching.

**Features:**
- Loads from dict, JSON string, bytes, or file path
- Automatic file caching for repeated loads
- Case-insensitive key matching
- Extreme performance optimizations (single-pass normalization)

**Usage:**

```python
from confstruct import load
from confstruct.providers import JSONProvider

# From dictionary
config = load(MyConfig, provider=JSONProvider({"host": "localhost", "port": 8000}))

# From JSON file
config = load(MyConfig, provider=JSONProvider("config.json"))

# From JSON string
config = load(MyConfig, provider=JSONProvider('{"host": "localhost", "port": 8000}'))

# From bytes
config = load(MyConfig, provider=JSONProvider(b'{"host": "localhost"}'))
```

**Example:**

```json
{
  "HOST": "localhost",
  "PORT": 8000,
  "DEBUG": true,
  "DATABASE_URL": "postgresql://user:pass@localhost/db"
}
```

```python
from confstruct.providers import JSONProvider

provider = JSONProvider("config.json")
print(provider.get_value("host"))            # "localhost"
print(provider.get_value("HOST"))            # "localhost" (case-insensitive)
print(provider.get_value("database_url"))    # "postgresql://..."
```

### Creating Custom Providers

Implement the `ABCProvider` protocol to create a custom provider. At minimum, implement `get_value()`:

```python
from confstruct.providers import ABCProvider

class CustomProvider(ABCProvider):
    def get_value(self, key: str) -> str | None:
        """Implement required get_value method."""
        # Your custom logic here
        return None

    def get_all(self) -> dict[str, Any]:
        """Optional: implement for better performance."""
        return {}
```

**Example: Database Provider**

```python
from typing import Any
from confstruct.providers import ABCProvider

class DatabaseProvider(ABCProvider):
    """Load configuration from a database."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._cache = {}
    
    def get_value(self, key: str) -> str | None:
        """Fetch single config value from database."""
        if key in self._cache:
            return self._cache[key]
        
        # Pseudo-code: query database
        value = self._query_db(key)
        if value is not None:
            self._cache[key] = value
        return value
    
    def get_all(self) -> dict[str, Any]:
        """Fetch all config values at once (more efficient)."""
        result = {}
        # Pseudo-code: query all configs from database
        rows = self._query_all_configs()
        for row in rows:
            result[row['key'].lower()] = row['value']
        return result
    
    def _query_db(self, key: str) -> str | None:
        # Your database query logic
        pass
    
    def _query_all_configs(self) -> list[dict]:
        # Your database query logic
        pass
```

**Example: YAML Provider**

```python
from pathlib import Path
from typing import Any
import yaml
from confstruct.providers import ABCProvider

class YAMLProvider(ABCProvider):
    """Load configuration from YAML file."""
    
    def __init__(self, path: str | Path):
        self.path = Path(path)
        with open(self.path) as f:
            self._data = yaml.safe_load(f)
    
    def get_value(self, key: str) -> Any | None:
        """Get value by key (case-insensitive)."""
        return self._data.get(key.lower())
    
    def get_all(self) -> dict[str, Any]:
        """Return normalized mapping."""
        return {k.lower(): v for k, v in self._data.items()}
```

### Passing Providers to `load()`

Pass a provider instance to `load()` via the `provider=` parameter:

```python
from confstruct import load

# Use custom provider
config = load(MyConfig, provider=CustomProvider(...))
```

### Performance Tips

1. **Implement `get_all()`** — Providers that can return all data at once are automatically optimized by the loader. Use this for batch operations.

2. **Use caching** — Cache frequently accessed values to avoid repeated lookups.

3. **Normalize keys** — If your data source stores keys with mixed case, normalize them to lowercase for consistency.

4. **Reuse provider instances** — Create a provider once and reuse it across multiple `load()` calls.

Example optimized custom provider:

```python
from confstruct.providers import ABCProvider

class OptimizedProvider(ABCProvider):
    def __init__(self, data: dict):
        # Normalize keys to lowercase once
        self._normalized = {k.lower(): v for k, v in data.items()}
    
    def get_value(self, key: str) -> Any | None:
        return self._normalized.get(key.lower())
    
    def get_all(self) -> dict[str, Any]:
        # Fast path: return pre-normalized data
        return self._normalized
```