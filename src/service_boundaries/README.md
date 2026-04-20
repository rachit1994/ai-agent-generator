# Folder: `src/service_boundaries`

## Why this folder exists
This folder groups code and artifacts for `service_boundaries` within the repository architecture.

## What is present
- `autonomy_sla_monitor` (folder): Groups related implementation for this subdomain boundary.
- `binary_release_gate_engine` (folder): Implements gate logic used to approve/reject progression.
- `boundary_contracts` (folder): Defines machine-checkable interface and schema expectations.
- `canary_rollout` (folder): Groups related implementation for this subdomain boundary.
- `capability_graph` (folder): Groups related implementation for this subdomain boundary.
- `chaos_simulator` (folder): Groups related implementation for this subdomain boundary.
- `evaluation` (folder): Groups related implementation for this subdomain boundary.
- `event_store` (folder): Handles event lineage, event contracts, or event persistence logic.
- `identity_authz` (folder): Groups related implementation for this subdomain boundary.
- `incident_ops` (folder): Groups related implementation for this subdomain boundary.
- `learning_update` (folder): Groups related implementation for this subdomain boundary.
- `lifecycle_governance` (folder): Groups related implementation for this subdomain boundary.
- `memory_lifecycle` (folder): Implements memory handling and memory-related lifecycle logic.
- `memory_poisoning_sentinel` (folder): Implements memory handling and memory-related lifecycle logic.
- `model_router` (folder): Wraps model-facing logic and invocation behavior.
- `objective_policy_engine` (folder): Groups related implementation for this subdomain boundary.
- `observability_gateway` (folder): Implements gate logic used to approve/reject progression.
- `orchestrator` (folder): Groups related implementation for this subdomain boundary.
- `policy_management` (folder): Groups related implementation for this subdomain boundary.
- `projection_query` (folder): Groups related implementation for this subdomain boundary.
- `quota_scheduler` (folder): Groups related implementation for this subdomain boundary.
- `reflection_rca` (folder): Groups related implementation for this subdomain boundary.
- `safety_controller` (folder): Groups related implementation for this subdomain boundary.
- `storage_lifecycle_manager` (folder): Handles file or state persistence concerns.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
