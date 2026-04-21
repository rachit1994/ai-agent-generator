# Folder: `src/agent_organization/reviewer_evaluator_agents`

## Why this folder exists
This folder groups code and artifacts for `reviewer_evaluator_agents` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py` (file): Reviewer/evaluator contract constants for payload validation.
- `findings.py` (file): Deterministic finding composition from static gates, manifest, and terminal state.
- `evaluator.py` (file): Evaluator authority checks and review payload validation.
- `runtime.py` (file): Public runtime facade consumed by review-gating modules.
- `surface.py` (file): Feature surface metadata and integration references.
- `tests/` (folder): Unit tests for reviewer/evaluator runtime behavior.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
