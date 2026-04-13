# Persona Agent Platform — phased checklist (plain English)

This is **one** checklist for reaching the program goal: **a single production-ready exit**, **every workflow** in `docs/implementation/production-workflow-manifest.md` proven on **both Ollama and vLLM**, with **no partial “MVP” release**.

That exit is only meaningful if it delivers what the design calls **continuously self-improving** persona agents (`docs/superpowers/specs/2026-04-13-persona-agent-platform-design.md` **Goal**): personas that **learn across runs** from memory, trajectories, and governed prompt or policy change—**without** weakening autonomy-with-safeguards, long memory, or local-first operation.

If anything here conflicts with another doc, follow **`docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md`** first, then the release gate spec, then the rest.

### How the phases line up with **self-learning**

**Self-learning** here means a **closed loop**: each run produces **measurable signals** (gates, traces, rejects, failures) → those signals are **stored and retrieved** (memory layers, failure signatures) → they **change future behavior** (heuristics, generative memory, prompt or policy promotion) → changes are **proven and rolled back** if they regress safety or reliability. Phases are ordered so **nothing downstream invents learning** that upstream contracts cannot support.

| Phase | Role in self-learning |
|-------|------------------------|
| **0** | Instrumentation and CI so “did we learn or regress?” is **measurable**, not anecdotal. |
| **1** | Scope and owners: **which** personas learn, under **which** KPIs and governance, with **no** hidden learning paths outside the manifest. |
| **2** | Typed workflows: stable **step IDs and schemas** so memory, eval, and promotion attach to the **same** units of behavior every time. |
| **3** | Runtime + tree search + replay: **trajectories** and planner choices exist as durable facts—the **raw material** for reflection and tuning. |
| **4** | Safety and time: **learning is never an excuse** to skip rails; unsafe or out-of-order adaptation is blocked. |
| **5** | **Where learning lives**: episodic / semantic / procedural / failure / generative memory, write rules, and “same mistake challenged twice” behavior. |
| **6** | **The improvement flywheel**: stress, eval suites, trajectory metrics, prompt or policy evolution, and demotion when learning hurts quality. |
| **7** | **Learning under real routing**: speculative decoding and dual backends so improved policies still work in production-like conditions. |
| **8** | **Observe learning in production**: replay and drills so you can tell when a promoted change caused a regression. |
| **9** | **Autonomous learning loop**: schedules and API or CLI so personas keep running, collecting signal, and applying governed updates **without** ad-hoc human glue. |
| **10** | **Prove the loop at exit**: evidence that self-learning mechanisms are **on**, **governed**, and **non-regressive** across the full manifest and both backends. |

### What this file is meant to cover (nothing skipped)

These program sources are folded into the phases below: **`README.md` (program summary)**, **implementation roadmap** (Phases 1–10, M1–M4, production exit criteria), **master plan** (cadence, **governance roles** including EM and Product/Ops stakeholders, ownership matrix, preconditions, **decision policy**), **execution playbook** (prereqs, corner cases, personal “phase done” checks), **delivery process** (DOR, TDD, gates 1–5, release readiness, post-release, evidence list), **release gate spec** (terms, soak, sampling, rollback, waivers, no-repeat proof), **design spec** (non-negotiables, hybrid scope, execution contract, safeguards, memory policy, improvement loop, implementation sequence, done criteria), **tech decisions** (stack, parity contract, adoption tiers, **Inference DRI** ownership for routing, compatibility and security policies), **doc-precedence** (parity math, `agentevals` §7, observability §8, gate packets §10, inference matrix), **quality advancements** (adopt-now, controlled rollout, governance, evidence per technique), **metrics and SLOs** (every SLO row, KPIs, reporting cadence including **executive summary**, trend packs, go-live alerts), **risk register** (active risks R1–R8, review, **closure criteria**), **production manifest** (inventory rules and column literals), **gate packet README** (`MANIFEST.json` fields), **research/OSS integration** (baseline vs optional OSS, **Letta** as design reference only unless ADR), and **schemas** (failure signature, normalization, OTel span names). **Optional** items you must explicitly decide **not** to do: **TruLens** (non-gating if OTel is complete), **SpecRouter** (backlog unless EM + Tech Lead promote it).

**Design “implementation sequence” (nine bullets)** maps to: Phase 2 → compiler; Phase 3 → tree search + engine + triad + checkpoints + hooks; Phase 4 → temporal + railguard + tool gateway; Phase 5 → memory service; Phase 6–7 → eval harness + router; Phase 8 → observability/replay; Phase 9 → API/CLI/scheduling. That sequence is the **build order** for subsystems; the **self-learning** table above explains **why** that order matters for continuously improving personas.

---

## Phase 0 — Machines and repo ready (before Phase 1 work counts)

These are the “you cannot honestly start” checks from the execution playbook.

**Self-learning link:** without eval harness owners, **OpenTelemetry** export suitable for **agentevals**, and a baseline observability owner, you cannot **measure** whether personas improve across runs or **prove** a regression after a promoted policy change.

1. Put **Python 3.13 or newer** on developer machines and CI, and commit a **pinned lockfile** for the app and for CI.
2. Stand up **Postgres with the pgvector extension** so both developers and CI can reach it; write down how schema changes roll out (**migration path**).
3. Install and prove you can call **Ollama** and **vLLM** from the environments where you will collect evidence (same machine or different machines is fine if you write down **hardware class** and model pins for parity).
4. Make sure CI can run **promptfoo**, **pytest with DeepEval**, and can **export or store OpenTelemetry** well enough for **agentevals** to score traces.
5. Read **`README.md`**, then **`docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md`**, then the **execution playbook** in the order it lists.
6. Assign **named owners** for the **test harness and full regression suite** before any Phase 2 compiler work starts (master plan precondition—no anonymous “the team”).
7. Assign a **named owner** for bringing up the **baseline observability stack** (metrics, exporters, dashboards) so the Phase 6 prerequisite is not orphan work.

**Exit check:** items 1–4 and 6–7 are true in writing (links, versions, owner names, or a short internal runbook).

---

## Phase 1 — Contracts, inventory, and who owns what (milestone **M1**)

**Goal:** everyone agrees how we work, what “in scope” means, and the manifest lists **every** persona markdown we will ship.

**Self-learning link:** governance and adopt-now mapping name **who** may promote memory or prompt changes, **which** KPIs prove learning (not vibes), and **how** rollbacks work so learning stays inside the manifest and risk register.

1. Write down the program rules you are following: **one** production promotion when **everything** passes; **no** MVP; **no** shrinking scope without EM + Tech Lead sign-off and risk-register tracking.
2. Lock scope to **only** workflows that will appear in the production manifest (no secret “side list”).
3. Write **architecture contracts**: what each subsystem owns, what it talks to, and what “done” means at its boundary.
4. Put names on those contracts (**subsystem owners**).
5. Create a **Definition of Ready** template: what must be true before a task starts (clear goal, tests named, risks named, rollback idea, telemetry expectation).
6. Create a **gate evidence** template: what files, links, and sign-offs a gate reviewer expects in a packet.
7. Open the **research and OSS integration** doc and make two lists: **research items to use or drop**, **OSS libraries to use or drop**.
8. For **each** dependency you decide to keep or add, write an **ADR** that includes: why, owner, rollback, date. Do not start building on a “maybe” library without that.
9. For **each** thing you reject, write **one line** why (so nobody silently assumes it is still planned).
10. List every `*.md` file under `docs/personas/` (except `README.md` and other **index-only** files unless Tech Lead says they are compiled personas).
11. Do the same for `docs/more_personas/`.
12. For **each** in-scope file, compute **`workflow_id`**: take the path from `docs/…`, drop `.md`, replace `/` with `.` (example: `docs/personas/sales.md` → `docs.personas.sales`).
13. Add **one manifest row per** in-scope file (or one row per compiler output ID if the compiler will emit more than one ID per file—then document the mapping for Tech Lead sign-off).
14. Set **`Compiler version / commit`** to **`pre-compiler`** on every new row until Phase 2 produces a real green compile.
15. Set **`Owner DRI`** to **`pending-DOR-assignment`** until the first DOR for that workflow names a person (until then, **Tech Lead** is accountable).
16. Set **`Last green gate run (link)`** to **`no-evidence-yet`** until real evidence exists.
17. Confirm the manifest table is **not empty** (an empty table means “production exit is impossible by definition”).
18. Get **Tech Lead** sign-off on the manifest wording: **“IDs match compiler contract for Phase 2.”**
19. Publish a **RACI** (who is accountable, responsible, consulted, informed) that matches the program: at least M1 Tech Lead, M2 Safety Owner, M3 Data/Memory + Quality, M4 SRE/Ops.
20. Publish an **approved gate board checklist** (the actual checklist artifact reviewers will use).
21. Publish the **named ownership matrix** for runtime subsystems (Planner, Run Engine, Safety, Memory, Observability, Release Gate) including **primary**, **secondary**, **response SLA**, and **escalation path**—use the master plan table as the minimum set.
22. Write how **hybrid packaging** will work (**library core + optional runtime service**) so operators know what runs where, without shrinking the manifest or skipping workflows (design scope).
23. Turn every **adopt-now** item in the quality advancements doc into **tracked work**: each line must have a **named owner**, a **measurable KPI or SLO hook**, a **safety non-regression test**, and a **rollback** story before you call Phase 1 “planning complete.”
24. For **controlled rollout** features: either list each one with its **flag ladder** to production configuration, or write **“none required for this exit”** once so nobody assumes hidden scope.
25. Define how **clarification and objective lock** happens before any **execution-heavy** milestone (design non-negotiable)—who runs it, where it is recorded, and what “locked” means.
26. Run a **formal sign-off** on: contracts, RACI, gate checklist, manifest, ownership matrix, hybrid plan, and adopt-now mapping (**Phase 1 acceptance**).
27. Name **Product and Operations stakeholders** (consulted/informed) for rollout and acceptance readiness, per the master plan governance model.

**Exit check:** Phase 1 acceptance in the roadmap is satisfied **in writing** with names and dates.

---

## Phase 2 — Compiler and first hard CI gates (start of **M2**)

**Goal:** every manifest workflow compiles to typed steps, and CI blocks bad changes.

**Self-learning link:** stable **`workflow_id`** and step schemas are the **anchors** for attaching memory writes, failure signatures, eval cases, and policy versions—without them, “learning” drifts into untraceable blobs.

1. Build the **workflow compiler** that reads the manifest’s persona markdown and emits **typed step specs**.
2. Enforce **schemas at the boundaries** the compiler defines (no loose JSON blobs without a schema).
3. Turn on **blocking CI** for: static types, lint, **critical security scans** where applicable, core unit tests, schema checks against emitted artifacts.
4. **Pin** DeepEval versions and wire the **first** DeepEval pytest tests (against compiler output or golden fixtures).
5. **Pin** RAGAS where you test **retrieval quality**, and wire those tests into CI.
6. Make LLM gate tests **deterministic enough** for CI (pinned seeds, recorded responses, or agreed fixtures—no “flaky green”).
7. Run the compiler on **every** `workflow_id` in the manifest; record **success for 100%** of rows.
8. For each row that first goes green, update **`Compiler version / commit`** to the **full 40-character git SHA** of the merge that produced that green compile.
9. If you ever change external IDs, do it in the **same PR** as the compiler change and update **every** manifest row, CI mapping, and packet reference, with **EM + Tech Lead** sign-off captured in the promotion packet.

**Exit check:** roadmap Phase 2 acceptance: **100%** compile, CI gates are real blockers, DeepEval runs in CI.

---

## Phase 3 — Run engine, triad, tree search (still **M2**)

**Goal:** runs can pause and resume, every step has architect / implementer / reviewer behavior, planning branches are auditable.

**Self-learning link:** checkpoints, **policy_version** in logs, and replayable planner branches are the **trajectory substrate** for trajectory metrics, reflection, and evidence-backed prompt tuning.

1. Integrate **LangGraph** as the run engine that drives workflows.
2. Wire **`langgraph-checkpoint-postgres`** so checkpoints live in Postgres on the **same governed database story** as memory (not a hidden second database).
3. Wire **LiteLLM** (or the agreed routing client from tech decisions) so all model calls go through one **versioned** abstraction that can target **Ollama** and **vLLM**.
4. For **each step**, run **`architect`**, then **`implementer`**, then **`reviewer`** through **AutoGen AgentChat** (or the agreed stack), in the order the design spec requires relative to planning and validators.
5. Use **Instructor + Pydantic** for structured outputs at the **planner**, **reviewer**, and **typed tool argument** boundaries.
6. Use **Pydantic v2** for **step input/output contracts** everywhere the design calls for schema-safe IO, not only inside Instructor-wrapped calls.
7. For any step that cannot use Instructor, file a **numbered ADR** listing the `workflow_id` and step ids and the alternative.
8. Implement **TreeSearchPlanner** (plan branches, pick a branch with **auditable reasons**, persist enough to replay the choice).
9. Emit **structured logs** (**structlog** per design stack) that carry **run_id**, **workflow_id**, **step_id**, and **policy_version** fields needed for audits and dashboards.
10. Prove **resume** works for **every** manifest workflow after a crash or restart.
11. Prove every step transition stores **gate state** and **reviewer decision** in durable artifacts.
12. Prove **planner outputs** are stored and can be **replayed** for audits.
13. Before scaling execution-heavy tests or dogfood volume, record an **objective lock** for that milestone (what question is settled, who approved, where stored)—same rule as Phase 1, reapplied per milestone.

**Exit check:** roadmap Phase 3 acceptance is true for **all** manifest rows.

---

## Phase 4 — Safety and time ordering (end of **M2**)

**Goal:** bad inputs, illegal tool calls, and “steps in the wrong order” never reach execution.

**Self-learning link:** faster memory or clever heuristics must **never** shortcut validators—otherwise “learning” becomes **silent risk accretion** instead of governed improvement.

1. Add the **policy validator chain** (input, action, output) so it runs **before** tools execute where the design says it must.
2. Implement **input** checks for **prompt injection**, **unsafe goals**, and **missing context** (design railguard list).
3. Implement **action** checks for **tool allowlists**, **capability scope**, and **temporal eligibility** before any tool runs.
4. Implement **output** checks for **PII leakage**, **unsupported claims**, and **schema conformance** before results leave the step boundary.
5. Add **temporal rules** (“step B cannot run before step A passes”) enforced **before** tools execute.
6. Add **hard stops** for policy violations and for **confidence-collapse** scenarios (design safeguards).
7. If **policy**, **auth**, or **tenant context** cannot be resolved, halt in **`safe_denied`** mode with **no** silent degraded bypass (design non-negotiable).
8. Integrate **openai-guardrails-python** where it fits; keep **tenant binding**, **pinned policy versions**, and **temporal proof** logic in **your** code, not only inside vendor defaults.
9. Run the **full manifest** test suite and prove **unsafe** actions are **blocked before execution**.
10. Prove **out-of-order** actions are **blocked before execution**.

**Exit check:** roadmap Phase 4 acceptance on the **full** manifest.

---

## Phase 5 — Memory and “learn without breaking safety” (start of **M3**)

**Goal:** five memory types behave correctly, retrieval happens before planning and execution, heuristics help reliability without opening safety holes.

**Self-learning link:** this phase is the **stateful core** of self-learning—what the persona **remembers**, **retrieves**, and **promotes** (including failure → prevention) so the next run is measurably different from the last.

1. Build **episodic** memory read/write with promotion rules.
2. Build **semantic** memory read/write with promotion rules.
3. Build **procedural** memory read/write with promotion rules.
4. Build **failure** memory read/write with promotion rules.
5. Build **generative** memory with **no ungoverned writes** (shadow / eval / promotion ladder as your design requires).
6. Implement the **summary ladder**: run logs → summaries → meta-summaries → distilled lessons, with checks that summaries match sources.
7. Wire **retrieval before planning** and **retrieval before execution** for every step that the design marks that way.
8. Add **ERL-style** “extract useful heuristics from past runs” and inject them where planning happens, without bypassing safety.
9. Test **reads and writes per memory class** with automated checks.
10. Run benchmarks for **retrieval** and **generative promotion** rules.
11. On held-out scenarios, show **reliability improves** with heuristics on, and show **safety gates do not get worse**.
12. Apply the **memory write policy** in tests and production code: **successful** runs may promote memories only **after** quality checks; **failed** runs write **failure memory only** (no blind promotion); **every** write stays **tenant-scoped**.
13. When a failure pattern repeats, ship a **prevention check** (validator, policy, or test) so the platform **learns**—not only logs (design non-negotiable + stability SLO spirit).
14. For **generative (MemGen-style) memory**, prove **trajectory-quality uplift** on held-out scenarios with **zero safety regression** and an **auditable promotion history** (quality advancements adopt-now #4), or do not turn it on in production configuration.

**Exit check:** roadmap Phase 5 acceptance.

---

## Phase 6 — Evaluation, stress, self-improvement (middle of **M3**)

**Goal:** you can prove quality in CI and in replay, stress the system, and evolve prompts/policies without sneaking regressions through.

**Self-learning link:** this phase closes the **eval → promote/demote** loop (trajectory metrics, **GEPA-style** evolution, **agentevals**, demotion on breach) so “self-improving” is **machine-checked**, not a narrative.

**Before heavy stress:** satisfy **baseline observability** exactly as **`docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` §8** (not a paraphrase): **≥99%** OTel export success for **`plan`**, **`action`**, and **`output`** spans over a rolling **168 hours** in the validation environment; dashboards with links for **gate pass rate**, **trace completeness**, **error rate**, and **p95 latency**, each scoped by **`workflow_id`**; at least **one** successful end-to-end trace export per manifest workflow in the **last 30 days** (synthetic smoke allowed).

1. Build a **replay harness** so you can re-run recorded traces or fixtures on demand.
2. Add **trajectory metrics** (not only pass/fail): quality, coherence, decomposition, recovery after reject—stored where reviewers can see trends.
3. Add **promptfoo** as the default **prompt and policy** regression and red-team harness; failures **block** merges when you say they should.
4. Store **promptfoo artifacts** so each **`workflow_id`** can be traced to its outputs.
5. Wire **agentevals** to read **exported OpenTelemetry** traces for **promotion** and **incident** review paths.
6. Expand **DeepEval** for **step** and **memory** quality tied to manifest workflows.
7. Expand **RAGAS** wherever retrieval is part of the test.
8. Add **pass-to-the-kth-power** (`pass^k`) stress, **perturbation** tests, and **injected** tool/API fault tests; run them on a schedule (CI and/or nightly).
9. Add **GEPA-style** prompt/policy evolution: versioned registry, held-out suite, rollback path, promotion only when **promptfoo + agentevals + DeepEval** (and RAGAS where relevant) agree it is safe.
10. Prove a **candidate promotion run** completes **without someone hand-editing files** mid-run to “make it green.”
11. Prove the **promotion path cannot merge** if non-regression gates fail.
12. Wire **automatic demotion** for any prompt/policy/memory lane that breaches **reliability or safety** thresholds after promotion (sandbox → shadow → canary → production ladder from the quality doc).
13. Whenever a **gate fails** or a **production incident** closes, add or extend **eval cases** so the failure becomes a permanent regression test.
14. On every material prompt/policy change, **replay held-out suites** and block if safety or reliability regresses versus baseline.
15. For each **adopt-now** technique you ship, attach the **evidence pack**: baseline vs candidate on held-out data, stress results, safety gate comparison, cost/latency deltas with confidence intervals.
16. Wire **dashboards and alerts** for **each SLO row** in the metrics doc (workflow reliability, `pass^k`, robustness, fault tolerance, safety, stability, performance, availability, observability) with the **named owner** and **breach action** documented.
17. Instrument and chart the **seven engineering KPIs** (gate-stage pass rate, retry rate per step, reviewer reject-to-accept ratio, schema validation failures, policy false negatives, heuristic hit rate and uplift, prompt-policy evolution win rate).
18. Prove **ERL-style** heuristics deliver at least **+2 percentage points** improvement in `pass^k` on the **full manifest** versus the pre-heuristic baseline, or document why not and get EM + Quality Owner decision (quality advancements bar).
19. When you publish a gate packet directory, **append one row** to the index table in `evidence/gate-packets/README.md` and set **`packet_id`** exactly as doc-precedence §10 describes.
20. For **GEPA-style** prompt evolution, prove **offline plus canary win rate** versus baseline with **mandatory safety replay green** (quality advancements adopt-now #5).
21. Keep **unit**, **integration**, and **full-manifest end-to-end** test suites green with **stable repeatability** on every merge candidate that claims Gate 2 (delivery process Gate 2—same bar at promotion).
22. Prove aggregate stress results meet the **consistency**, **robustness**, and **fault tolerance** SLO targets from the metrics doc / Appendix A (quality advancements adopt-now #2).
23. When claiming **agentevals** without the Tech Lead substitute path, meet **all** doc-precedence §7 rules: spans **`plan`**, **`action`**, **`output`** per `docs/implementation/schemas/otel-span-stage-registry.json`; **mean(score) ≥ 0.85** across returned dimensions; **no** manifest `workflow_id` below **0.75** mean score in the sample; pin **agentevals**, **scorer config**, and **OTel exporter** versions in the packet; any disabled scorer dimension needs **Quality Owner + Observability DRI** joint rationale and you may not disable **more than half** of dimensions.

**Exit check:** roadmap Phase 6 acceptance, and baseline observability was true **before** you treated high-volume stress runs as evidence.

---

## Phase 7 — Routing between Ollama and vLLM (end of **M3**)

**Goal:** the system chooses backends responsibly, speculative decoding is tuned without breaking SLOs, and you have logs and benchmarks.

**Self-learning link:** improved prompts and heuristics must stay **valid** when routing, decoding, and load change—otherwise learning optimized in the lab **fails in real local operation**.

1. Implement **routing** that can send work to **Ollama** and to **vLLM**.
2. Add **speculative decoding** tuning that respects **latency and quality** SLOs under changing load.
3. **Log every routing decision** (who chose what, for which run).
4. Benchmark **every manifest workflow** under an agreed load profile; save charts or tables for evidence.
5. Compare results to **latency** and **quality** budgets and file gaps as defects if you miss.
6. For **SLO-aware speculative decoding**, keep evidence that **p95 latency stays inside SLO** with **no safety or reliability regression** across **two consecutive weekly operating windows** (quality advancements adopt-now #3).
7. Have **Inference DRI** (tech decisions) sign off on **routing policy and benchmark governance** for the evidence you attach at promotion.

**Exit check:** roadmap Phase 7 acceptance.

---

## Cross-check — parity math (after Phase 7 evidence exists, repeated through exit)

These steps implement doc-precedence §4 and the tech decisions parity contract.

**Self-learning link:** parity proves a **learned** policy or memory lane does not encode **backend-specific cheating**; disagreement between **Ollama** and **vLLM** is treated as a **learning or integration defect**, not noise to average away.

1. For **each** `workflow_id`, run the **same pinned inputs** on **Ollama** and **vLLM** and record an **ordered list of gate outcomes** (pass/fail + reason codes) for each side.
2. If the two lists have **different lengths**, treat parity as **failed** until the pipeline is fixed (do not average your way out of it).
3. If lengths match, compute **Hamming agreement** between the two lists; require **≥ 0.99 per workflow**, and **≥ 0.99** averaged across the manifest for the evaluation window.
4. Also prove **no critical safety disagreement** between backends on the release corpus.
5. Check **p95 latency** delta canary vs baseline **≤ 20%** where the tech decisions demand it.
6. Check **memory top-k overlap ≥ 0.90** on the seeded replay set.
7. Write down, for each release candidate, the full **parity dimension** set: backend, model pin + quantization, hardware class, Python and library versions, prompt and validator bundle versions, promptfoo revision, agentevals and DeepEval pins.

---

## Phase 8 — Observability and replay “for real” (start of **M4**)

**Goal:** on-call engineers can replay incidents; every subsystem failure mode has been drilled; **every** manifest workflow has at least one successful replay trace (batching allowed).

**Self-learning link:** when a promoted change **hurts** trajectories or safety, replay and drills are how you **attribute** the regression and **roll back** the right artifact (policy, memory, or routing)—without that, learning is **irreversible guesswork**.

1. Add **replay hooks** and prove an engineer can complete **incident replay** and a **root-cause drill** in the validation environment.
2. Build or tune **dashboards** and **alerts** so noise is low and real fires are loud.
3. Prove **audit logs** cover required actions (who did what, when, under which policy version).
4. If you use **Langfuse**, get **Observability DRI approval** first; if not approved, write that down and stay on **OpenTelemetry + structured logs + agentevals** only.
5. Maintain a **drill matrix** that hits **each subsystem failure mode** you planned for.
6. Collect **at least one successful replay trace per manifest `workflow_id`** (no gaps).
7. Update manifest **`Last green gate run`** links from `no-evidence-yet` to a real **immutable URL** or a path under `evidence/gate-packets/…` when evidence exists.
8. Prove **coordination diagnostics** (multi-step, multi-agent runs) are observable enough for incident review—align with the “rigorous testing / coordination checks” intent in the design’s research notes (dashboards or drill scripts).

**Exit check:** roadmap Phase 8 acceptance. If Phase 8 later **regresses**, treat earlier heavy stress evidence as **stale** and re-run stress after recovery (doc-precedence §8).

---

## Phase 9 — Local API, CLI, and schedules (still **M4**)

**Goal:** operators can run and audit the system without a developer’s laptop tricks; scheduled runs obey the same gates and telemetry as interactive runs.

**Self-learning link:** schedules make **continuous signal** (runs, evals, canary checks) routine so personas **keep learning** in operation—not only when a developer kicks off a job.

1. Ship a **local runtime HTTP API** (or agreed interface) that matches the execution semantics.
2. Ship a **CLI** with the same semantics.
3. Ship **scheduling** for unattended runs.
4. Demonstrate **start, pause, resume, and audit** through **both** CLI and API on real workflows.
5. Prove **scheduled runs** use the **same gates** and **same telemetry** as interactive runs (no hidden “scheduler bypass”).
6. Publish a **local operations runbook**: common tasks, failure symptoms, who to call, how to roll back locally.

**Exit check:** roadmap Phase 9 acceptance.

---

## Phase 10 — Single production exit (end of **M4**)

**Goal:** one controlled promotion with soak, rollback proof, and a complete evidence story.

**Self-learning link:** exit proves the **whole loop** is live: memory + eval + evolution + demotion + observability + parity, **governed** under soak—**self-learning personas**, not a frozen demo.

### Build and verify (final integration)

1. Confirm **production-grade observability** from Phase 8 is still true.
2. Confirm **Phase 9** runtime surfaces are still true.
3. Run the **five validation gates** from the delivery process on the candidate: **(1)** contract and schema gate including **compatibility** checks on published interfaces, **(2)** quality gate (**unit**, **integration**, and **full-manifest E2E** with stable repeatability; DeepEval; RAGAS where relevant; promptfoo; **agentevals** per doc-precedence §7 **or** Tech Lead-signed full re-run substitute), **(3)** safety gate, **(4)** performance gate (**latency and resource** targets vs current SLO budgets), **(5)** observability gate (OTel mandatory; Langfuse optional).
4. Build a **gate packet** under `evidence/gate-packets/<packet_id>/` (or an immutable CI archive) with **`MANIFEST.json`** exactly as `evidence/gate-packets/README.md` requires, including **`backends`: `ollama` and `vllm`**, tool pins, `normalization_regex_table_version`, and `otel_span_registry_version`, **plus** **OTel sample hashes** or equivalent immutable trace references required by `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` §10.
5. Map **every artifact** in the packet to **every** `workflow_id` in the manifest (no orphan workflows).
6. Attach **promptfoo**, **DeepEval**, **RAGAS or signed RAGAS N/A**, and **agentevals** (or the documented Tech Lead substitute) so nothing is silently missing, **plus** the rest of the delivery-process milestone bundle: **test report links**, **policy validation output**, **performance benchmark results**, **telemetry dashboard links**, and **sign-off records** from each gate owner.
7. Prove **telemetry completeness ≥ 99%** for the sampled runs you cite, or discard that sample and collect a valid one.
8. Implement and run **CI replay tests** named in `MANIFEST.json` that prove the **no-repeat-failure** rule for **critical** signatures (failure payloads validate against `docs/implementation/schemas/normalized-failure-signature.schema.json` at version **1.0.0**; hashing follows doc-precedence §6).

### Soak, rollback, and promotion rules

9. Run a **canary plan** with written pass/fail thresholds; confirm **on-call and escalation roster** (delivery process release readiness).
10. Execute **soak**: **24 hours** continuous and **at least 500** canary runs across manifest workflows (raise the count if EM + SRE say the manifest is large; never lower without a written exception).
11. During soak, keep **incident-free**: **no** Sev1/Sev2; **no** unresolved Sev3.
12. If **any confirmed unsafe action** slips through, or **completion rate drops below 99%** for **two 15-minute windows in a row**, execute **rollback**: freeze promotion, restore the last known good bundles, run **smoke + safety replay** before trying again.
13. Verify **rollback** on the **exact artifact** you intend to promote, including bundles for runtime, prompts/policies, validators, routing, and memory schema.
14. Confirm **no safety gate waiver** exists (waivers are not allowed for production promotion).
15. Confirm any **non-safety waiver** has owner, expiry, mitigation, at most **one** renewal, and EM review if someone tries more.

### Program-level “done” list

16. Satisfy **every** bullet in `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md` with evidence.
17. Satisfy **every** “production exit criteria” bullet in the implementation roadmap with evidence.
18. Satisfy **every** “done criteria” bullet in the platform **design** spec with evidence, including: full manifest compile+execute with gate outcomes; **no-repeat** behavior for critical failures; policy and temporal blocks; **both** backends; measurable, regression-safe improvement loop including **governed generative memory** and **prompt evolution**.
19. Run the **reliability stress suite twice in a row** with **no critical regressions** either time.
20. Clear **all critical risks** in the risk register or close them with an **EM-approved** residual you can live with.
21. Complete **release and rollback validation** with the **named owners** on the promoting artifact.
22. Keep **generative memory** and **prompt/policy evolution** **on** under governance (shadow/canary rules, audits, safety non-regression)—not parked as “phase two.”
23. Publish **release notes** and update **global runbooks** (delivery release readiness—same moment as promotion prep).
24. Collect **written sign-offs from each gate owner** named in the delivery process (Quality, Safety, SRE/Ops, etc.) for the final packet.
25. For **every** SLO or gate claim in the packet, write down the **sample size** and **time window** used (release gate sampling rule—missing math invalidates the claim).
26. Prove **all four `critical_slos` families** (Safety, Availability, Workflow Reliability, Observability—release gate terms) stay green through the soak window, with dashboard links.
27. Attach **trend packs** to the milestone review: pinned **promptfoo**, **DeepEval**, and **agentevals** artifacts when those tools are cited (metrics doc).
28. If anyone changes **`schema_version`**, the **normalization regex table**, or the **`criticality` rules** for failure signatures, get **Data/Memory DRI + Safety Owner** joint approval and version it with the manifest row set (release gate spec).
29. Review **every active risk R1–R8** in the risk register: each must have a working mitigation, an accepted residual with owner, or **closure** that meets **all** register closure rules—trigger absent **two** consecutive review cycles, **preventive checks** added when applicable, owner confirms **residual within accepted threshold**, and **critical** risks tied to release gates need the **incident-free soak** standard where the register demands it.
30. If a **manual promotion override** is ever needed, obtain **EM approval** plus **written risk acceptance** (metrics release guardrails).
31. After promotion, run the **post-release review** loop: verify **SLO compliance** during soak, **log incidents and near misses**, and **turn repeated failure patterns into new prevention checks** (delivery process §5).
32. Any change to **`docs/implementation/production-workflow-manifest.md`** after Phase 1 must follow **change control**: manifest edit + **DOR** + plan to **re-prove** every affected gate and workflow (manifest rules).
33. Run a **cross-doc consistency audit** (roadmap vs release gate vs metrics vs risk register vs manifest) so there are **no contradicting numbers or owners** left unfixed (master plan “acceptance rules for this package”).

**Exit check:** Phase 10 acceptance in the roadmap and a single, documented promotion event with immutable packets.

---

## All phases — weekly rhythm and every-task discipline

These repeat across the program (delivery process + playbook + master plan cadence).

1. **Monday:** lock scope for the week, review dependencies and risks, check DORs for incoming work (**weekly planning and risk review**).
2. **Wednesday:** architecture and integration checkpoint; read upcoming gates before merges pile up (**midweek checkpoint**).
3. **Friday:** gate board with a written outcome: **pass**, **block**, or **rollback prep**; include a **weekly risk register update** for open risks (risk register cadence).
4. **Monthly:** run the **operating review** on trend metrics and risk burndown (master plan), the **risk trend review** on open vs closed ratio and mitigation effectiveness (risk register), and the **executive summary** covering reliability, safety, and velocity posture (metrics doc reporting cadence).
5. **Daily:** each subsystem DRI does the **dashboard scan** prescribed in the metrics doc (not optional near exit).
6. Before **any** task starts, satisfy **DOR entry**: clear goal, machine-checkable acceptance tests named, interfaces and version impact noted, dependency map updated, security risks logged with mitigations, rollback and telemetry expectations written.
7. Before **any** task closes, satisfy **DOR exit**: EM + Tech Lead sign-off with a **named DRI** and a **due window**.
8. Build with **tests first** for each acceptance line (red → green → refactor), no skipped tests, no ignored **critical** lint, type, or **security** findings.
9. For **RAGAS**: if a suite truly does not test retrieval, attach **Quality Owner–signed N/A** and still run the other DeepEval tests. **Langfuse** being down is **not** an excuse to skip observability evidence if **OpenTelemetry** export and dashboards are complete (playbook + delivery process).
10. For **agentevals** gaps: either meet doc-precedence §7 floors or ship the **Tech Lead-signed** full re-run substitute—never stay silent.
11. For **flakes**: at most **three** deterministic retries per workflow per CI run; then **stop** and open a defect (no infinite retry).
12. For **Graphiti / Mem0**: do not add parallel memory stores without an ADR; default remains **Postgres + pgvector + RLS**.
13. For **dependency failure matrix** (Ollama, vLLM, Postgres, telemetry): define and test **happy, nil, empty, error**; on inference outage, **route to healthy backend or safe_denied** for **every manifest workflow**; on empty memory, continue only with **`no-memory` marker** and stricter reviewer; on validator timeout, **fail closed**; on telemetry sink outage, **block release** and use **local buffered audit logs** only if you must keep the lab running.
14. Before anyone says “phase done,” check: phase acceptance bullets, evidence mapped to **every** manifest row that exists at that time, **no open critical risks** without EM waiver, parity dimensions updated if models or pins changed.
15. **Waiver discipline:** any waiver needs owner, expiry, mitigation; **repeat waivers on the same subsystem** must trigger **EM + Tech Lead escalation** (delivery block policy); **never** waive the **safety gate** for production.
16. Publish a **12-month minimum backward-compatibility rule** (or stricter ADR) for every outward-facing contract between subsystems (tech decisions).
17. Implement **strong authentication** on control-plane and runtime APIs (**OIDC/JWT** for people; **service tokens or mTLS** between services).
18. Implement **default-deny authorization** with the named roles (**Operator**, **SafetyOwner**, **InferenceDRI**, **Auditor**, **ServiceAgent**) and **dual authorization plus immutable audit records** for **policy change**, **promotion**, **tenant override**, and **manual release override** (tech decisions).
19. Ensure **every tool call** carries signed context **`principal_id`, `tenant_id`, `run_id`, `step_id`, `policy_version`** and is **rejected on mismatch** (tech decisions).
20. Do **not** implement **SpecRouter-style multi-level speculative chains** unless EM + Tech Lead explicitly promote them from **backlog** to scope (tech decisions backlog tier).
21. After **any critical risk fires** (see risk register), run an **immediate risk-board review** outside the Friday cadence if the trigger demands it (risk register cadence).
22. If you enable **TruLens**-compatible instrumentation, treat it as **supplementary only**—it must **not** replace the required **OpenTelemetry** evidence path (tech decisions).
23. For every meaningful decision, keep **evidence-first** artifacts: **links to runs**, **logs**, and **validation reports** attached to tickets or packets—not “trust me” messages (design non-negotiable).
24. When you are stuck, use the **execution playbook escalation table** (who owns schema vs safety vs memory vs CI vs promotion vs scope) instead of rerouting at random.
25. Follow the master-plan **decision policy**: never declare a **milestone** complete with unresolved **critical** defects, failed policy checks, or missing evidence; allow **only one** production promotion after **canary SLO adherence** and an **incident-free soak** (master plan + release gate spec).

---

## Go-live blocking items (metrics doc — do not skip near the end)

1. Wire **alerts**: page on **safety SLO breach**; page if **availability** is below target for **15 minutes**; warn and **freeze release** if **trace completeness** is under **99%** for **30 minutes**.
2. In the **14 days before go-live**, run and record: **rollback drill** on the current candidate, **inference outage drill**, **memory degradation drill**.
3. Get **primary and secondary** on-call acknowledgments in writing with **runbook links** attached to the packet.
4. Confirm dashboard links show **gate pass trends, latency, errors, and safety events** (metrics dashboard requirements).

---

## Appendix A — Service level objectives (verify each explicitly before promotion)

Use the metrics doc for exact numbers and owners. Before you call the program done, prove each row is instrumented, has a dashboard, and has a **breach runbook** tested at least once.

| # | Domain (SLO) | Plain-English verification |
|---|----------------|----------------------------|
| A1 | Workflow reliability (step gate pass rate ≥ 97% / 7d) | Dashboard + alert wired; breach path tested (block promotion + corrective action). |
| A2 | Consistency (`pass^k`, k=5, ≥ 95% / 7d) | Metric computed on manifest; breach blocks promotion. |
| A3 | Robustness (perturbation survival ≥ 92% / 7d) | Approved perturbation set exists in CI; breach opens robustness queue. |
| A4 | Fault tolerance (injected faults ≥ 90% / 7d) | Fault harness lives in CI/nightly; breach freezes rollout. |
| A5 | Safety (known unsafe blocks 100% / 7d) | Red-team fixtures prove blocks; breach triggers emergency patch + replay. |
| A6 | Stability (no repeated unmitigated critical signatures / 30d) | Failure-signature store + prevention checks wired; breach freezes lane. |
| A7 | Performance (p95 ≤ 8s baseline flow / 24h) | Latency dashboard per workflow; breach triggers routing/decode tuning. |
| A8 | Availability (completion ≥ 99% / 24h) | Availability dashboard; breach triggers incident + rollback if persistent. |
| A9 | Observability (trace completeness ≥ 99% / 24h) | Trace completeness dashboard; breach blocks release. |

---

## Appendix B — Engineering KPIs (instrument every line)

Each KPI from the metrics doc must have a query, a dashboard panel, and an owner who acts when it moves the wrong way.

| # | KPI | What “done” looks like |
|---|-----|-------------------------|
| B1 | Test pass rate by gate stage | Breakdown chart by gate stage; alerts on sustained drops. |
| B2 | Retry rate per workflow step | Per-`workflow_id` / step heatmap; investigate outliers. |
| B3 | Reviewer reject-to-accept ratio | Trend line; sudden spikes trigger triage. |
| B4 | Schema validation failure rate | Count and classify failures; block promotion if unexplained spike. |
| B5 | Policy validation false-negative count | Must stay at **zero** for known violations; any >0 is Sev-class incident. |
| B6 | Heuristic retrieval hit rate and uplift | Shows ERL injection is helping; flatlines trigger Quality review. |
| B7 | Prompt-policy evolution win rate vs baseline | Tracks GEPA-style promotions; demotion wired to regressions. |

---

## Appendix C — “Phase complete” and playbook corner cases (verbatim expectations)

Before you tell anyone a roadmap phase is finished, you must satisfy **all** of these (from `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md`):

1. Every **acceptance bullet** for that phase in the roadmap is **demonstrably true** (not “almost”).
2. Evidence is mapped to **every** manifest `workflow_id` that exists at that date.
3. There are **no open critical risks** in the risk register unless the EM granted a **written waiver** with compensating controls.
4. If you changed **models**, **suite pins**, or **backends**, you updated the **parity dimensions** list in the tech decisions doc so the next reader can reproduce your proof.

**Playbook corner-case table (must be handled, not hand-waved):**

| Situation | Required behavior |
|-----------|-------------------|
| RAGAS not applicable for a suite | Gate packet includes **Quality Owner–signed one-line N/A**; other DeepEval tests still run. |
| `agentevals` cannot run on traces | Attach Tech Lead–signed **full re-run** logs meeting the **same** pass/fail bar; **silent omission = failed gate**. |
| `promptfoo` / CI flake | Up to **3** deterministic retries per workflow per run; then **block** and file a defect. |
| Langfuse not deployed | **Allowed** if OTel + dashboard links are complete. |
| Instructor exemption | **Numbered ADR** listing `workflow_id` and step IDs. |
| Graphiti / Mem0 not selected | Default **Postgres + pgvector + RLS** only; no silent parallel memory store. |

---

## Design contract — per-step runtime order (embed in Phase 3–5 testing)

For **every** persona step, the running system must be able to demonstrate this order end to end:

1. Fetch memory (same tenant, similar past failures, successful patterns).
2. Run the planner with tree search; pick or update the active plan branch.
3. Run **architect** (approach and risks for the chosen branch).
4. Run **implementer** through the tool gateway; write artifacts.
5. Run **temporal** checks on the action sequence.
6. Run **validators** (schema, policy, quality, safety, domain).
7. Run **reviewer** with explicit accept/reject reasons.
8. On reject: bounded retries with tighter constraints and a reflection payload.
9. Write episodic and generative memory updates, metrics, and audit records as your design specifies.

---

*This checklist was merged from the implementation roadmap, master plan, production manifest rules, execution playbook, delivery and release gate specs, gate packet README, doc-precedence, tech decisions, design spec, quality advancements, research/OSS integration, metrics and SLOs doc, and risk register. If a step references a file path, treat that file as the detailed spec for that step.*
