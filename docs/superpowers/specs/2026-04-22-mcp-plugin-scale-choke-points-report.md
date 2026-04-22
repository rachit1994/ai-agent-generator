# MCP and plugin support at scale: choke-point and failure report

**Companion:** [2026-04-22-mcp-plugin-scale-solution.md](./2026-04-22-mcp-plugin-scale-solution.md)  
**Context baseline:** [master-architecture-feature-completion.md](../../master-architecture-feature-completion.md)

## Executive summary

Supporting MCP servers and plugins at large scale is mainly a control, isolation, and reliability challenge. The likely failures are not only request throughput issues; they are also trust-boundary failures (unsafe tool execution), cascading dependencies (slow or unavailable plugin servers), and multi-tenant fairness issues (one tenant monopolizing tool capacity).

At scale, a plugin/tool platform fails first when:
- Tool calls are executed inline with user request paths.
- Per-plugin and per-tenant budgets are missing.
- Plugin health, circuit breakers, and fallback behavior are absent.
- Plugin contracts drift without compatibility gates.
- Local-dev behavior differs from production semantics.

This report lists where failures occur and how to detect them early.

---

## Scope and assumptions

- Scope includes MCP transport, tool invocation lifecycle, authz, tenancy controls, plugin isolation, observability, and rollout safety.
- The repo currently documents strong local contract discipline but limited production service guarantees in several architecture rows; this report assumes plugin hosting is a production concern layered on top.
- Local and production server environments must preserve contract semantics even if infrastructure adapters differ.

---

## Failure layers and choke points

## 1) Plugin discovery and registry

| Failure mode | Symptom | Root cause | Detection |
| --- | --- | --- | --- |
| Stale plugin registry | Missing or wrong plugin metadata | Non-atomic registry updates, cache staleness | Registry checksum mismatch, high 404 tool lookup |
| Incompatible plugin version rollout | Sudden invocation failures | No compatibility matrix or canary | Error spike by plugin version |
| Cold plugin resolution latency | Slow first call | Registry lookup and handshake done synchronously | p95 plugin-resolution latency |

## 2) Authn/authz and trust boundaries

| Failure mode | Symptom | Root cause | Detection |
| --- | --- | --- | --- |
| Cross-tenant tool access | Data leakage | Missing tenant scoping in token claims and policy checks | Access logs show tenant ID mismatch |
| Over-privileged tool execution | Unauthorized side effects | Broad plugin scopes and missing least-privilege policies | Policy-deny gap metrics, audit anomalies |
| Credential replay | Unexpected invocations | Long-lived static credentials | Abnormal geo/device reuse patterns |

## 3) MCP transport and session lifecycle

| Failure mode | Symptom | Root cause | Detection |
| --- | --- | --- | --- |
| Session churn overload | Connection resets, high handshake cost | No pooling/session reuse; short keepalive | MCP handshake rate and reset counters |
| Head-of-line blocking | Slow or timed-out tool calls | Shared event loop for unrelated plugin calls | Queue wait time and timeout histograms |
| Partial response ambiguity | Incorrect retries or duplicate actions | No standard completion/abort semantics | Duplicate invocation IDs and retry collisions |

## 4) Tool execution runtime and sandboxing

| Failure mode | Symptom | Root cause | Detection |
| --- | --- | --- | --- |
| Sandbox escape/path traversal | Host or tenant data exposure | Weak file/path boundary enforcement | Security audit events, denied path metrics |
| Resource starvation | Unresponsive workers | Unbounded CPU/RAM/file descriptors per plugin | Per-plugin cgroup throttling and OOM metrics |
| Dependency poisoning | Unexpected behavior after deploy | Mutable shared runtime dependencies | Artifact hash drift and failed attestation |

## 5) Backpressure, retry, and circuit behavior

| Failure mode | Symptom | Root cause | Detection |
| --- | --- | --- | --- |
| Retry storm | Cascading failures across plugins | Client+server retries without jitter/caps | Retry-to-success ratio surge |
| Queue overload | Large tail latency, dropped work | Missing admission control and fairness | Oldest-message age and queue depth alarms |
| Cascading dependency failure | Platform-wide degradation | No per-plugin circuit breakers/bulkheads | Blast radius metric by dependency |

## 6) Data plane and artifact persistence

| Failure mode | Symptom | Root cause | Detection |
| --- | --- | --- | --- |
| Duplicate side effects | Double writes/external actions | Missing idempotency keys at tool boundary | Duplicate operation fingerprints |
| Artifact inconsistency | Different results for same invocation | Non-transactional metadata/artifact writes | Metadata-to-blob reconciliation failures |
| Hot partitions | Localized DB or object-store throttling | Skewed keys by tenant/plugin/run | Partition-level throttle metrics |

## 7) Observability and SLO operations

| Failure mode | Symptom | Root cause | Detection |
| --- | --- | --- | --- |
| Untraceable failures | Long MTTR | Missing correlation IDs across API->MCP->plugin | Missing span-link rate |
| Unknown plugin health | Brownouts discovered by users | No plugin-level SLIs/SLOs | SLO coverage gaps per plugin |
| Cost blindness | Budget overrun | No per-plugin/per-tenant cost attribution | Cost anomaly detection lag |

## 8) Contract and schema evolution

| Failure mode | Symptom | Root cause | Detection |
| --- | --- | --- | --- |
| Contract drift | Runtime parse/validation errors | Weak version negotiation and compatibility checks | Contract mismatch reject metrics |
| Silent behavior changes | Logic regressions without hard errors | Optional fields with semantic changes | Golden-trace diff failures |
| Rollback incompatibility | Failed incident rollback | One-way migrations in plugin protocol | Rollback test failures in staging |

---

## Local vs production parity risks

Parity must preserve semantics, not infrastructure:
- Same request/response contracts.
- Same idempotency guarantees.
- Same authorization decisions for equivalent principals.
- Same run-state transitions and failure classification.

Common parity failures:
- Local mocks that hide timeouts/retries seen in production.
- Different auth policy engines between local and production.
- Different queue semantics (exactly-once locally vs at-least-once in production).
- Missing production-only plugin health/circuit states during local validation.

---

## FMEA (top risks)

Scoring: Severity (S) 1-5, Occurrence (O) 1-5, Detection difficulty (D) 1-5, RPN=S*O*D.

| ID | Risk | S | O | D | RPN | Primary mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | Cross-tenant tool access | 5 | 3 | 4 | 60 | Strict tenant-bound authz + policy tests |
| M2 | Retry storm on degraded plugin | 4 | 4 | 3 | 48 | Jittered retries + per-plugin circuit breakers |
| M3 | Missing idempotency on tool side effects | 5 | 3 | 3 | 45 | Invocation IDs and idempotency ledger |
| M4 | Queue fairness collapse | 4 | 4 | 2 | 32 | Per-tenant quotas and weighted fair queues |
| M5 | Plugin contract drift | 4 | 3 | 3 | 36 | Version negotiation + compatibility CI gates |
| M6 | Sandbox resource starvation | 4 | 3 | 2 | 24 | Hard CPU/RAM/FD limits and isolation pools |
| M7 | Untraceable plugin incidents | 3 | 4 | 4 | 48 | End-to-end trace IDs and plugin SLIs |
| M8 | Local/prod semantic mismatch | 4 | 3 | 4 | 48 | Parity test matrix and release blockers |

---

## Conclusion

Scaling MCP and plugin support safely requires treating plugin execution as a multi-tenant platform, not a simple extension hook. The most important controls are:
- strict trust boundaries,
- durable idempotent execution,
- bounded retries and backpressure,
- versioned contract governance,
- local/production parity gates.

Use the companion solution doc for architecture, rollout, and must-pass validation gates.
