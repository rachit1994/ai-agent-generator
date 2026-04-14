from V1.contracts.types import PhaseResult
from V1.features.phase_runner import run_phase


def run_phase_00() -> PhaseResult:
    return run_phase("phase_00")

