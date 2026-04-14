from V1.contracts.phase_contracts import PHASE_CONTRACT_BY_ID
from V1.contracts.types import PhaseStatus, RoleResult
from V1.features.gate_evaluator import evaluate_phase_gate
from V1.features.output_parser import extract_missing_markers
from V1.features.prompt_loader import load_phase_prompt, load_role_prompt


def test_extract_missing_markers_detects_gaps() -> None:
    role_results = (
        RoleResult(role_name="architect", stdout="EVIDENCE: A", stderr="", exit_code=0),
        RoleResult(role_name="reviewer", stdout="VERDICT: PASS", stderr="", exit_code=0),
    )
    missing = extract_missing_markers(role_results, ("EVIDENCE:", "VERDICT:", "TRACE:"))
    assert missing == ("TRACE:",)


def test_evaluate_phase_gate_passes_with_valid_outputs() -> None:
    contract = PHASE_CONTRACT_BY_ID["phase_00"]
    role_results = tuple(
        RoleResult(
            role_name=role_name,
            stdout="EVIDENCE: present\nVERDICT: PASS",
            stderr="",
            exit_code=0,
        )
        for role_name in contract.required_roles
    )
    status, reason = evaluate_phase_gate(contract=contract, role_results=role_results)
    assert status == PhaseStatus.PASS
    assert "required role outputs" in reason


def test_evaluate_phase_gate_blocks_on_failed_role() -> None:
    contract = PHASE_CONTRACT_BY_ID["phase_00"]
    role_results = (
        RoleResult(role_name="architect", stdout="EVIDENCE: x\nVERDICT: PASS", stderr="", exit_code=0),
        RoleResult(role_name="validator", stdout="EVIDENCE: x\nVERDICT: FAIL", stderr="boom", exit_code=1),
    )
    status, reason = evaluate_phase_gate(contract=contract, role_results=role_results)
    assert status == PhaseStatus.BLOCKED
    assert "validator" in reason


def test_evaluate_phase_gate_returns_retry_for_quota_issue() -> None:
    contract = PHASE_CONTRACT_BY_ID["phase_00"]
    role_results = (
        RoleResult(role_name="architect", stdout="", stderr="", exit_code=0),
        RoleResult(
            role_name="implementer",
            stdout="",
            stderr="You're out of usage. Try later.",
            exit_code=1,
        ),
    )
    status, reason = evaluate_phase_gate(contract=contract, role_results=role_results)
    assert status == PhaseStatus.RETRY
    assert "quota" in reason


def test_prompt_loader_reads_role_and_phase_prompts() -> None:
    assert "Architect Role" in load_role_prompt("architect")
    assert "Phase 00 Prompt" in load_phase_prompt("phase_00")

