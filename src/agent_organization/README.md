# Folder: `src/agent_organization`

## Why this folder exists
This folder groups code and artifacts for `agent_organization` within the repository architecture.

## What is present
- `interaction_contracts` (folder): Defines machine-checkable interface and schema expectations.
- `junior_mid_senior_architect_agent_roles` (folder): Groups related implementation for this subdomain boundary.
- `learning_practice_agents` (folder): Groups related implementation for this subdomain boundary.
- `manager_specialist_careerstrategy_agents` (folder): Groups related implementation for this subdomain boundary.
- `reviewer_evaluator_agents` (folder): Implements review and gating logic for quality/safety decisions.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
