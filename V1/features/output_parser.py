"""Parse role outputs for evidence and verdict markers."""

from __future__ import annotations

from V1.contracts.types import RoleResult


def extract_missing_markers(role_results: tuple[RoleResult, ...], required_markers: tuple[str, ...]) -> tuple[str, ...]:
    combined = "\n".join(result.stdout for result in role_results)
    return tuple(marker for marker in required_markers if marker not in combined)

