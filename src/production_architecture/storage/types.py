"""Common storage types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JsonDict = dict[str, Any]


@dataclass(slots=True, frozen=True)
class EventRecord:
    event_id: str
    run_id: str
    event_seq: int
    idempotency_key: str
    event_type: str
    payload_json: JsonDict
    payload_sha256: str
    prev_payload_sha256: str
    created_at: str


@dataclass(slots=True, frozen=True)
class ProjectionCheckpoint:
    projection_name: str
    last_event_seq: int


@dataclass(slots=True, frozen=True)
class VectorMatch:
    chunk_id: str
    content: str
    confidence: float
    distance: float
    metadata_json: JsonDict
