"""Environment-backed local configuration."""

import os
from pathlib import Path


def database_path() -> Path:
    """Return the configured SQLite path (relative paths use the launch directory)."""
    configured_path = os.environ.get("CDIT_DATABASE_PATH", "data/cdit_support.db")
    return Path(configured_path).expanduser()
