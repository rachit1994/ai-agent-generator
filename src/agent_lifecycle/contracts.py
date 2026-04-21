"""Contracts for deterministic local agent lifecycle runtime."""

from __future__ import annotations

LIFECYCLE_SCHEMA_VERSION = "1.0"
LIFECYCLE_STAGES: tuple[str, str, str, str] = ("junior", "mid", "senior", "architect")
PROMOTION_THRESHOLDS: dict[str, float] = {"junior": 0.5, "mid": 0.7, "senior": 0.9, "architect": 1.0}
DEMOTION_FLOORS: dict[str, float] = {"junior": 0.0, "mid": 0.45, "senior": 0.65, "architect": 0.85}
STAGNATION_EPSILON = 0.02
STAGNATION_MIN_OBSERVATIONS = 3
