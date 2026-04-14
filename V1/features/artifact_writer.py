"""Persist deterministic phase artifacts."""

from __future__ import annotations

from pathlib import Path

from V1.contracts.types import PhaseResult
from V1.utils.constants import ARTIFACTS_DIR


def write_phase_artifact(phase_result: PhaseResult) -> Path:
    phase_dir = ARTIFACTS_DIR / phase_result.phase_id
    phase_dir.mkdir(parents=True, exist_ok=True)
    output_file = phase_dir / "result.md"
    lines = [
        f"# {phase_result.phase_id}",
        f"status: {phase_result.status.value}",
        f"reason: {phase_result.reason}",
    ]
    for role_result in phase_result.role_results:
        lines.append(f"## {role_result.role_name}")
        lines.append(f"exit_code: {role_result.exit_code}")
        lines.append(role_result.stdout.strip())
    output_file.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return output_file

