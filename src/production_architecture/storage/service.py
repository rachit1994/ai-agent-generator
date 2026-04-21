"""Unified storage service API."""

from __future__ import annotations

from production_architecture.storage.vector.query import deterministic_rank


class StorageService:
    def __init__(self, *, event_store: object, projection_store: object, vector_store: object) -> None:
        self._event_store = event_store
        self._projection_store = projection_store
        self._vector_store = vector_store

    def record_event(self, **kwargs: object) -> object:
        return self._event_store.append_event(**kwargs)

    def project_pending(self, *, projection_name: str, run_id: str) -> int:
        return self._projection_store.project_pending(projection_name, run_id)

    def store_retrieval_chunks(self, *, run_id: str, chunks: list[dict[str, object]]) -> None:
        for chunk in chunks:
            self._vector_store.upsert_chunk_embedding(
                run_id=run_id,
                chunk_id=str(chunk["chunk_id"]),
                embedding=list(chunk["embedding"]),
                content=str(chunk["content"]),
                confidence=float(chunk["confidence"]),
                metadata_json=dict(chunk.get("metadata_json", {})),
            )

    def retrieve_similar_chunks(
        self,
        *,
        run_id: str,
        query_embedding: list[float],
        top_k: int,
        min_confidence: float,
    ) -> list[object]:
        matches = self._vector_store.query_similar(
            run_id=run_id,
            query_embedding=query_embedding,
            top_k=top_k,
            min_confidence=min_confidence,
        )
        return deterministic_rank(matches)
