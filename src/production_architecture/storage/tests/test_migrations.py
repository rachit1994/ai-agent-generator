from __future__ import annotations

import pytest

from production_architecture.storage.errors import STORAGE_MIGRATION_FAILED, StorageError
from production_architecture.storage.postgres.migrations import _render_migration


def test_render_migration_injects_vector_dim() -> None:
    rendered = _render_migration("embedding VECTOR(__PA_VECTOR_DIM__)", vector_dim=1024)
    assert "VECTOR(1024)" in rendered


def test_render_migration_rejects_invalid_vector_dim() -> None:
    with pytest.raises(StorageError) as exc:
        _render_migration("x", vector_dim=0)
    assert exc.value.code == STORAGE_MIGRATION_FAILED
