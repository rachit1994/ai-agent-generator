# 10M DAU full coding-agent API: choke-point and failure report

**Companion:** [2026-04-22-10m-dau-api-choke-points-solution.md](./2026-04-22-10m-dau-api-choke-points-solution.md)  
**Architecture baseline:** [docs/master-architecture-feature-completion.md](../../master-architecture-feature-completion.md)

## Executive summary

Shipping this repository’s **full agent** (long sessions, worktrees, benchmarks, run-directory artifacts) as a **customer-facing HTTP API** to **10M daily active users** is not a request-rate problem alone. It is a **concurrency, cost, state, and isolation** problem. The current codebase is strongest as a **local deterministic CLI spine** and **Python library surface** under [`src/production_architecture/local_runtime/orchestrator/api/`](../../../src/production_architecture/local_runtime/orchestrator/api/); most rows in the master architecture snapshot that matter for a hosted service (distributed orchestration, centralized observability, external identity, durable queues, production storage ops) are **partially implemented or explicitly out of scope** for a multi-tenant platform.

This report names **where the system will choke or fail** when naively wrapped in an API, organized by **layer**. It separates **DAU** from **concurrent sessions**, **sustained RPS on the control plane**, and **LLM token and dollar throughput**—all of which can become limiting factors at different times.

**Bottom line:** Without a **control plane / data plane split**, **durable job execution**, **per-tenant quotas and budgets**, and **hardened sandboxes and storage**, the first failures will appear as **provider throttling and runaway cost**, then **DB and queue saturation**, then **data plane** failures (disk, inodes, git locks), and finally **cascading latency and incident blindness** (weak observability). The companion solution doc maps mitigations to these layers.

---

## Traffic and load assumptions (explicit)

These are **scenarios** for reasoning, not forecasts. The report avoids claiming a single “RPS for 10M DAU” without a product-specific mix.

| Dimension | What to model | Why it matters |
| --------- | ------------- | -------------- |
| DAU | 10M unique users / day | Sets *potential* load; does not define concurrency. |
| Session mix | % of DAU that start an agent run / day | Drives **job** and **LLM** load; small % × heavy run = system-bound. |
| Session duration | p50 / p99 wall time, tool steps | Drives **worker** count and **sandboxes** live simultaneously. |
| Control-plane QPS | create run, status, cancel, list artifacts | Drives **API workers**, **DB read/write**, **connection pools**. |
| LLM | tokens/user/day, peak tokens/sec, model tier | Primary **cost** and **429** risk; often the real bottleneck. |
| Artifact volume | bytes written/read per run, listing frequency | Drives **object store** and **egress** costs. |

**Sensitivity:** A product where most DAU only checks status of **previously started** jobs differs by orders of magnitude from one where most DAU **start** long **benchmark** or **evolve** loops on every visit.

---

## Baseline: this repo today vs. a 10M-DAU service

| Concern | Snapshot from master doc | Implication for hosted API |
| ------- | ------------------------ | -------------------------- |
| Runtime | “Local runtime … still a local deterministic **CLI spine** rather than production service runtime” (~47%) | Long work **cannot** stay bound to a single HTTP process lifetime. |
| Orchestration | “Production-grade **distributed lease/arbitration** guarantees **remain out of scope**” (~34%) | Need real **leases / fencing** (or idempotent single-writer semantics) in the service layer. |
| Observability | “**Centralized telemetry backend and dashboards** remain **out of scope**” (multiple ~34% rows) | On-call and SLOs require **new** logging/metrics/traces pipelines. |
| Identity / authz | “**External IdP** integration and **distributed policy-plane** enforcement **remain out of scope**” | API needs **mTLS or OAuth**, **per-tenant RBAC**, **API keys** with rotation. |
| Storage | Modules exist; “lacks **production ops hardening**” (~36%) | Need backup, **pooling**, **migrations** without full outages, and **SLOs** for queries. |
| Traces / events | “**Local logs**” / file artifacts; not **ingestion, indexing, retention** | Customer-facing **log streaming** and **query** need new systems. |
| Queues / retry | “**Distributed queue/backoff orchestration** remains out of scope” (e.g. retry/repeat profile) | **Required** in the product wrapper for fair scheduling and backpressure. |

Source for percentages and quotes: [docs/master-architecture-feature-completion.md](../../master-architecture-feature-completion.md).

---

## Layer 1: Edge and API gateway

| Failure mode | Symptom | Root cause in full-agent API | Detection signal |
| ------------ | ------- | ----------------------------- | ------------------ |
| Connection exhaustion | Clients see timeouts, TLS handshake errors | **Keep-alive** storms, **WebSocket/SSE** leaks, or tiny **client timeouts** retrying in parallel | SYN backlog, `accept` queue depth, edge 5xx |
| Body / message limits | 413, truncated uploads | **Repo snapshots**, **trace uploads**, or **context bundles** exceed limits | 413 rate, WAF allowlist hits |
| Deploy / config churn | 502 bursts | Rolling updates draining **in-flight** long streams | 502 during deploy window, `upstream_reset` |
| DDoS / abuse | Throttling for everyone | **No** per-IP or per-tenant **admission** at edge | Baseline RPS per IP vs. global |

---

## Layer 2: Authentication, authorization, tenancy

| Failure mode | Symptom | Root cause in full-agent API | Detection signal |
| ------------ | ------- | ----------------------------- | ------------------ |
| Noisy neighbor | One tenant **starves** others | **Shared** API and worker pools with **no** concurrency or **token** caps | Per-tenant queue depth vs. p99 |
| Quota bypass | **Runaway** job creation | **Idempotency** or billing gaps (duplicate `POST` creates many runs) | Duplicate `Idempotency-Key` without dedupe |
| Stolen API keys | Cross-tenant data access | No **key rotation**, **scoping**, or **binding** to workspace | Unusual peer IPs on same key |

Master doc: identity/authorization and permission matrix are **contract-hardened locally**; **external** policy and budget **sync** are **out of scope** for the repo as-is.

---

## Layer 3: Application and API workers (Python)

| Failure mode | Symptom | Root cause in full-agent API | Detection signal |
| ------------ | ------- | ----------------------------- | ------------------ |
| Head-of-line blocking | p99 **latencies** blow up for **short** calls | **Long** `run_project_session` / `validate_run` style work in **request** thread | p99 for `GET /status` tied to `POST /run` load |
| Worker OOM | Process killed mid-request | **Large** in-memory project graph, **buffers** of traces, unbounded **string** growth | OOMKilled count, RSS per pod |
| GIL / CPU contention | **Slow** JSONL parsing, **CPU** hot paths on hot cores | Tight **JSON** and validation loops on same event loop as I/O | CPU profiles, GIL wait time |

---

## Layer 4: Async job plane (durable queue + workers)

| Failure mode | Symptom | Root cause in full-agent API | Detection signal |
| ------------ | ------- | ----------------------------- | ------------------ |
| Queue backlog | **wait_time** in hours | **Autoscaling** lag; **too few** workers; **downstream** slow | **Age of oldest** message, `queue_depth` |
| Poison messages | Same job **fails** forever | Unhandled exception in user repo or **tool**; no **max attempts** with **dead letter** | DLQ rate, same `run_id` failures |
| At-least-once **duplication** | **Double** tool side effects, double spend | No **idempotency** for tool calls, git pushes, or billing | Reconciliation diffs, audit |

Master doc: **distributed** queue/backoff for retry/repeat profile is **out of scope** in-repo; the service **must** add this.

---

## Layer 5: LLM and tool upstream

| Failure mode | Symptom | Root cause in full-agent API | Detection signal |
| ------------ | ------- | ----------------------------- | ------------------ |
| Provider 429/503 | Mass **throttling** | **Token** or **request** limits; **regional** capacity | `rate_limit` errors, **Retry-After** |
| Retry storm | **Amplified** load during outage | **Uncoordinated** retries from **all** workers | Retry rate >> success rate in outage |
| **Cost** runaway | Budget blown in minutes | “**Viral**” usage pattern + **no** per-tenant **hard** caps | $/min vs. budget, token/min |
| **Latency** SLO miss | p99 to first token | **Oversubscribed** model tier; **no** queueing at router | p99 `time_to_first_token` |

This is often the **first** business-critical choke point for 10M DAU if even a small fraction uses **full** agent depth.

---

## Layer 6: Execution sandbox (worktrees, git, subprocesses)

| Failure mode | Symptom | Root cause in full-agent API | Detection signal |
| ------------ | ------- | ----------------------------- | ------------------ |
| Disk full | Random **write** failures, corrupted runs | **Unbounded** clone/cache growth; no **per-run** volume caps | `df`, pod evictions, write errors |
| Inode exhaustion | “No space” with **apparent** free GB | Many **small** files in **workdir** and **node_modules** | inodes used % |
| Git lock / slow clone | Stuck at **init** | Shared **template** repos; **NFS** latency; **concurrent** `git` on same path | stage timer for `git fetch` |
| **Fork** or **fd** limit | `Cannot allocate memory` or “too many open files” | **Subprocess** fan-out, unclosed pipes | `ulimit`, open FD count per worker |

---

## Layer 7: Data plane: Postgres, object store, vector search

| Failure mode | Symptom | Root cause in full-agent API | Detection signal |
| ------------ | ------- | ----------------------------- | ------------------ |
| Pool saturation | **Hanging** API requests at DB | `max_connections` hit; **pool** smaller than **workers** | `waiting` sessions in Postgres, pool wait time |
| Long transactions | **Deadlocks** or bloat | **Holding** rows across **LLM** calls | `pg_stat_activity` duration, `deadlocks` |
| Read replica **lag** | Stale **status** after run completes | **Async** replication; user polls **replica** | replica lag seconds |
| Object store list storms | **High** list API cost, slow UX | UIs that **list** every object per **poll** | LIST req/min, 503 from provider |
| **Vacuum** / IO | Write **amplification** | Hot **append-only** event tables | table bloat, autovacuum behind |

Master doc: storage ~36% with **“production ops hardening”** and **“externalized deployment guarantees”** **missing**—operational playbooks and HA must be **added** in deployment.

---

## Layer 8: Coordination (leases, sharding, idempotency)

| Failure mode | Symptom | Root cause in full-agent API | Detection |
| -------- | --- | --- | --- |
| **Split-brain** or double work | Inconsistent **artifacts**; **duplicate** side effects | **No** true **fencing**; two workers think they own a **run** | Conflicting `run_id` writes, checksum mismatch |
| Stale **lease** | Ghost progress | **Clock skew** or **missed** lease renew | `lease_expired` events without stop |

Master doc: **“production-grade distributed lease/arbitration guarantees remain out of scope.”**

---

## Layer 9: Observability and operability

| Failure mode | Symptom | Root cause in full-agent API | Detection |
| -------- | --- | --- | --- |
| **Blind** incidents | Long MTTR, user reports first | **File-local** JSONL not in **central** logs; no **SLO** dashboards | Missing traces for user-visible failures |
| No **SLO** burn | **Reactive** only **after** cost/limit alerts | **No** SLIs for **run completion** and **stage** time | SLO: none |

---

## Layer 10: Security and abuse

| Failure mode | Symptom | Root cause in full-agent API | Detection |
| -------- | --- | --- | --- |
| **SSRF** | **Internal** network access from **tool** fetches | Agent **open** URLs; **no** **egress** policy | Outbound to RFC1918 from sandbox |
| **Path traversal** | **Escape** from workspace to host | Unsanitized user paths in **read_file**-style tools | open() outside `root` |
| **Crypto / abuse** | **CPU** and **reputation** damage | Unrestricted **CPU** in sandbox; **no** **verified** org sign-up | Sustained high CPU, abuse reports |

---

## FMEA-style table (top failure themes)

**Severity (S):** 1=minor, 5=catastrophic (data loss, widespread outage, major financial loss).  
**Occurrence (O):** 1=rare, 5=very likely under naive scaling.  
**Detection (D):** 1=high (clear alert), 5=low (silent or user-reported).  
**RPN = S×O×D** (higher = prioritize mitigation).

| ID | Theme | S | O | D | RPN | Repo gap (today) | Primary mitigation (see solution doc) |
| -- | ----- | - | - | - | --- | ------------------ | ------------------------------------- |
| F1 | LLM **429/503** and **cost** blowout | 5 | 5 | 3 | 75 | No production **model router** or **spend** plane in master scope | **Router**, **caps**, **circuit breakers** |
| F2 | **No job plane**: HTTP-bound long work | 5 | 4 | 2 | 40 | **CLI spine** not service runtime | **Async jobs**, **worker** autoscale |
| F3 | **DB** pool / connection **exhaustion** | 4 | 4 | 2 | 32 | **Ops hardening** called out as missing | **Pooling**, **limits**, read path tuning |
| F4 | **Sandbox** disk / **inode** / **oom** | 4 | 4 | 3 | 48 | **Local** workdirs | **Quotas**, **ephemeral** volumes, **cgroups** |
| F5 | **Queue** backlog / **DLQ** neglect | 4 | 3 | 3 | 36 | **Distributed queue** not in scope | **Backpressure**, **SLOs**, **DLQ** playbooks |
| F6 | **Noisy** tenant / **abuse** | 4 | 3 | 4 | 48 | **Policy-plane** not distributed | **Per-tenant** limits, **isolation** |
| F7 | **Duplicate** execution / **idempotency** | 5 | 2 | 4 | 40 | **Leases** not production-grade | **Fencing**, **idempotency** keys |
| F8 | **Observability** gap | 3 | 4 | 5 | 60 | **Centralized** telemetry out of scope | **Tracing**, **SLOs**, run **stage** metrics |
| F9 | **Object store** / **egress** cost | 3 | 3 | 3 | 27 | Artifacts are **file**-local in harness | **S3** layout, **lifecycle**, **signed URLs** |
| F10 | **SSRF** / **escape** from sandbox | 5 | 2 | 4 | 40 | **External** egress policy not in scope | **Egress** proxy, **default-deny** |
| F11 | **Provider** + **our** **retry** storm | 4 | 3 | 3 | 36 | — | **Jittered** backoff, **hedging** limits |
| F12 | **Edge** **502** during **deploy** | 3 | 3 | 2 | 18 | — | **Graceful** drain, **connection** **migration** |

---

## Conclusion

A **10M DAU** **full-agent** API will fail in predictable **layers** unless the product wrapper introduces a **durable** execution tier, **strict** **multi-tenant** **governance**, **LLM** **economics** and **routing**, **hardened** **sandboxes**, and **operational** **observability**. The in-repo **orchestrator** and **run-directory** contracts provide a **strong** **correctness** foundation for **local** runs; they do not, by themselves, provide **distributed** **safety** or **scale**.

**Next:** Read the companion [solution document](./2026-04-22-10m-dau-api-choke-points-solution.md) for the target architecture, mitigations, phased rollout, and **codebase follow-ups**.

### Related documents

| Document | Role |
| -------- | ---- |
| *This file* | choke points, FMEA, traffic assumptions, repo-baseline table |
| [2026-04-22-10m-dau-api-choke-points-solution.md](./2026-04-22-10m-dau-api-choke-points-solution.md) | target architecture, mitigations, phases, follow-ups |
| [master-architecture-feature-completion.md](../../master-architecture-feature-completion.md) | in-repo % completion and “out of scope” quotes |
