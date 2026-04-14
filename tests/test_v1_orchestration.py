from pathlib import Path

from V1.contracts.types import PhaseStatus, RoleResult
from V1.features import phase_runner
from V1.index import run_one_phase


def test_run_one_phase_dry_run(monkeypatch) -> None:
    monkeypatch.setattr(
        phase_runner,
        "invoke_cursor_cli",
        lambda role_name, prompt_text: RoleResult(
            role_name=role_name,
            stdout="EVIDENCE: dry-run\nVERDICT: PASS",
            stderr="",
            exit_code=0,
        ),
    )
    monkeypatch.setattr(phase_runner, "write_phase_artifact", lambda phase_result: Path("/tmp/mock"))
    result = run_one_phase("phase_00")
    assert result.phase_id == "phase_00"
    assert result.status == PhaseStatus.PASS


def test_run_one_phase_rejects_unknown_phase() -> None:
    try:
        run_one_phase("phase_99")
    except ValueError as exc:
        assert "Unknown phase id" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown phase id")

