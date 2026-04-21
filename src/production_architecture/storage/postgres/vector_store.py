"""Postgres vector store."""

from __future__ import annotations

import math
import uuid
from typing import Any

from production_architecture.storage.errors import (
    STORAGE_BACKEND_UNAVAILABLE,
    STORAGE_INVALID_NUMERIC_BOOL,
    STORAGE_VECTOR_DIMENSION_MISMATCH,
    STORAGE_VECTOR_INVALID_FLOAT,
    StorageError,
    fail,
)
from production_architecture.storage.types import JsonDict, VectorMatch


def _validate_embedding(values: list[float], dim: int) -> None:
    if len(values) != dim:
        raise fail(STORAGE_VECTOR_DIMENSION_MISMATCH, f"expected dim={dim}")
    for value in values:
        if isinstance(value, bool):
            raise fail(STORAGE_INVALID_NUMERIC_BOOL, "boolean is not a valid float")
        if not isinstance(value, (float, int)):
            raise fail(STORAGE_VECTOR_INVALID_FLOAT, "embedding value must be numeric")
        if not math.isfinite(float(value)):
            raise fail(STORAGE_VECTOR_INVALID_FLOAT, "embedding value must be finite")


class PostgresVectorStore:
    def __init__(self, conn: Any, *, vector_dim: int) -> None:
        self._conn = conn
        self._vector_dim = vector_dim

    def upsert_chunk_embedding(
        self,
        *,
        run_id: str,
        chunk_id: str,
        embedding: list[float],
        content: str,
        confidence: float,
        metadata_json: JsonDict,
    ) -> None:
        _validate_embedding(embedding, self._vector_dim)
        vector_id = str(uuid.uuid4())
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pa_vectors (vector_id, run_id, chunk_id, embedding, content, confidence, metadata_json) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (run_id, chunk_id) DO UPDATE SET embedding = EXCLUDED.embedding, content = EXCLUDED.content, confidence = EXCLUDED.confidence, metadata_json = EXCLUDED.metadata_json",
                    (vector_id, run_id, chunk_id, embedding, content, confidence, metadata_json),
                )
            self._conn.commit()
        except StorageError:
            raise
        except Exception as exc:
            raise fail(STORAGE_BACKEND_UNAVAILABLE, str(exc)) from exc

    def query_similar(
        self,
        *,
        run_id: str,
        query_embedding: list[float],
        top_k: int,
        min_confidence: float,
    ) -> list[VectorMatch]:
        _validate_embedding(query_embedding, self._vector_dim)
        if top_k <= 0:
            raise fail(STORAGE_VECTOR_INVALID_FLOAT, "top_k must be positive")
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT chunk_id,content,confidence,metadata_json,(embedding <-> %s) AS distance FROM pa_vectors WHERE run_id = %s AND confidence >= %s ORDER BY distance ASC, chunk_id ASC LIMIT %s",
                    (query_embedding, run_id, min_confidence, top_k),
                )
                rows = cur.fetchall()
        except Exception as exc:
            raise fail(STORAGE_BACKEND_UNAVAILABLE, str(exc)) from exc
        return [
            VectorMatch(
                chunk_id=row[0],
                content=row[1],
                confidence=float(row[2]),
                metadata_json=row[3],
                distance=float(row[4]),
            )
            for row in rows
        ]
