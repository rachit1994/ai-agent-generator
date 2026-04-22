# 2026-04-22 strict scale feature re-audit

This is a strict anti-inflation rescore of the `Scale-out API and MCP/plugin platform features` section.

Scoring policy:
- Documentation-only evidence = `0`.
- Scaffold-only code = `0`.
- Local-only approximations score only minimal partial credit.
- Final score = conservative floor (`min(strict_a, strict_b)`) from two independent audits.

## Strict rescored features

| Feature | strict_a | strict_b | confirmed_floor |
| --- | ---: | ---: | ---: |
| Local-first non-regression gate (everyday use) | 6 | 0 | **0** |
| Local and server semantic parity enforcement | 0 | 0 | **0** |
| Control plane / data plane split | 0 | 0 | **0** |
| Async job plane for long-running API operations | 3 | 0 | **0** |
| Edge admission control (rate limits + Retry-After) | 0 | 0 | **0** |
| Per-tenant quotas and concurrency budgets | 1 | 0 | **0** |
| Idempotent invocation and side-effect deduplication | 12 | 6 | **6** |
| Distributed queue fairness (weighted scheduling) | 2 | 3 | **2** |
| Per-plugin circuit breakers and retry budgets | 0 | 0 | **0** |
| MCP broker/session lifecycle management | 0 | 0 | **0** |
| Plugin discovery/registry compatibility governance | 0 | 0 | **0** |
| Plugin/runtime bulkheads by trust class | 0 | 0 | **0** |
| Sandbox hardening (egress allowlists, cgroups, limits) | 0 | 0 | **0** |
| Local vs production semantic parity gates | 1 | 0 | **0** |
| Local/prod config overlay with invariant semantics | 2 | 0 | **0** |
| Contract-version negotiation for MCP/plugins | 0 | 0 | **0** |
| Plugin authz scopes and least-privilege policy engine | 1 | 0 | **0** |
| Cross-tenant isolation for plugin/tool execution | 0 | 0 | **0** |
| End-to-end plugin observability (API->MCP->runtime) | 3 | 0 | **0** |
| Per-plugin/per-tenant cost attribution and caps | 0 | 0 | **0** |
| Artifact keying parity (local mirror vs object store) | 2 | 0 | **0** |
| Progressive rollout/canary/rollback for plugin versions | 0 | 0 | **0** |
| Scale failure drills (provider 429, queue lag, restart) | 0 | 0 | **0** |
| Incident runbooks for plugin outage/saturation/auth | 0 | 0 | **0** |

## Interpretation

- Under strict implementation-only scoring, nearly all scale/platform features are still unimplemented in executable production-grade runtime paths.
- The only non-zero floors came from:
  - `Idempotent invocation and side-effect deduplication` (`6`) due to partial idempotency at storage append paths.
  - `Distributed queue fairness (weighted scheduling)` (`2`) due to local scheduler behavior that does not satisfy distributed fairness requirements.
