<img src='https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/refs/heads/main/Objects/Toolbox.webp' width='75' style='vertical-align:middle'>

# Confstruct
Modern library to configure your Python apps based on msgspec

<p>
    <img alt="uv" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fastral-sh%2Fuv%2Fmain%2Fassets%2Fbadge%2Fv0.json&style=flat-square&labelColor=232226&color=6341AC&link=https%3A%2F%2Fastral.sh%2Fuv">
    <img alt="Ruff" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fastral-sh%2Fruff%2Fmain%2Fassets%2Fbadge%2Fv2.json&style=flat-square&labelColor=232226&color=6341AC&link=https%3A%2F%2Fastral.sh%2Fruff">
    <a href="https://github.com/skarnu/confstruct/blob/master/pyproject.toml"><img alt="Python versions" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/skarnu/confstruct/refs/heads/main/pyproject.toml&style=flat-square&logo=python&logoColor=fff&labelColor=black"></img></a>
    <a href="https://github.com/skarnu/confstruct/blob/master/pyproject.toml">
    <img alt="Project version" src="https://img.shields.io/badge/version-v1.0.1-black?style=flat-square&logo=python&logoColor=fff"></img></a>
</p>

<h2><img src='https://github.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/blob/master/Emojis/Objects/Pencil.png?raw=true' width='20' style='vertical-align:middle'> Usage</h2>

```shell
pip install "confstruct @ https://github.com/skarnu/confstruct.git"
```

```python
import msgspec
from confstruct import load
from confstruct.provider import JSONProvider
from confstruct.types import SecretStr

class Config(msgspec.Struct):
    password: SecretStr

config = load(Config, provider=JSONProvider({"password": "12345678"}))
print(config.password) # Output: ********
print(config.password.value) # Output: 12345678
```

<h2><img src='https://github.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/blob/master/Emojis/Objects/Notebook.png?raw=true' width='20' style='vertical-align:middle'> License</h2>

Confstruct is [MIT licensed](https://github.com/skarnu/confstruct/blob/master/LICENSE)
