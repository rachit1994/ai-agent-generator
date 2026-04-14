from V1.contracts.phase_contracts import PHASE_CONTRACTS
from V1.steps.index import STEP_FUNCTION_BY_PHASE_ID
from V1.utils.constants import PROMPTS_DIR


def test_all_phases_have_step_function() -> None:
    phase_ids = {contract.phase_id for contract in PHASE_CONTRACTS}
    step_phase_ids = set(STEP_FUNCTION_BY_PHASE_ID.keys())
    assert phase_ids == step_phase_ids


def test_all_phases_have_prompt_file() -> None:
    missing = []
    for contract in PHASE_CONTRACTS:
        prompt_path = PROMPTS_DIR / "phases" / f"{contract.phase_id}.md"
        if not prompt_path.exists():
            missing.append(str(prompt_path))
    assert missing == []


def test_all_role_prompts_exist() -> None:
    role_files = ("architect.md", "implementer.md", "validator.md", "reviewer.md")
    for role_file in role_files:
        assert (PROMPTS_DIR / "roles" / role_file).exists()

