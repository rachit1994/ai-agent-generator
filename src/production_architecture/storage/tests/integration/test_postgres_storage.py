from __future__ import annotations

import hashlib
import json
import os
import uuid

import pytest

from production_architecture.storage.errors import StorageError
from production_architecture.storage.postgres.event_store import PostgresEventStore
from production_architecture.storage.postgres.migrations import apply_migrations
from production_architecture.storage.postgres.projection_store import PostgresProjectionStore
from production_architecture.storage.postgres.vector_store import PostgresVectorStore
from production_architecture.storage.service import StorageService

SKIP_REASON_PSYCOPG_UNAVAILABLE = "psycopg is not installed; postgres integration tests require psycopg"
psycopg = pytest.importorskip("psycopg", reason=SKIP_REASON_PSYCOPG_UNAVAILABLE)
SKIP_REASON_PG_DSN_UNSET = "PA_STORAGE_DB_DSN is not set; refusing implicit external DB dependency"


def _dsn() -> str:
    dsn = os.getenv("PA_STORAGE_DB_DSN", "").strip()
    if not dsn:
        pytest.skip(SKIP_REASON_PG_DSN_UNSET)
    return dsn


def _vector_dim() -> int:
    raw = os.getenv("PA_VECTOR_DIM", "").strip()
    if not raw:
        return 1536
    return int(raw)


@pytest.fixture()
def conn():
    connection = psycopg.connect(_dsn(), autocommit=False)
    try:
        apply_migrations(connection, vector_dim=_vector_dim())
        yield connection
    finally:
        connection.close()


def _payload_sha(value: dict[str, object]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def test_event_projection_vector_flow(conn) -> None:
    run_id = f"run-{uuid.uuid4()}"
    events = PostgresEventStore(conn)
    projections = PostgresProjectionStore(conn, events)
    vectors = PostgresVectorStore(conn, vector_dim=_vector_dim())
    service = StorageService(event_store=events, projection_store=projections, vector_store=vectors)
    payload_one = {"type": "start"}
    sha_one = _payload_sha(payload_one)
    e1 = service.record_event(
        run_id=run_id,
        idempotency_key="k1",
        event_type="started",
        payload_json=payload_one,
        payload_sha256=sha_one,
        prev_payload_sha256="",
    )
    assert e1.event_seq == 1
    payload_two = {"type": "complete"}
    sha_two = _payload_sha(payload_two)
    e2 = service.record_event(
        run_id=run_id,
        idempotency_key="k2",
        event_type="completed",
        payload_json=payload_two,
        payload_sha256=sha_two,
        prev_payload_sha256=sha_one,
    )
    assert e2.event_seq == 2
    assert service.project_pending(projection_name="run_state", run_id=run_id) == 2
    embedding = [0.0] * _vector_dim()
    embedding[0] = 1.0
    service.store_retrieval_chunks(
        run_id=run_id,
        chunks=[
            {"chunk_id": "a", "embedding": embedding, "content": "A", "confidence": 0.9},
            {"chunk_id": "b", "embedding": embedding, "content": "B", "confidence": 0.9},
        ],
    )
    matches = service.retrieve_similar_chunks(
        run_id=run_id,
        query_embedding=embedding,
        top_k=2,
        min_confidence=0.0,
    )
    assert [row.chunk_id for row in matches] == ["a", "b"]


def test_hash_chain_fail_closed(conn) -> None:
    run_id = f"run-{uuid.uuid4()}"
    events = PostgresEventStore(conn)
    payload = {"x": 1}
    sha = _payload_sha(payload)
    events.append_event(
        run_id=run_id,
        idempotency_key="k1",
        event_type="x",
        payload_json=payload,
        payload_sha256=sha,
        prev_payload_sha256="",
    )
    with pytest.raises(StorageError):
        events.append_event(
            run_id=run_id,
            idempotency_key="k2",
            event_type="y",
            payload_json={"x": 2},
            payload_sha256=_payload_sha({"x": 2}),
            prev_payload_sha256="bad",
        )


def test_projection_checkpoint_isolated_per_run(conn) -> None:
    events = PostgresEventStore(conn)
    projections = PostgresProjectionStore(conn, events)
    run_one = f"run-{uuid.uuid4()}"
    run_two = f"run-{uuid.uuid4()}"

    payload_one = {"type": "r1"}
    sha_one = _payload_sha(payload_one)
    events.append_event(
        run_id=run_one,
        idempotency_key="k1",
        event_type="started",
        payload_json=payload_one,
        payload_sha256=sha_one,
        prev_payload_sha256="",
    )
    assert projections.project_pending(projection_name="run_state", run_id=run_one) == 1

    payload_two = {"type": "r2"}
    sha_two = _payload_sha(payload_two)
    events.append_event(
        run_id=run_two,
        idempotency_key="k1",
        event_type="started",
        payload_json=payload_two,
        payload_sha256=sha_two,
        prev_payload_sha256="",
    )
    # A checkpoint written for run_one must not suppress run_two projection.
    assert projections.project_pending(projection_name="run_state", run_id=run_two) == 1


def test_postgres_integration_skip_reason_is_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PA_STORAGE_DB_DSN", raising=False)
    with pytest.raises(pytest.skip.Exception) as exc:
        _dsn()
    assert str(exc.value) == SKIP_REASON_PG_DSN_UNSET
