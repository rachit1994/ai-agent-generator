# Feature 10: MCP broker/session lifecycle management

This folder contains isolated MCP broker lifecycle gate logic.

## Components
- `runtime.py`: broker/session lifecycle checks.
- `contracts.py`: strict report contract validation.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces broker presence, lifecycle API semantics, persistence/reclaim, heartbeat/resume, authz boundary, deterministic routing, failover tests, and telemetry coverage.
- Blocks release on any failed broker-session gate check.
- Runs via one executable command in both `preflight` and `ci` modes.
