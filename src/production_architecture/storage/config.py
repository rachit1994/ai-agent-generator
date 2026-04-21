"""Fail-closed storage backend configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .errors import STORAGE_BACKEND_UNAVAILABLE, fail

_DEFAULT_VECTOR_DIM = 1536
_MODE_POSTGRES = "postgres"
_MODE_ARTIFACT_COMPAT = "artifact_compat"
_ALLOWED_MODES = {_MODE_POSTGRES, _MODE_ARTIFACT_COMPAT}


@dataclass(frozen=True, slots=True)
class StorageBackendConfig:
    mode: str
    dsn: str
    vector_dim: int


def _parse_vector_dim(raw: str) -> int:
    value = raw.strip()
    if not value:
        return _DEFAULT_VECTOR_DIM
    try:
        parsed = int(value)
    except ValueError as exc:
        raise fail(STORAGE_BACKEND_UNAVAILABLE, "PA_VECTOR_DIM must be an integer") from exc
    if parsed <= 0:
        raise fail(STORAGE_BACKEND_UNAVAILABLE, "PA_VECTOR_DIM must be positive")
    return parsed


def load_storage_backend_config(*, runtime_mode: str) -> StorageBackendConfig:
    mode = os.getenv("PA_STORAGE_BACKEND_MODE", _MODE_POSTGRES).strip() or _MODE_POSTGRES
    if mode not in _ALLOWED_MODES:
        raise fail(
            STORAGE_BACKEND_UNAVAILABLE,
            "PA_STORAGE_BACKEND_MODE must be one of: postgres, artifact_compat",
        )
    if runtime_mode == "local-prod" and mode != _MODE_POSTGRES:
        raise fail(
            STORAGE_BACKEND_UNAVAILABLE,
            "local-prod requires PA_STORAGE_BACKEND_MODE=postgres",
        )
    dsn = os.getenv("PA_STORAGE_DB_DSN", "").strip()
    if mode == _MODE_POSTGRES and not dsn:
        raise fail(STORAGE_BACKEND_UNAVAILABLE, "PA_STORAGE_DB_DSN is required in postgres mode")
    vector_dim = _parse_vector_dim(os.getenv("PA_VECTOR_DIM", ""))
    return StorageBackendConfig(mode=mode, dsn=dsn, vector_dim=vector_dim)
