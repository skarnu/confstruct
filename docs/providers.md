## Providers

Providers are responsible for fetching raw configuration values for Confstruct. Every provider implements the same minimal interface: it inherits from `confstruct.providers.ABCProvider` and defines a single method `get_value(self, key: str) -> str`.

### Built-in providers

Confstruct ships with a few providers out of the box:

- `EnvProvider`: reads values from environment variables.
- `DotenvProvider`: reads values from a `.env` file (and typically exposes them like environment-style key/value pairs).
- `JSONProvider`: reads values from a JSON source.

### Passing a provider to `load()`

To use a custom provider (or configure a built-in one), pass an instance via `provider=`:

```python
from confstruct import load

config = load(Config, provider=YourProvider(...))
```