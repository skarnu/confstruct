from pathlib import Path

from dotenv import load_dotenv

from .env_prov import EnvProvider


class DotenvProvider(EnvProvider):
    """Provider that loads .env files."""

    def __init__(self, dotenv_path: str | Path | None = None, override: bool = False) -> None:
        """Initialize provider and load .env file.

        Args:
            dotenv_path: Path to .env file
            override: Override existing environment variables
        """
        super().__init__()
        if isinstance(dotenv_path, Path):
            load_dotenv(dotenv_path=dotenv_path, override=override)
        elif isinstance(dotenv_path, str):
            load_dotenv(dotenv_path=Path(dotenv_path), override=override)
        else:
            load_dotenv(override=override)
