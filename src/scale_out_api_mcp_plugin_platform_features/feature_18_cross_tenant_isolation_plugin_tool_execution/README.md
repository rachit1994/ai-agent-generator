# Feature 18: cross-tenant isolation for plugin/tool execution

This folder contains isolated cross-tenant isolation gate logic.

## Components
- `runtime.py`: tenant-path/isolation/cache/key/budget/audit/leakage/containment checks.
- `contracts.py`: strict report contract and evidence refs.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces tenant identity propagation, runtime/queue/storage isolation, cache/artifact reuse blocking, tenant key policy controls, budget guardrails, continuous audit, adversarial leakage tests, and incident containment procedures.
- Blocks release on any failed cross-tenant isolation gate check.
- Uses one executable command for `preflight` and `ci`.
