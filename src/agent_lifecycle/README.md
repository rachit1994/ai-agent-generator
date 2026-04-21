# Folder: `src/agent_lifecycle`

## Why this folder exists
This folder groups code and artifacts for `agent_lifecycle` within the repository architecture.

## What is present
- `autonomy_levels_trust_progression` (folder): Groups related implementation for this subdomain boundary.
- `demotion_logic` (folder): Groups related implementation for this subdomain boundary.
- `lifecycle_stages_graph` (folder): Groups related implementation for this subdomain boundary.
- `promotion_rules` (folder): Groups related implementation for this subdomain boundary.
- `recertification_decay` (folder): Groups related implementation for this subdomain boundary.
- `stagnation_detection` (folder): Groups related implementation for this subdomain boundary.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py` (file): Lifecycle thresholds and stage constants.
- `runtime.py` (file): Deterministic lifecycle decision and artifact payload builders.
- `tests/` (folder): Unit tests for lifecycle runtime behavior.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
