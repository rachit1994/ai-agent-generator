# Scale risk external references (blogs, papers, repos)

This document tracks external references that are likely to prevent future failures in the scale-out API and MCP/plugin platform roadmap.

It is intentionally vendor-neutral. Sources are mapped to feature gaps and failure modes, not to one specific coding agent product.

## How to use this document

- Use this list during planning for any scale feature currently at low completion.
- Prioritize `official` and `paper` sources for architecture decisions.
- Treat `community` posts as implementation examples, not policy authority.
- For each adopted pattern, add tests and fail-closed gates before raising completion percentages.

## Risk-to-reference map

| Risk area | Why it matters | Recommended references |
| --- | --- | --- |
| Idempotent invocation and dedupe | Prevent duplicate side effects under retries and ambiguous failures | [Stripe idempotency design](https://stripe.com/blog/idempotency), [Stripe idempotent requests](https://stripe.com/docs/api/idempotent_requests) |
| Retry storms and overload collapse | Prevent cascading failure when dependencies degrade | [Google SRE handling overload](https://sre.google/sre-book/handling-overload/), [Google load shedding](https://cloud.google.com/blog/products/gcp/using-load-shedding-to-survive-a-success-disaster-cre-life-lessons), [AWS retries/backoff/jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) |
| Queue fairness and tenant starvation | Avoid noisy-tenant monopolization of worker capacity | [DRR paper (SIGCOMM)](https://dl.acm.org/doi/10.1145/217391.217453), [DWRR paper](https://happyli.org/tongli/papers/dwrr.pdf) |
| Circuit breakers and dependency blast radius | Bound failure propagation per plugin/dependency | [Envoy circuit breaking](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/circuit_breaking), [Envoy outlier detection](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/outlier.html) |
| Async job durability and replay | Support long-running operations beyond request lifetimes | [Temporal retry policies](https://docs.temporal.io/retry-policies), [Temporal repo](https://github.com/temporalio/temporal) |
| Dual-write inconsistency | Prevent metadata/artifact divergence across DB + broker | [Transactional outbox pattern](https://microservices.io/patterns/data/transactional-outbox.html), [Saga pattern](https://microservices.io/patterns/data/saga.html), [Saga + outbox article](https://infoq.com/articles/saga-orchestration-outbox) |
| Plugin authz and least privilege | Enforce tenant/plugin scope constraints centrally | [OpenFGA repo](https://github.com/openfga/openfga), [OpenFGA docs](https://openfga.dev/) |
| Cross-tenant data isolation | Prevent tenant data leakage in pooled storage | [AWS RLS guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-managed-postgresql/rls.html) |
| Sandbox hardening for untrusted tool execution | Contain code execution risk and limit host blast radius | [Firecracker repo](https://github.com/firecracker-microvm/firecracker/), [firecracker-containerd](https://github.com/firecracker-microvm/firecracker-containerd/), [Kata Containers](https://github.com/kata-containers/kata-containers) |
| Progressive rollout and rollback | Limit deploy risk with metric-gated promotion | [Argo Rollouts repo](https://github.com/argoproj/argo-rollouts/), [Argo analysis docs](https://argoproj.github.io/argo-rollouts/features/analysis/), [Argo Prometheus analysis](https://argoproj.github.io/argo-rollouts/analysis/prometheus/) |
| Failure drills and resilience validation | Validate recovery before production incidents | [Principles of Chaos Engineering paper](https://arxiv.org/pdf/1702.05843), [Netflix Simian Army](https://netflixtechblog.com/the-netflix-simian-army-16e57fbab116), [LitmusChaos repo](https://github.com/litmuschaos/litmus) |
| MCP compatibility/version governance | Prevent protocol drift across server/client/plugin versions | [MCP spec repo](https://github.com/modelcontextprotocol/modelcontextprotocol/), [MCP spec latest](https://modelcontextprotocol.io/specification/latest) |
| End-to-end observability and correlation | Reduce MTTR across API -> broker -> runtime -> plugin path | [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv), [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector), [Collector contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/) |
| Long-term memory lifecycle management | Prevent stale memory, contradiction drift, and poor multi-session recall | [MemGPT paper](https://arxiv.org/abs/2310.08560), [Generative Agents paper](https://arxiv.org/abs/2304.03442), [LongMem paper](https://arxiv.org/abs/2306.07174), [LongMemEval benchmark](https://arxiv.org/abs/2410.10813v2), [Long-term memory doc](./long-term-memory-and-memory-management-references.md) |

## Source quality labels

- `official`: standards bodies, project docs, or primary vendor engineering docs.
- `paper`: peer-reviewed papers or foundational research publications.
- `repo`: actively maintained OSS implementation reference.
- `community`: useful writeups or examples, lower authority than official docs.

## Suggested near-term adoption order

1. Idempotency + overload controls (`official`).
2. Queue fairness + circuit breaking (`paper` + `official`).
3. Async job durability + outbox/saga consistency (`official` + pattern references).
4. Authz and tenant isolation (`official` + `repo`).
5. Rollout gating + observability + failure drills (`repo` + `official` + `paper`).

## Notes for completion scoring discipline

- Do not increase feature percentages based on reference collection alone.
- Increase only after code, tests (including negative paths), and evidence artifacts exist.
- For each reference adopted, record:
  - selected pattern,
  - where implemented,
  - test coverage added,
  - known limitations and rollback path.
