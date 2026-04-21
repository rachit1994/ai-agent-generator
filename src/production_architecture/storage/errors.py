"""Stable fail-closed storage errors."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StorageError(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}:{self.message}"


def fail(code: str, message: str) -> StorageError:
    return StorageError(code=code, message=message)


STORAGE_INVALID_RUN_ID = "storage_invalid_run_id"
STORAGE_INVALID_EVENT_TYPE = "storage_invalid_event_type"
STORAGE_INVALID_NUMERIC_BOOL = "storage_invalid_numeric_bool"
STORAGE_EVENT_HASH_CHAIN_MISMATCH = "storage_event_hash_chain_mismatch"
STORAGE_EVENT_IDEMPOTENCY_CONFLICT = "storage_event_idempotency_conflict"
STORAGE_PROJECTION_CHECKPOINT_REGRESSION = "storage_projection_checkpoint_regression"
STORAGE_PROJECTION_EVENT_GAP = "storage_projection_event_gap"
STORAGE_VECTOR_DIMENSION_MISMATCH = "storage_vector_dimension_mismatch"
STORAGE_VECTOR_INVALID_FLOAT = "storage_vector_invalid_float"
STORAGE_BACKEND_UNAVAILABLE = "storage_backend_unavailable"
STORAGE_PGVECTOR_MISSING = "storage_pgvector_missing"
STORAGE_MIGRATION_FAILED = "storage_migration_failed"
