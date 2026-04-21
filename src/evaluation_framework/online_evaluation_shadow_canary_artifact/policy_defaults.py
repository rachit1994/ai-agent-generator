"""Single-source defaults and identifiers for online-evaluation policy."""

from __future__ import annotations

MIN_SAMPLE_SIZE = 5
MAX_ERROR_RATE_DELTA = 0.05
MAX_LATENCY_P95_DELTA_MS = 50.0
MIN_QUALITY_DELTA = 0.0

GATE_ID_MIN_SAMPLE = "min_sample"
GATE_ID_ERROR_RATE_DELTA = "error_rate_delta"
GATE_ID_LATENCY_P95_DELTA_MS = "latency_p95_delta_ms"
GATE_ID_QUALITY_DELTA = "quality_delta"

MANDATORY_GATE_IDS = (
    GATE_ID_MIN_SAMPLE,
    GATE_ID_ERROR_RATE_DELTA,
    GATE_ID_LATENCY_P95_DELTA_MS,
    GATE_ID_QUALITY_DELTA,
)
