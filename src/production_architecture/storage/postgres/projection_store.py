"""Postgres projection store."""

from __future__ import annotations

import json
from typing import Any

from production_architecture.storage.errors import (
    STORAGE_BACKEND_UNAVAILABLE,
    STORAGE_PROJECTION_CHECKPOINT_REGRESSION,
    STORAGE_PROJECTION_EVENT_GAP,
    StorageError,
    fail,
)
from production_architecture.storage.projections.processor import apply_events_to_run_state
from production_architecture.storage.types import ProjectionCheckpoint


class PostgresProjectionStore:
    def __init__(self, conn: Any, event_store: Any) -> None:
        self._conn = conn
        self._event_store = event_store

    def get_checkpoint(self, projection_name: str) -> ProjectionCheckpoint:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT last_event_seq FROM pa_projection_checkpoint WHERE projection_name = %s",
                    (projection_name,),
                )
                row = cur.fetchone()
                if row is None:
                    return ProjectionCheckpoint(projection_name=projection_name, last_event_seq=0)
                return ProjectionCheckpoint(projection_name=projection_name, last_event_seq=int(row[0]))
        except Exception as exc:
            raise fail(STORAGE_BACKEND_UNAVAILABLE, str(exc)) from exc

    def _checkpoint_key(self, projection_name: str, run_id: str) -> str:
        return f"{projection_name}:{run_id}"

    def project_pending(self, projection_name: str, run_id: str) -> int:
        checkpoint_key = self._checkpoint_key(projection_name, run_id)
        checkpoint = self.get_checkpoint(checkpoint_key)
        events = self._event_store.list_events(run_id=run_id, from_seq=checkpoint.last_event_seq, limit=100000)
        expected_seq = checkpoint.last_event_seq + 1
        for event in events:
            if event.event_seq != expected_seq:
                raise fail(STORAGE_PROJECTION_EVENT_GAP, "event sequence gap detected")
            expected_seq += 1
        if not events:
            return checkpoint.last_event_seq
        latest_seq = events[-1].event_seq
        if latest_seq < checkpoint.last_event_seq:
            raise fail(STORAGE_PROJECTION_CHECKPOINT_REGRESSION, "checkpoint regression")
        summary = apply_events_to_run_state(events)
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pa_projection_run_state (run_id, latest_event_seq, status, summary_json) VALUES (%s,%s,%s,%s) ON CONFLICT (run_id) DO UPDATE SET latest_event_seq = EXCLUDED.latest_event_seq, status = EXCLUDED.status, summary_json = EXCLUDED.summary_json, updated_at = NOW()",
                    (run_id, latest_seq, "consistent", json.dumps(summary)),
                )
                cur.execute(
                    "INSERT INTO pa_projection_checkpoint (projection_name, last_event_seq) VALUES (%s,%s) ON CONFLICT (projection_name) DO UPDATE SET last_event_seq = EXCLUDED.last_event_seq, updated_at = NOW()",
                    (checkpoint_key, latest_seq),
                )
            self._conn.commit()
            return latest_seq
        except StorageError:
            raise
        except Exception as exc:
            raise fail(STORAGE_BACKEND_UNAVAILABLE, str(exc)) from exc
