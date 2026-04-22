# Feature 16: contract-version negotiation for MCP/plugins

This folder contains isolated version-negotiation gate logic.

## Components
- `runtime.py`: handshake/range/fallback/rejection/deprecation/telemetry/mixed-fleet checks.
- `contracts.py`: strict report contract and evidence refs.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces version-negotiation handshake and compatibility guardrails including deterministic incompatible rejection, rollback-safe dual-version behavior, deprecation windows, telemetry, mixed-version testing, and rollout gating.
- Blocks release on any failed version-negotiation gate check.
- Uses one executable command for `preflight` and `ci`.
