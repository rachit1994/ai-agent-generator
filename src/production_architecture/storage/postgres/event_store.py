"""Postgres event store."""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from production_architecture.storage.errors import (
    STORAGE_BACKEND_UNAVAILABLE,
    STORAGE_EVENT_HASH_CHAIN_MISMATCH,
    STORAGE_EVENT_IDEMPOTENCY_CONFLICT,
    STORAGE_INVALID_EVENT_TYPE,
    STORAGE_INVALID_RUN_ID,
    StorageError,
    fail,
)
from production_architecture.storage.types import EventRecord, JsonDict


def _validate_run_id(run_id: str) -> None:
    if not isinstance(run_id, str) or not run_id.strip():
        raise fail(STORAGE_INVALID_RUN_ID, "run_id must be a non-empty string")


def _validate_event_type(event_type: str) -> None:
    if not isinstance(event_type, str) or not event_type.strip():
        raise fail(STORAGE_INVALID_EVENT_TYPE, "event_type must be a non-empty string")


def _to_record(row: Any) -> EventRecord:
    return EventRecord(
        event_id=row[0],
        run_id=row[1],
        event_seq=int(row[2]),
        idempotency_key=row[3],
        event_type=row[4],
        payload_json=row[5],
        payload_sha256=row[6],
        prev_payload_sha256=row[7],
        created_at=str(row[8]),
    )


class PostgresEventStore:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    def append_event(
        self,
        *,
        run_id: str,
        idempotency_key: str,
        event_type: str,
        payload_json: JsonDict,
        payload_sha256: str,
        prev_payload_sha256: str,
    ) -> EventRecord:
        _validate_run_id(run_id)
        _validate_event_type(event_type)
        try:
            with self._conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (run_id,))
                cur.execute(
                    "SELECT event_id,run_id,event_seq,idempotency_key,event_type,payload_json,payload_sha256,prev_payload_sha256,created_at FROM pa_events WHERE run_id = %s AND idempotency_key = %s",
                    (run_id, idempotency_key),
                )
                existing = cur.fetchone()
                if existing is not None:
                    existing_rec = _to_record(existing)
                    if existing_rec.payload_sha256 != payload_sha256:
                        raise fail(STORAGE_EVENT_IDEMPOTENCY_CONFLICT, "idempotency key conflict")
                    return existing_rec
                cur.execute(
                    "SELECT event_seq,payload_sha256 FROM pa_events WHERE run_id = %s ORDER BY event_seq DESC LIMIT 1",
                    (run_id,),
                )
                last = cur.fetchone()
                if last is None:
                    expected_prev = ""
                    next_seq = 1
                else:
                    expected_prev = str(last[1])
                    next_seq = int(last[0]) + 1
                if expected_prev != prev_payload_sha256:
                    raise fail(STORAGE_EVENT_HASH_CHAIN_MISMATCH, "previous hash mismatch")
                if not payload_sha256:
                    payload_sha256 = hashlib.sha256(
                        json.dumps(payload_json, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    ).hexdigest()
                event_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO pa_events (event_id, run_id, event_seq, idempotency_key, event_type, payload_json, payload_sha256, prev_payload_sha256) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING event_id,run_id,event_seq,idempotency_key,event_type,payload_json,payload_sha256,prev_payload_sha256,created_at",
                    (event_id, run_id, next_seq, idempotency_key, event_type, json.dumps(payload_json), payload_sha256, prev_payload_sha256),
                )
                row = cur.fetchone()
            self._conn.commit()
            return _to_record(row)
        except StorageError:
            raise
        except Exception as exc:
            raise fail(STORAGE_BACKEND_UNAVAILABLE, str(exc)) from exc

    def get_latest_event(self, run_id: str) -> EventRecord | None:
        _validate_run_id(run_id)
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT event_id,run_id,event_seq,idempotency_key,event_type,payload_json,payload_sha256,prev_payload_sha256,created_at FROM pa_events WHERE run_id = %s ORDER BY event_seq DESC LIMIT 1",
                    (run_id,),
                )
                row = cur.fetchone()
                return None if row is None else _to_record(row)
        except Exception as exc:
            raise fail(STORAGE_BACKEND_UNAVAILABLE, str(exc)) from exc

    def list_events(self, run_id: str, from_seq: int, limit: int) -> list[EventRecord]:
        _validate_run_id(run_id)
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT event_id,run_id,event_seq,idempotency_key,event_type,payload_json,payload_sha256,prev_payload_sha256,created_at FROM pa_events WHERE run_id = %s AND event_seq > %s ORDER BY event_seq ASC LIMIT %s",
                    (run_id, from_seq, limit),
                )
                return [_to_record(row) for row in cur.fetchall()]
        except Exception as exc:
            raise fail(STORAGE_BACKEND_UNAVAILABLE, str(exc)) from exc
