from __future__ import annotations

from core_components.self_learning_loop.policy_defaults import (
    GATE_ID_CONTRADICTION_RATE,
    GATE_ID_MIN_EXAMPLES,
    GATE_ID_NOVELTY_SCORE,
    GATE_ID_REGRESSION_RATE,
    GATE_ID_VERIFIER_PASS_RATE,
    MANDATORY_GATE_IDS,
)


def test_policy_gate_ids_are_stable_and_exact() -> None:
    assert MANDATORY_GATE_IDS == (
        GATE_ID_MIN_EXAMPLES,
        GATE_ID_VERIFIER_PASS_RATE,
        GATE_ID_REGRESSION_RATE,
        GATE_ID_NOVELTY_SCORE,
        GATE_ID_CONTRADICTION_RATE,
    )
