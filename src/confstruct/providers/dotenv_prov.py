import json
from pathlib import Path

from dotenv import load_dotenv

from .env_prov import EnvProvider


class DotenvProvider(EnvProvider):
    def __init__(self, dotenv_path: str | Path | None = None) -> None:
        super().__init__()
        load_dotenv(dotenv_path=dotenv_path)
