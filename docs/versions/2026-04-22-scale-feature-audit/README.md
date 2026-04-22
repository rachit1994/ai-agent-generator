# 2026-04-22 Scale feature audit (versioned)

This folder contains one document per feature from the `Scale-out API and MCP/plugin platform features` section.
Each feature doc includes:
- two independent agent checklists (`Agent A`, `Agent B`),
- conservative confirmed score (`min(agent_a, agent_b)`),
- confirmed missing checklist reviewed as missing.

## Feature docs
- `01-local-first-non-regression-gate-everyday-use.md`
- `02-local-and-server-semantic-parity-enforcement.md`
- `03-control-plane-data-plane-split.md`
- `04-async-job-plane-for-long-running-api-operations.md`
- `05-edge-admission-control-rate-limits-retry-after.md`
- `06-per-tenant-quotas-and-concurrency-budgets.md`
- `07-idempotent-invocation-and-side-effect-deduplication.md`
- `08-distributed-queue-fairness-weighted-scheduling.md`
- `09-per-plugin-circuit-breakers-and-retry-budgets.md`
- `10-mcp-broker-session-lifecycle-management.md`
- `11-plugin-discovery-registry-compatibility-governance.md`
- `12-plugin-runtime-bulkheads-by-trust-class.md`
- `13-sandbox-hardening-egress-allowlists-cgroups-limits.md`
- `14-local-vs-production-semantic-parity-gates.md`
- `15-local-prod-config-overlay-with-invariant-semantics.md`
- `16-contract-version-negotiation-for-mcp-plugins.md`
- `17-plugin-authz-scopes-and-least-privilege-policy-engine.md`
- `18-cross-tenant-isolation-for-plugin-tool-execution.md`
- `19-end-to-end-plugin-observability-api-mcp-runtime.md`
- `20-per-plugin-per-tenant-cost-attribution-and-caps.md`
- `21-artifact-keying-parity-local-mirror-vs-object-store.md`
- `22-progressive-rollout-canary-rollback-for-plugin-versions.md`
- `23-scale-failure-drills-provider-429-queue-lag-restart.md`
- `24-incident-runbooks-for-plugin-outage-saturation-auth.md`

## Validation
- Run `python scripts/validate_scale_feature_audit.py`
- Run `python -m pytest tests/docs/test_scale_feature_audit_validation.py`
