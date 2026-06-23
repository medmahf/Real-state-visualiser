"""Connexion SQLite en lecture seule."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "data.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()
