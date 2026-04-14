"""Evaluate role outputs against phase gate contracts."""

from __future__ import annotations

from V1.contracts.types import PhaseContract, PhaseStatus, RoleResult
from V1.features.output_parser import extract_missing_markers

QUOTA_MARKERS: tuple[str, ...] = (
    "you're out of usage",
    "out of usage",
    "usage limit",
    "rate limit",
)


def evaluate_phase_gate(contract: PhaseContract, role_results: tuple[RoleResult, ...]) -> tuple[PhaseStatus, str]:
    combined_streams = "\n".join(result.stdout + "\n" + result.stderr for result in role_results).lower()
    if any(marker in combined_streams for marker in QUOTA_MARKERS):
        return PhaseStatus.RETRY, "cursor usage quota reached; retry when limits reset"
    failed_roles = tuple(result.role_name for result in role_results if result.exit_code != 0)
    if failed_roles:
        return PhaseStatus.BLOCKED, f"role command failures: {', '.join(failed_roles)}"
    missing_markers = extract_missing_markers(role_results, contract.required_markers)
    if missing_markers:
        return PhaseStatus.RETRY, f"missing markers: {', '.join(missing_markers)}"
    return PhaseStatus.PASS, "all required role outputs and markers are present"

