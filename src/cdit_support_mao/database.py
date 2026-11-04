"""Minimal SQLite connection helpers; domain schema is intentionally undecided."""

import sqlite3
from contextlib import closing

from cdit_support_mao.config import database_path


def connect() -> sqlite3.Connection:
    """Open the local database with foreign-key enforcement enabled."""
    path = database_path()
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=5.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def check_database() -> bool:
    """Check that the configured SQLite database accepts a simple query."""
    with closing(connect()) as connection:
        connection.execute("SELECT 1").fetchone()
    return True
