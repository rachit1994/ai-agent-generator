# Feature 17: plugin authz scopes and least-privilege policy engine

This folder contains isolated plugin-scope authz gate logic.

## Components
- `runtime.py`: taxonomy/engine/invocation/deny-default/policy/audit/escalation/admin checks.
- `contracts.py`: strict report contract and evidence refs.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces plugin scope taxonomy, least-privilege policy evaluation, per-invocation scope checks, default-deny semantics, versioned policy authoring/simulation, allow/deny auditing, escalation test coverage, and admin controls.
- Blocks release on any failed plugin authz gate check.
- Uses one executable command for `preflight` and `ci`.
