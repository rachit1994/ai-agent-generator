# `src/services/orchestrator/runtime/sde`

- Purpose: SDE agent runtime package for orchestration execution, CTO gate artifacts, and evaluation.
- V1 artifacts: `runner.py` emits `review.json`, `token_context.json`, `balanced_gates` in `summary.json`, multi-file `outputs/`, and `run.log`. Gate logic lives in `cto_gates.py`.
- Scope: Folder path is `src/services/orchestrator/runtime/sde`.
- Should contain: Should contain implementation files, schemas, tests, or docs directly relevant to `services/orchestrator/runtime/sde`.
- Should not contain: Should not contain unrelated domain logic or artifacts owned by sibling folders under `src/`.
- Keep files here focused, small, and aligned with this folder contract.
