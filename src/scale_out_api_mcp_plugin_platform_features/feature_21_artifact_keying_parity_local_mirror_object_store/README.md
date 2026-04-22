# Feature 21: artifact keying parity (local mirror vs object store)

Isolated gate implementation for verifying canonical artifact key parity behavior.

## Components
- `runtime.py`: evaluates parity checks and gate status.
- `contracts.py`: validates report schema and canonical evidence references.
- `__init__.py`: exports stable feature package API.

## Gate behavior
- Enforces canonical key schema adoption, object-store adapter coverage, local/object reconciliation, collision and drift detection, checksum integrity checks, legacy migration support, conflict semantics, and backend parity integration test readiness.
- Fails closed when any check is missing.
