from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from .config import get_setting


def connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or str(get_setting("DB_PATH", "data/ytseo.sqlite"))
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    return conn


def _find_migration_file(filename: str = "0001_init.sql") -> Optional[Path]:
    candidates = [
        Path.cwd() / "migrations" / filename,
        Path(__file__).resolve().parents[1] / "migrations" / filename,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def apply_migrations(conn: sqlite3.Connection) -> None:
    mig = _find_migration_file()
    if not mig:
        return
    sql = mig.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()
