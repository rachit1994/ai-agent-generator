from __future__ import annotations

import pytest

from production_architecture.storage.config import load_storage_backend_config
from production_architecture.storage.errors import STORAGE_BACKEND_UNAVAILABLE, StorageError


def test_load_storage_backend_config_defaults_to_postgres(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PA_STORAGE_BACKEND_MODE", raising=False)
    monkeypatch.setenv("PA_STORAGE_DB_DSN", "postgres://localhost/db")
    cfg = load_storage_backend_config(runtime_mode="local-prod")
    assert cfg.mode == "postgres"
    assert cfg.vector_dim == 1536


def test_load_storage_backend_config_rejects_unknown_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PA_STORAGE_BACKEND_MODE", "bad-mode")
    with pytest.raises(StorageError) as exc:
        load_storage_backend_config(runtime_mode="local-prod")
    assert exc.value.code == STORAGE_BACKEND_UNAVAILABLE


def test_load_storage_backend_config_local_prod_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PA_STORAGE_BACKEND_MODE", "artifact_compat")
    with pytest.raises(StorageError) as exc:
        load_storage_backend_config(runtime_mode="local-prod")
    assert exc.value.code == STORAGE_BACKEND_UNAVAILABLE


def test_load_storage_backend_config_rejects_invalid_vector_dim(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PA_STORAGE_BACKEND_MODE", "artifact_compat")
    monkeypatch.setenv("PA_VECTOR_DIM", "not-int")
    with pytest.raises(StorageError) as exc:
        load_storage_backend_config(runtime_mode="guarded_pipeline")
    assert exc.value.code == STORAGE_BACKEND_UNAVAILABLE
