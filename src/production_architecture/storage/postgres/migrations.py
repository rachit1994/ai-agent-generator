"""Postgres migration runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from production_architecture.storage.errors import (
    STORAGE_MIGRATION_FAILED,
    STORAGE_PGVECTOR_MISSING,
    fail,
)

_SQL_DIR = Path(__file__).resolve().parents[1] / "sql"
_MIGRATIONS = ("001_storage_core.sql", "002_storage_indexes.sql")


def _render_migration(sql: str, *, vector_dim: int) -> str:
    if not isinstance(vector_dim, int) or isinstance(vector_dim, bool) or vector_dim <= 0:
        raise fail(STORAGE_MIGRATION_FAILED, "vector_dim must be a positive integer")
    return sql.replace("__PA_VECTOR_DIM__", str(vector_dim))


def apply_migrations(conn: Any, *, vector_dim: int = 1536) -> None:
    try:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS pa_schema_migrations (migration_id TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
            )
            cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            if cur.fetchone() is None:
                raise fail(STORAGE_PGVECTOR_MISSING, "pgvector extension is required")
            for migration_name in _MIGRATIONS:
                cur.execute(
                    "SELECT 1 FROM pa_schema_migrations WHERE migration_id = %s",
                    (migration_name,),
                )
                if cur.fetchone() is not None:
                    continue
                sql = _render_migration(
                    (_SQL_DIR / migration_name).read_text(encoding="utf-8"),
                    vector_dim=vector_dim,
                )
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO pa_schema_migrations (migration_id) VALUES (%s)",
                    (migration_name,),
                )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        if hasattr(exc, "code") and str(getattr(exc, "code")) == STORAGE_PGVECTOR_MISSING:
            raise
        raise fail(STORAGE_MIGRATION_FAILED, str(exc)) from exc
