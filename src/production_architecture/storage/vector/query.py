"""Deterministic vector ranking helpers."""

from __future__ import annotations

from production_architecture.storage.types import VectorMatch


def deterministic_rank(matches: list[VectorMatch]) -> list[VectorMatch]:
    return sorted(matches, key=lambda row: (row.distance, row.chunk_id))
