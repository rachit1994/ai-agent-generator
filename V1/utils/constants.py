"""Hardcoded constants for V1 orchestration."""

from __future__ import annotations

from pathlib import Path

V1_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = V1_ROOT / "prompts"
ARTIFACTS_DIR = V1_ROOT / "artifacts"
DEFAULT_TIMEOUT_SECONDS = 60

