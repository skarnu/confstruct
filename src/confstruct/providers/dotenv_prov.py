from pathlib import Path

from dotenv import load_dotenv

from .env_prov import EnvProvider


class DotenvProvider(EnvProvider):
    """Provider that loads .env files."""

    def __init__(
        self,
        prefix: str = "",
        case_sensitive: bool = False,
        dotenv_path: str | Path | None = None,
        override: bool = False,
    ) -> None:
        """Initialize provider and load .env file.

        Args:
            dotenv_path: Path to .env file
            override: Override existing environment variables
        """
        load_dotenv(dotenv_path=dotenv_path, override=override)
        super().__init__(prefix=prefix, case_sensitive=case_sensitive)
