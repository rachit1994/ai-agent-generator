"""Single-source defaults and identifiers for self-learning-loop policy."""

from __future__ import annotations

MIN_ELIGIBLE_EXAMPLES = 5
MIN_VERIFIER_PASS_RATE = 0.9
MAX_REGRESSION_RATE = 0.1
MIN_NOVELTY_SCORE = 0.5
MAX_CONTRADICTION_RATE = 0.05

GATE_ID_MIN_EXAMPLES = "min_examples"
GATE_ID_VERIFIER_PASS_RATE = "verifier_pass_rate"
GATE_ID_REGRESSION_RATE = "regression_rate"
GATE_ID_NOVELTY_SCORE = "novelty_score"
GATE_ID_CONTRADICTION_RATE = "contradiction_rate"

MANDATORY_GATE_IDS = (
    GATE_ID_MIN_EXAMPLES,
    GATE_ID_VERIFIER_PASS_RATE,
    GATE_ID_REGRESSION_RATE,
    GATE_ID_NOVELTY_SCORE,
    GATE_ID_CONTRADICTION_RATE,
)
