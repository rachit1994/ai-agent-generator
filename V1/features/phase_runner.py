"""Generic runner used by every phase step module."""

from __future__ import annotations

from V1.contracts.phase_contracts import PHASE_CONTRACT_BY_ID
from V1.contracts.types import PhaseResult
from V1.features.artifact_writer import write_phase_artifact
from V1.features.cli_runner import invoke_cursor_cli
from V1.features.gate_evaluator import evaluate_phase_gate
from V1.features.prompt_loader import load_phase_prompt, load_role_prompt


def run_phase(phase_id: str) -> PhaseResult:
    contract = PHASE_CONTRACT_BY_ID[phase_id]
    phase_prompt = load_phase_prompt(phase_id)
    role_results = []
    for role_name in contract.required_roles:
        role_prompt = load_role_prompt(role_name)
        full_prompt = (
            f"{role_prompt}\n\n"
            f"PHASE_ID: {phase_id}\n"
            f"PHASE_TITLE: {contract.phase_title}\n"
            f"PHASE_PROMPT:\n{phase_prompt}\n"
        )
        role_results.append(invoke_cursor_cli(role_name=role_name, prompt_text=full_prompt))
    status, reason = evaluate_phase_gate(contract=contract, role_results=tuple(role_results))
    result = PhaseResult(
        phase_id=phase_id,
        status=status,
        reason=reason,
        role_results=tuple(role_results),
    )
    write_phase_artifact(result)
    return result

