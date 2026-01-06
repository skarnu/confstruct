## Custom Validators & Types

Confstruct doesn't require a dedicated base class for validators. Any type can act as a validator as long as it defines a `__validate__` classmethod. This makes validation a composable, ergonomic part of your configuration model.

### The `__validate__` Contract

To make a custom type compatible with Confstruct:

1. **Define `__validate__` classmethod** — This is called by Confstruct during loading to validate and convert raw values
2. **Inherit from the target type** (recommended) — If you want the final value to behave like a string, subclass `str`
3. **Return value or instance** — You can return either:
   - The validated raw value (e.g., `int`, `str`). Confstruct will automatically wrap it into your custom type.
   - An instance of your custom type itself (useful for custom initialization or state)

### Validation Hook Signature

```python
class MyType:
    @classmethod
    def __validate__(cls, value: Any) -> Any:
        """
        Validate and/or transform the raw value.
        
        Args:
            value: The raw value from the provider (usually a string)
        
        Returns:
            Either the validated raw value or an instance of cls
        
        Raises:
            ValueError, TypeError: On validation failure
        """
        # Your validation logic here
        return value
```

### Example 1: Port Number Validator

Here's a practical example that validates port numbers (1-65535):

```python
from typing import Any

class Port(int):
    """Validates that a port is in the valid range (1-65535)."""
    
    @classmethod
    def __validate__(cls, value: Any) -> int:
        """Validate the port number."""
        # Convert to int (works with strings from env vars)
        port = int(value)
        
        # Check valid range
        if not (1 <= port <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {port}")
        
        # Return the raw int; Confstruct wraps it into Port(port)
        return port

    def __encode__(self) -> int:
        """Serialize port back to JSON."""
        return int(self)
```

**Usage:**

```python
import msgspec
from confstruct import load

class Config(msgspec.Struct):
    port: Port

config = load(Config)  # PORT=8000 → Port(8000)
print(config.port)      # Port(8000)
print(int(config.port)) # 8000
```

### Example 2: Email Validator

Validate email addresses with a simple regex pattern:

```python
import re
from typing import Any

class Email(str):
    """Validates email format."""
    
    EMAIL_PATTERN = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
    
    @classmethod
    def __validate__(cls, value: Any) -> str:
        """Validate email format."""
        email = str(value).strip()
        
        if not cls.EMAIL_PATTERN.match(email):
            raise ValueError(f"Invalid email format: {email}")
        
        return email

    def __encode__(self) -> str:
        return str(self)
```

**Usage:**

```python
import msgspec
from confstruct import load

class Config(msgspec.Struct):
    admin_email: Email

config = load(Config)  # ADMIN_EMAIL=admin@example.com → Email('admin@example.com')
```

### Example 3: URL Validator

Validate HTTP/HTTPS URLs:

```python
from typing import Any
from urllib.parse import urlparse

class URL(str):
    """Validates HTTP/HTTPS URLs."""
    
    @classmethod
    def __validate__(cls, value: Any) -> str:
        """Validate URL format."""
        url = str(value).strip()
        
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                raise ValueError(f"URL must use http or https, got {parsed.scheme}")
            if not parsed.netloc:
                raise ValueError("URL must have a domain")
        except Exception as e:
            raise ValueError(f"Invalid URL: {url}") from e
        
        return url

    def __encode__(self) -> str:
        return str(self)
```

### Example 4: Database Connection String with Parsing

Create a validator that parses and stores connection components:

```python
from typing import Any
from urllib.parse import urlparse

class DatabaseURL:
    """Parses and validates database connection strings."""
    
    def __init__(self, url: str):
        self.url = url
        parsed = urlparse(url)
        self.scheme = parsed.scheme
        self.username = parsed.username
        self.password = parsed.password
        self.host = parsed.hostname
        self.port = parsed.port
        self.database = parsed.path.lstrip('/')
    
    @classmethod
    def __validate__(cls, value: Any) -> "DatabaseURL":
        """Validate and parse database URL."""
        url = str(value)
        
        # Basic validation
        if not url.startswith(('postgresql://', 'mysql://', 'sqlite://')):
            raise ValueError("Database URL must start with postgresql://, mysql://, or sqlite://")
        
        # Return instance directly (with custom state)
        return cls(url)
    
    def __encode__(self) -> str:
        """Serialize back to connection string."""
        return self.url
    
    def __repr__(self) -> str:
        return f"DatabaseURL({self.scheme}://{self.host}/{self.database})"
```

**Usage:**

```python
import msgspec
from confstruct import load

class Config(msgspec.Struct):
    database: DatabaseURL

config = load(Config)  # DATABASE=postgresql://user:pass@localhost/mydb
print(config.database.scheme)   # "postgresql"
print(config.database.host)     # "localhost"
print(config.database.database) # "mydb"
```

### The `__encode__` Method

To correctly serialize your custom types back to JSON (for logging, APIs, etc.), implement `__encode__`:

```python
class MyType:
    @classmethod
    def __validate__(cls, value: Any) -> Any:
        # Validation logic
        pass
    
    def __encode__(self) -> Any:
        """
        Return a JSON-serializable representation of this value.
        
        Returns:
            A primitive type (str, int, dict, list, etc.) that msgspec can serialize
        """
        # Return JSON-serializable representation
        return "some_value"
```

**Example with complex serialization:**

```python
class Config:
    """Stores configuration with complex state."""
    
    def __init__(self, data: dict):
        self.host = data['host']
        self.port = data['port']
        self.timeout = data.get('timeout', 30)
    
    @classmethod
    def __validate__(cls, value: Any) -> "Config":
        """Parse config string or dict."""
        if isinstance(value, str):
            # Parse JSON string
            import json
            data = json.loads(value)
        else:
            data = value
        return cls(data)
    
    def __encode__(self) -> dict:
        """Serialize back to dict for JSON output."""
        return {
            'host': self.host,
            'port': self.port,
            'timeout': self.timeout
        }
```

### Inheritance and Type Relationships

For better type compatibility, inherit from the type you want to behave like:

```python
# Good: PositiveInt will behave like int
class PositiveInt(int):
    @classmethod
    def __validate__(cls, value: Any) -> int:
        num = int(value)
        if num <= 0:
            raise ValueError("Must be positive")
        return num

# Also works: inheriting from str
class SafeString(str):
    @classmethod
    def __validate__(cls, value: Any) -> str:
        s = str(value).strip()
        if not s:
            raise ValueError("Cannot be empty")
        return s

# Works for any type: doesn't inherit but still functions
class CustomConfig:
    @classmethod
    def __validate__(cls, value: Any) -> "CustomConfig":
        # Custom parsing logic
        return cls(value)
```

### Performance Optimization: Caching Validators

For types that perform expensive validation (like `SecretStr`), Confstruct caches the validation method:

```python
from functools import lru_cache

class MyExpensiveValidator:
    @classmethod
    @lru_cache(maxsize=128)
    def _get_validate_method(cls):
        """Cache the validation method for repeated lookups."""
        return cls.__validate__
    
    @classmethod
    def __validate__(cls, value):
        # Your expensive validation logic
        return value
```

### Error Handling in Validators

Always raise informative errors to help users debug configuration issues:

```python
class StrictPort(int):
    @classmethod
    def __validate__(cls, value: Any) -> int:
        try:
            port = int(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"PORT must be a valid integer, got {value!r}") from e
        
        if not (1 <= port <= 65535):
            raise ValueError(
                f"PORT must be between 1 and 65535 (valid port range), got {port}"
            )
        
        return port
```

### Testing Custom Validators

```python
from confstruct import load
from confstruct.providers import JSONProvider
import msgspec

class Config(msgspec.Struct):
    port: Port

# Test valid port
config = load(Config, provider=JSONProvider({"port": "8000"}))
assert config.port == 8000

# Test invalid port
try:
    config = load(Config, provider=JSONProvider({"port": "99999"}))
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "Port out of range" in str(e)
```

### Best Practices

1. **Always validate on construction** — Catch issues early
2. **Provide clear error messages** — Help users understand what went wrong
3. **Implement `__encode__` if needed** — Ensure custom types can be serialized
4. **Use inheritance** — Subclass the type you want to behave like
5. **Cache expensive operations** — Use `@lru_cache` for validation methods
6. **Handle type coercion** — Accept raw strings from environment variables
7. **Keep validation logic focused** — One validator, one concern
