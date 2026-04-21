# Folder: `src/human_professional_evolution_model`

## Why this folder exists
This folder groups code and artifacts for `human_professional_evolution_model` within the repository architecture.

## What is present
- `career_progression_model` (folder): Wraps model-facing logic and invocation behavior.
- `deliberate_practice` (folder): Groups related implementation for this subdomain boundary.
- `feedback_loops` (folder): Groups related implementation for this subdomain boundary.
- `human_growth_loop` (folder): Groups related implementation for this subdomain boundary.
- `human_to_agent_behavior_mapping` (folder): Groups related implementation for this subdomain boundary.
- `institutional_memory` (folder): Implements memory handling and memory-related lifecycle logic.
- `mentorship_operating_model` (folder): Wraps model-facing logic and invocation behavior.
- `performance_review_cycle` (folder): Implements review and gating logic for quality/safety decisions.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py` (file): Human evolution runtime constants.
- `runtime.py` (file): Deterministic evolution decision and artifact builders.
- `tests/` (folder): Unit tests for runtime behavior.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
