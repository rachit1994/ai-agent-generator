# Folder: `src/workflow_pipelines/strategy_overlay`

## Why this folder exists
This folder groups code and artifacts for `strategy_overlay` within the repository architecture.

## What is present
- `execution_modes` (folder): Groups related implementation for this subdomain boundary.
- `__init__.py` (file): Public exports for strategy-overlay runtime and contracts.
- `contracts.py` (file): Contract constants and fail-closed validators for overlay artifacts.
- `runtime.py` (file): Deterministic strategy-overlay derivation.
- `surface.py` (file): Feature-surface metadata.
- `strategy_overlay_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `tests/` (folder): Focused runtime and contract tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
