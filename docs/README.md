# Confstruct Documentation

Confstruct is a modern, high-performance configuration loading library for Python that integrates seamlessly with `msgspec.Struct`. It provides type-safe configuration management with support for custom validators, secret types, and flexible data providers.

## Table of Contents

1. **[Getting Started](./usage.md)** — Installation, basic setup, and common usage patterns
2. **[Configuration Providers](./providers.md)** — Understanding and using different data sources (environment variables, JSON, .env files)
3. **[Custom Validators & Types](./validators.md)** — Creating custom validation logic and serialization for specialized types

## Key Features

- **Type-safe configuration** using `msgspec.Struct` models
- **Zero-overhead validation** with custom `__validate__` methods
- **Secret handling** with `SecretStr` type for sensitive data
- **Multiple data sources** via pluggable providers
- **Extreme performance optimizations** including caching and single-pass normalization
- **Case-insensitive field matching** (by default) for flexibility
- **Custom serialization** with `__encode__` method support