# Folder: `src/scalability_strategy`

## Why this folder exists
This folder groups code and artifacts for `scalability_strategy` within the repository architecture.

## What is present
- `event_scaling` (folder): Handles event lineage, event contracts, or event persistence logic.
- `memory_scaling` (folder): Implements memory handling and memory-related lifecycle logic.
- `multi_agent_scaling` (folder): Groups related implementation for this subdomain boundary.
- `replay_scaling` (folder): Groups related implementation for this subdomain boundary.
- `full_build_order_progression` (folder): Deterministic stage-order progression runtime and contracts.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py` (file): Scalability strategy artifact contract and validator.
- `runtime.py` (file): Deterministic scalability strategy derivation.
- `surface.py` (file): Top-level feature-surface metadata.
- `tests/` (folder): Unit tests for top-level scalability strategy runtime.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
