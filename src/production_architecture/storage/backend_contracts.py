"""Storage backend contracts."""

from __future__ import annotations

from typing import Protocol

from .types import EventRecord, JsonDict, ProjectionCheckpoint, VectorMatch


class EventStoreBackend(Protocol):
    def append_event(
        self,
        *,
        run_id: str,
        idempotency_key: str,
        event_type: str,
        payload_json: JsonDict,
        payload_sha256: str,
        prev_payload_sha256: str,
    ) -> EventRecord: ...

    def get_latest_event(self, run_id: str) -> EventRecord | None: ...

    def list_events(self, run_id: str, from_seq: int, limit: int) -> list[EventRecord]: ...


class ProjectionBackend(Protocol):
    def get_checkpoint(self, projection_name: str) -> ProjectionCheckpoint: ...

    def project_pending(self, projection_name: str, run_id: str) -> int: ...


class VectorMemoryBackend(Protocol):
    def upsert_chunk_embedding(
        self,
        *,
        run_id: str,
        chunk_id: str,
        embedding: list[float],
        content: str,
        confidence: float,
        metadata_json: JsonDict,
    ) -> None: ...

    def query_similar(
        self,
        *,
        run_id: str,
        query_embedding: list[float],
        top_k: int,
        min_confidence: float,
    ) -> list[VectorMatch]: ...


class StorageBackend(EventStoreBackend, ProjectionBackend, VectorMemoryBackend, Protocol):
    pass
