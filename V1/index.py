"""Entrypoint for running one V1 persona phase."""

from __future__ import annotations

from V1.contracts.types import PhaseResult
from V1.steps.index import STEP_FUNCTION_BY_PHASE_ID


def run_one_phase(phase_id: str) -> PhaseResult:
    step_fn = STEP_FUNCTION_BY_PHASE_ID.get(phase_id)
    if step_fn is None:
        known = ", ".join(sorted(STEP_FUNCTION_BY_PHASE_ID))
        raise ValueError(f"Unknown phase id '{phase_id}'. Known phase ids: {known}")
    return step_fn()


if __name__ == "__main__":
    # Hardcoded entrypoint for deterministic local execution.
    result = run_one_phase("phase_00")
    print(f"{result.phase_id}: {result.status.value} ({result.reason})")

