from __future__ import annotations

import pytest

from production_architecture.storage.errors import (
    STORAGE_BACKEND_UNAVAILABLE,
    STORAGE_INVALID_NUMERIC_BOOL,
    STORAGE_VECTOR_DIMENSION_MISMATCH,
    StorageError,
)
from production_architecture.storage import validate_storage_architecture_dict
from production_architecture.storage.postgres.event_store import PostgresEventStore
from production_architecture.storage.postgres.vector_store import _validate_embedding
from production_architecture.storage.service import StorageService
from production_architecture.storage.types import VectorMatch
from production_architecture.storage.vector.query import deterministic_rank


def test_validate_embedding_fail_closed() -> None:
    with pytest.raises(StorageError) as exc:
        _validate_embedding([1.0, 2.0], dim=3)
    assert exc.value.code == STORAGE_VECTOR_DIMENSION_MISMATCH
    with pytest.raises(StorageError) as exc_bool:
        _validate_embedding([1.0, True], dim=2)
    assert exc_bool.value.code == STORAGE_INVALID_NUMERIC_BOOL


def test_deterministic_rank_tie_breaks_by_chunk_id() -> None:
    rows = [
        VectorMatch(chunk_id="c2", content="", confidence=1.0, distance=0.1, metadata_json={}),
        VectorMatch(chunk_id="c1", content="", confidence=1.0, distance=0.1, metadata_json={}),
    ]
    assert [row.chunk_id for row in deterministic_rank(rows)] == ["c1", "c2"]


class _FakeEventStore:
    def append_event(self, **kwargs: object) -> dict[str, object]:
        return {"ok": True, "kwargs": kwargs}


class _FakeProjectionStore:
    def project_pending(self, projection_name: str, run_id: str) -> int:
        return 7


class _FakeVectorStore:
    def __init__(self) -> None:
        self.upserts: list[tuple[str, str]] = []

    def upsert_chunk_embedding(self, **kwargs: object) -> None:
        self.upserts.append((str(kwargs["run_id"]), str(kwargs["chunk_id"])))

    def query_similar(self, **_: object) -> list[VectorMatch]:
        return [
            VectorMatch(chunk_id="b", content="", confidence=1.0, distance=0.1, metadata_json={}),
            VectorMatch(chunk_id="a", content="", confidence=1.0, distance=0.1, metadata_json={}),
        ]


def test_storage_service_smoke() -> None:
    service = StorageService(
        event_store=_FakeEventStore(),
        projection_store=_FakeProjectionStore(),
        vector_store=_FakeVectorStore(),
    )
    event = service.record_event(run_id="r1")
    assert event["ok"] is True
    assert service.project_pending(projection_name="run_state", run_id="r1") == 7
    service.store_retrieval_chunks(
        run_id="r1",
        chunks=[{"chunk_id": "c1", "embedding": [0.1], "content": "x", "confidence": 0.9}],
    )
    ranked = service.retrieve_similar_chunks(run_id="r1", query_embedding=[0.1], top_k=2, min_confidence=0.0)
    assert [row.chunk_id for row in ranked] == ["a", "b"]


class _BrokenConnection:
    def cursor(self) -> None:
        raise RuntimeError("db down")


def test_event_store_maps_backend_errors_fail_closed() -> None:
    store = PostgresEventStore(_BrokenConnection())
    with pytest.raises(StorageError) as exc:
        store.get_latest_event("run-1")
    assert exc.value.code == STORAGE_BACKEND_UNAVAILABLE


def test_storage_contract_rejects_consistent_status_mismatch() -> None:
    errs = validate_storage_architecture_dict(
        {
            "schema": "sde.storage_architecture.v1",
            "schema_version": "1.0",
            "run_id": "r1",
            "mode": "guarded_pipeline",
            "status": "consistent",
            "projections": {"coverage": 0.5, "required_paths_count": 6, "present_paths_count": 3},
            "vector_memory": {},
            "consistency": {
                "trace_digest_matches_event_payload": True,
                "run_id_alignment_ok": True,
            },
        }
    )
    assert "storage_architecture_consistency_status_mismatch" in errs


def test_storage_contract_rejects_present_paths_exceeding_required() -> None:
    errs = validate_storage_architecture_dict(
        {
            "schema": "sde.storage_architecture.v1",
            "schema_version": "1.0",
            "run_id": "r1",
            "mode": "guarded_pipeline",
            "status": "degraded",
            "projections": {"coverage": 0.5, "required_paths_count": 1, "present_paths_count": 2},
            "vector_memory": {},
            "consistency": {
                "trace_digest_matches_event_payload": False,
                "run_id_alignment_ok": True,
            },
        }
    )
    assert "storage_architecture_projections_present_paths_count_exceeds_required" in errs
