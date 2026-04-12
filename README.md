# Persona Library

This package **is** the product: a Python library your application imports. You give it a **persona definition** in YAML—who the coworker is, how they think, which tools they may use, and—for each **task type**—which **stages** and **steps** to run. The library turns that YAML into a **runnable persona** with **memory**, **self-learning** (durable retrospectives and gated promotion), and **orchestration kept inside** the package. Your app stays small: **configure credentials and paths once**, build a **Squad** (or **Pipeline** that owns one Squad) from that YAML, then call **`launch(inputs=...)`**—a **`launch`-first** entrypoint in the spirit of common multi-agent stacks, with **our own** type names. Stages, steps, Architecture / Implementer / Reviewer roles per step, validators, checkpoints, and replay all run **behind the scenes**.

The sections below keep every technical rule from the design. Read in order for the full picture, then use the bullets and tables when you build.

---

## Inspired orchestration surface (distinct names, one persona)

The public Python API takes **inspiration** from popular multi-agent patterns—**without** reusing another library’s identifiers. **Pipelines** sit at the backbone (outer state and wiring), **Squads** are the runnable unit bound to one persona, **Specialists** and **Assignments** are the building blocks, and **`launch`** / **`alaunch`** (plus batch and threaded async variants) are the execution entry points. The stable surface is **ours**: `Specialist`, `Squad`, `Assignment`, `RunOrder`, `SquadReport`, `Pipeline`, `@entry`, `@follows`, `launch`, `blueprint`, decorators such as `@SquadBase`, `@specialist`, `@assignment`, `@squad`, `@before_launch`, `@after_launch`, and matching async helpers where this library defines them.

**What stays different under the hood (the crux):** everything still runs from **one persona definition in YAML** per active configuration. The engine is **not** an open-ended multi-persona studio. It **materialises exactly one persona** at a time: ordered **stages → steps**, each step running **Architecture → Implementer → validators → Reviewer**, with **ToolGateway**, **tenant isolation**, and **gated memory**. The vocabulary above is a **thin facade and ergonomics layer** over that pipeline—not a second orchestration philosophy.

**Scope rule:** v1 supports **one logical persona per loaded YAML** (one “world” of task types, memory, and tools). You may still pass lists of `Specialist` and `Assignment` objects into `Squad(...)` for a conventional call style, but the library **generates or binds** those objects from the same persona file; you do not design unrelated specialist teams side by side inside one product instance.

| Inspired idea | Name in this library | What it actually drives here |
|-------------|---------------------------|------------------------------|
| **Outer workflow spine** | `Pipeline`, `@entry`, `@follows`, `state`, `launch()`, `blueprint()` | Tenant/workspace lifecycle, optional outer workflow, checkpoints/resume hooks; may delegate the heavy lift to a single **Squad** that represents the persona. |
| **Runnable team unit** | `Squad`, `specialists`, `assignments`, `order`, `memory`, `verbose`, `stream`, … | One **persona-bound** squad: `launch(inputs=...)` selects a **task type** (from YAML), pins its hash, and runs stages/steps with validators and reviewer gates. |
| **Role participant** | `Specialist` (role, goal, backstory, tools, …) | Facade or template-bound specialist objects; per **atomic step**, the real work still maps to **Architecture / Implementer / Reviewer** roles defined in YAML, not free-form role chatter. |
| **Unit of delegated work** | `Assignment` (description, expected_output, specialist, …) | Represents a **YAML task type** slice or an internal step-facing assignment for streaming/logging; execution order follows **stages**, not ad-hoc graphs. |
| **Ordering policy** | `RunOrder.sequential` (default), optional layered mapping | **Sequential** maps to ordered stages and steps. **Layered** maps to “validate before proceed” only where it aligns with **Reviewer + human gate** policy—no LLM-only merge authority. |
| **`launch` / `alaunch` / `launch_each` / …** | Distinct method names (see §10) | Internally call the materialiser + LangGraph adapter; return values are **`SquadReport`** / **`AssignmentOutcome`**-shaped for structured access (`raw`, `json_dict`, `assignments_output`, `token_usage`, …). |
| **Memory / knowledge** | `memory`, `knowledge_sources`, embedder config | Wired to **memory bank + capsules + FTS** (and optional vectors), tenant-scoped, with **gated promotion**—implemented only by this library’s stores. |
| **`@before_launch` / `@after_launch`** | Hook decorators | Map to **input normalisation** (tenant, workspace, idempotency key) and **output shaping / redaction** before returning `SquadReport`. |

---

## How we get from idea to shipped behaviour (one line each)

These lines tell the whole story from “idea” to “library behaviour.” Later sections add names, tables, and edge cases; **nothing here drops a feature**.

1. We ship a **normal Python library** (wheel/sdist) that your app imports—this package **is** the product, not a sample app wrapped around it.
2. Your integration code stays **tiny**: supply an **API key** (or auth bundle) and a **path to persona YAML** during **`configure` / `init`**, materialise **one** **`Squad`** for that persona, then call **`launch(inputs=...)`** (including a **task type id** in `inputs` when multiple task types exist)—**everything else** (graphs, model roles, memory, tools, checkpoints) runs **inside the library**.
3. The **persona YAML** is the **factory definition**: identity, models, tools, memory settings, and—per **task type**—the **ordered stages** and **ordered steps** that define how that kind of work gets done.
4. **`configure` / `init`** parses and validates that YAML, wires **tenant + workspace + memory stores + tool registry**, and returns (or binds) a **Persona** handle and/or a ready **`Squad`** your app keeps for many **`launch`** calls.
5. **`Squad.launch`** (and async **`alaunch`**, batch **`launch_each`**, and the other launch variants) resolves the right task template from the YAML, **pins its version/hash** on the new run row, and starts the hidden orchestration loop for that run only.
6. **Personas** are **generated at runtime from your YAML**—same file checked into Git; bump `version` when behaviour or steps change.
7. **Task templates** are the **per–task-type** sections inside that YAML (or split files merged at load time)—still **reviewable in Git** like CI.
8. A **task run** is one **`launch`** with concrete inputs (for example “review this PR” or “draft this campaign”).
9. Every run is tagged with **`companyId`** so we always know **which customer or org** owns that row of data—even if you only use one customer today.
10. Optionally we also tag **`workspaceId`** when one customer has **several repos or workspaces** and you want memory and paths kept apart inside that customer.
11. When a run starts, we **open the right database slice and folder** for that customer so paths and memory cannot wander across tenants by accident.
12. **Before** the first model call for that task, we **load the memory bank**—your human-written Markdown “how we work here” slice—so the run does not cold-start from zero context.
13. Still before serious work, we **search past task capsules** (short structured “what worked / what hurt”) filtered by tenant and persona so **similar past jobs** show up as **citations**, not whispered facts.
14. The library **materialises** the YAML into an internal ordered plan (stages → steps); that materialisation is **deterministic code + pinned content**—it **does not rewrite** your YAML mid-run.
15. The run walks **stages in order**: think chapters of a checklist for that **task type**.
16. Inside each stage we walk **steps in order**: think lines inside a chapter.
17. **Stage two never starts** until **every step in stage one** has passed validators **and** been **accepted by a Reviewer**.
18. **Every step** runs **three LLM roles in order**: **Architecture** agent (approach and constraints for this step), **Implementer** agent (does the work with tools), then **non-LLM validators**, then **Reviewer** agent (accept / reject / escalate)—each with **its own customisable prompts** (paths, inline text, or message lists) declared **on that atomic step** in YAML, with optional persona-level defaults underneath.
19. The **Architecture** agent outputs a **structured plan slice** for the step (risks, sub-goals, what “done” means in its own words within YAML bounds)—usually **read-heavy or tool-light** per your YAML.
20. The **Implementer** agent uses **only tools that step’s YAML allows**—terminal, search, files, git, browser, etc.—and produces the **implementer draft** (often JSON) matching the step output shape.
21. Every tool call goes through a **gateway**: we validate arguments with a schema, enforce allowlists and rate limits, and **write an audit line** (what ran, hashed args, how long it took).
22. **Non-LLM validators** run next—tests, linters, JSON Schema, secret scanners, custom checks—whatever the YAML listed by **stable ids** from one central catalog.
23. **Validators are the boss for “is this step technically OK”**—not another chatbot agreeing with the Architecture or Implementer pass.
24. The **Reviewer** reads the **Architecture output**, **Implementer output**, validator results, and your **criteria** list; it returns **accept**, **reject with a reason**, or **escalate** (for example critical security).
25. **Architecture, Implementer, and Reviewer do not share one continuous private chat log**—the Reviewer is fed **declared outputs and evidence**, not raw chain-of-thought from the other roles, so review stays a real second pass.
26. If the Reviewer **rejects**, **Implementer** (and if policy says so, **Architecture**) may retry up to a **policy limit**, and each retry must show **real progress** (for example a different output hash or better validator score), not the same wrong answer pasted again.
27. If retries run out, the run pauses in **`awaiting_human`** until a person approves, edits, or aborts—your escape hatch.
28. If the Reviewer **escalates**, policy can send the run straight to **human** without burning more automatic retries.
29. When a step is **accepted**, we **append an episodic record**—the machine-friendly trail of tools, hashes, validator links—so you can **replay** and debug later.
30. Optionally we also stage **“step learning” rows**—short signals about failures or fixes—under promotion rules so noise does not flood long-term memory.
31. When **every step in a stage** is accepted, we clear or archive **stage scratch (“working memory”)** per policy and **open the next stage**.
32. When the **whole task ends**—success, failure, cancel, or partial—we write or update a **retrospective capsule**: what worked, mistakes, paths touched, validator fingerprints, in a **searchable** row with **redaction** applied first—that is the core of **self-learning** for the next **`launch`**.
33. **Full-text search (FTS5)** indexes those capsules so the **next** similar task can pull them up quickly; **vector search** is optional for “smells like last month’s incident” style matches.
34. **Promotion** from raw logs into **long-term playbooks** or the git-tracked memory bank is **gated**: humans or strict policy decide—so a bad run does not automatically become company law.
35. **Mistake clustering** (for example embeddings + DBSCAN) may highlight recurring patterns for analytics and prompt hints—but **never** as unvetted automatic doctrine.
36. **Dedupe fingerprints** on mistakes reduce ten copies of the same lesson crowding search results.
37. If you enable a **Markdown run diary** under the workspace, we **append human-readable sections** after meaningful events so PMs can read a story; **automation still trusts** SQLite + validators, not prose alone.
38. **DAG-first mode** (future) lets a global planner own a branching plan—but it still **compiles down to the same step records** so checkpoints, validators, and replay stay one system.
39. **Follow-up messages** (you, CI bots, tickets) land in a **queue** and merge into plans under **rules** so nobody silently widens tools or scope mid-run.
40. **Plan or YAML changes** after the fact require a **version bump** and a short **why** note; we **never silently rewrite** steps that already finished.
41. **Idempotency** on **`launch`** (and any thin `execute_task` alias) is defined and tested so double-clicks do not spawn ghost runs—keys are scoped per **(companyId, key)** when you pass them.
42. **Hard caps** cover retries, wall clock, tokens, and dollars—**per task** and **aggregated per tenant**—so one customer cannot drain the host.
43. **Workspace jail** means every file path resolves under that customer’s allowed root; we reject escapes, bad symlinks, and mismatched tenant ids on tool calls.
44. **Shell** gets timeouts, max output size, and a deny list for obviously dangerous patterns; high-risk deploys can move execution to **stronger isolation** without changing YAML shape.
45. **Network tools** treat fetched text as **untrusted**; allowlists apply where you need tight control.
46. **Secrets** stay out of model context by default; scanners run as validators before risky commits; **replay exports are redacted**.
47. Advanced callers can still use lower-level **`RunSession`**, **`memory.search`**, **`replay.export`**, **`approve`**—but the **happy path** is: **`configure` / `init` + `Squad.launch`** (optional **`Pipeline.launch`** when you need outer state). A legacy **`execute_task(...)`** alias may exist as a one-line forwarder to **`launch`** for older integrations.
48. **Extension hooks** let you register **custom tools** and **custom validators** without forking core types into app code everywhere.
49. **Hermetic CI** uses a **fake or recorded model** and **no network** in unit tests, plus **cross-tenant negative tests** that prove company A cannot read company B’s ids.
50. **Phase A** delivers one vertical slice: one persona YAML, one task type, full **Architecture → Implementer → validators → Reviewer** loop per step, SQLite per tenant, replay, human gate, offline tests.
51. **Phase B** adds smarter retrieval: vectors, async embedding jobs, hybrid rank, optional mistake clustering analytics.
52. **Phase C** adds breadth: more personas and task types, optional DAG templates on the **same** step engine, richer promotion workflows for playbooks.
53. **Non-goals for v1** stay honest: we do not require Kafka-scale buses; we do not let an LLM score alone approve a merge; we do not merge memory across tenants without an explicit audited export bridge.
54. **What success looks like:** each persona you define in YAML **keeps getting smarter** in a controlled way because capsules and search surface **prior evidence**; quality stays high because **validators and humans** hold the line—not because we pretend models never repeat errors.

---

## 1. Product goal

The library is the **factory and runtime** for AI coworkers: you pass **persona YAML**, build a **`Squad`**, call **`launch`**, and get **`SquadReport`** while the package wires memory, learning, tools, and the three-agent step loop **behind the scenes**.

It should:

- **Materialise personas from YAML** at `init` time (and per run): identity, models, tools, memory policy, and **per–task-type** definitions (**stages → steps**).
- Run each **`launch`** as **ordered stages**; each stage contains **ordered steps** for that task type.
- For **every step**: an **Architecture** agent shapes the approach; an **Implementer** agent does the work with tools; **non-LLM validators** run; a **Reviewer** accepts, rejects, or escalates. **No step completes without Reviewer confirmation** (after validators pass).
- Keep **stages sequential**: stage *k+1* starts only when every step in stage *k* is confirmed.
- Load **memory and precedents before step-level LLM work**, and **write structured outcomes** (episodic + retrospective capsules) so later **`launch`** calls retrieve lessons—**self-learning** with **gated** promotion to long-term doctrine.
- Expose **terminal, search, filesystem, git**, and other tools only through a **registry + gateway** (allowlists, schemas, audit).
- Scale from **one organisation / one workspace** to **many tenants** (`companyId`) without cross-tenant data leaks.
- Keep **orchestration** (e.g. LangGraph) **inside an adapter**; the **default public API** is the **Pipeline / Squad / Specialist / Assignment** surface: **`launch` / `alaunch`**, optional **`Pipeline`** + **`blueprint`**, with optional advanced entry points (`RunSession`, replay, memory search).
- Expose **composable stop rules** (see §10.3) so caps, clocks, token budgets, and cooperative cancel are one coherent policy surface—not only prose in §11.
- Publish a **versioned event schema** for `stream_task_events` and optional **message-path middleware** at role boundaries (see §10.3).

Retrieval plus gated memory **strongly reduces** repeated mistakes; **validators and human gates** prevent silent regressions. No design can promise “never wrong twice” without lying—this design encodes **process and evidence** instead.

---

## 2. Non-goals (v1)

v1 is **not** a giant cloud SaaS, does not let chatbots vote on shipping, and does not silently blend two customers’ memories.

- Mandatory Kafka/SQS or hyperscale multi-region SaaS.
- LLM-as-judge for merge/shipping authority (LLM hints may exist; **mechanical validators decide**).
- Cross-tenant memory merge or handoff without explicit audited export policy.
- **Peer specialist-to-specialist handoff** or **dynamic router / “who speaks next”** selection inside a step. Each step stays **Architecture → Implementer → validators → Reviewer**; future **DAG** mode is still **planner → materialised steps**, not arbitrary group-chat topology.
- **Distributed agent runtime** in v1 (separate processes, mesh RPC, pub/sub topics as the primary execution model). The default remains **in-process** orchestration with **SQLite per tenant** and an optional LangGraph adapter.
- **First-class multimodal role traffic** (e.g. images or audio as native messages between roles) in v1. Rich data flows through **tools**, **files under workspace jail**, and declared **structured outputs** unless a later version extends the contract.

---

## 3. Core execution contract

These rules define the **pipeline persona** runtime. Optional **DAG-first** mode (a **global planner** owns a branching plan) may exist later but must compile to the same internal **step/todo** records for checkpoints and replay.

```
Run  (one Squad.launch / one task run)
 └── Stage (ordered)
       └── Step (ordered)
             1. Resolve tenant + workspace; bind ToolGateway.
             2. Load memory context (memory bank + retrospective search) — see §7.
             3. ARCHITECTURE AGENT: step-level approach, risks, “done” shape (structured output per YAML; tools optional / read-first).
             4. IMPLEMENTER AGENT: tools + prompts + structured implementer draft.
             5. VALIDATORS (non-LLM): authoritative pass/fail.
             6. REVIEWER: ACCEPT | REJECT(reason) | ESCALATE — fed Architecture + Implementer outputs + validator evidence, not a merged private transcript of all three.
             7. On ACCEPT: persist episodic record; advance when all steps in stage are done.
             8. On REJECT: bounded retries with progress proof (e.g. output hash must change); Implementer and optionally Architecture rerun per policy; then awaiting_human if exhausted.
             9. On ESCALATE: awaiting_human per policy (e.g. critical severity).
```

**Invariants**

- **Architecture, Implementer, and Reviewer do not share one continuous conversation transcript** for the step. The Reviewer sees **declared structured outputs** and validator results—not raw hidden chain-of-thought from Architecture or Implementer.
- **Validators outrank LLM agreement.** Multiple models agreeing is not evidence of correctness.
- **YAML defines what** (stages, steps, per-role prompts/tools, criteria, validator ids); the **library enforces how** (the loop above). YAML is versioned and content-hashed per run.

---

## 4. Concept model

Words you will see everywhere in code and docs:

| Concept | Definition |
|--------|------------|
| **`companyId`** | Tenant key on **every** persisted row and API mutation. Maps to “customer,” “org,” or “division” per deployment. Single-tenant dev may use a fixed default only in documented profiles. |
| **`workspaceId`** | Optional slug for a repo or workspace **inside** a tenant. Composite `(companyId, workspaceId)` selects roots, memory paths, and vector namespaces. |
| **Persona** | **Runtime object materialised from persona YAML** at `init`: policies, default models, tool enablement, memory settings, registry of **task types** (each with its own stage/step graph). |
| **Task template** | Definition of **one task type** inside persona YAML: `stages[] → steps[]`, memory block, output schema, policies (retries, human timeouts). |
| **Task run** | One **`Squad.launch`** (or equivalent **`Pipeline.launch`**) for a task type with inputs, budgets, pinned template hash, bound `companyId` / workspace. |
| **Materialiser** | Library code path: validate YAML + environment, resolve task type, build internal ordered plan; **compose per-step, per-agent prompts** from YAML + persona defaults + **injected** memory/task context (see §5.1); **never rewrites** pinned YAML mid-run. |
| **Architecture agent** (per step) | First LLM pass **inside the step**: approach, constraints, risks, structured plan slice for the Implementer—tool use per YAML (often read-first). |
| **Implementer agent** (per step) | Second LLM pass **inside the step**: runs allowlisted tools, produces the **implementer draft** matching output schema. |
| **Reviewer agent** (per step) | Third LLM pass **inside the step**: judges Architecture output + Implementer output + validators + criteria; accept / reject / escalate. |
| **`StopRule`** | Composable termination unit (§10.3); evaluated with caps, clocks, human-pending, and cancel signals. |
| **`RunDriver`** | Optional narrow handle for one **`task_id`**: cancel, resume event cursor, poll status—without rebuilding a **`Squad`**. |
| **`AssignmentOutcome`** | Structured slice for **one** assignment inside a finished or partial run (pairs with **`SquadReport`**). |

---

## 5. Task YAML (authoritative shape)

YAML is the **recipe** that **defines the persona and each task type** (stages and steps). Each step names **three agents** (Architecture → Implementer → Reviewer). Validators stay **ids** pointing at one real implementation so your checklist cannot drift away from what the code actually runs.

Tasks are **declarative** and **reviewable in Git**—same mental model as CI.

**Required structure**

- `persona`, `task` (task type id), `version`.
- `memory`: at minimum `search_before_start`, caps for injected retrospectives, flags for episodic write per confirmed step and capsule on terminal outcome.
- `stages`: ordered list; each stage has `id`, optional `name`, ordered `steps`.
- Each **atomic step** includes: `id`, `name`, and three blocks—**`architecture`**, **`implementer`**, **`reviewer`**—each of which **must** declare how that agent is prompted for **this step only** (see §5.1). Also: optional `input_schema` / `output_schema` per agent where useful, **`implementer`** tool allowlist (synonym **`executor`** allowed for migration only), **`reviewer`** **criteria** list, optional `max_rejections` / `escalate_on_severity`, and `validators[]` (catalog **ids** only—no ad-hoc shell duplicated in YAML).

**Rules**

- Validator and tool references resolve through a **single catalog** in code to avoid drift with CI or local scripts.
- Stage *n* cannot start until all steps in stage *n−1* are **confirmed** (ACCEPT + validators passed).

### 5.1 Per-step, per-agent prompts (atomic customization)

Every **atomic step** is its own mini product: you can use **different instructions** for the Architecture, Implementer, and Reviewer agents on that step—**without** changing other steps. Defaults can live on the **persona**; each step **overrides** only what it needs.

For **each** of `architecture`, `implementer`, and `reviewer`, the YAML **must** supply at least one of the following (combinations allowed; the library merges them in a **documented order**—typically system instructions first, then persona-level defaults, then step overrides, then **library-injected** context such as task inputs, memory citations, and upstream step outputs):

| Field (per agent, per step) | Meaning |
|----------------------------|---------|
| `system_prompt_path` | Path to Markdown/text file: **system** role for that agent on this step only. |
| `user_prompt_path` | Path to template file: **user** message; may contain `{{placeholders}}` filled by the runtime. |
| `system_prompt` / `user_prompt` | **Inline** strings when the prompt is short or generated; still versioned with the YAML. |
| `prompt_messages` | Optional explicit list of `{role, content}` for advanced layouts (tool-result replay, few-shot) — must pass schema validation. |
| `model` / `temperature` / `max_tokens` | **Optional per-agent, per-step overrides** of persona defaults (quality vs cost tuning per atomic step). |
| `stop_sequences` / `tool_choice` | Optional provider-specific knobs where the stack supports them. |

**Inheritance:** Persona YAML may define **`default_prompts.architecture`**, **`default_prompts.implementer`**, **`default_prompts.reviewer`**; a step **merges** defaults with its own block, with **step fields winning** on conflict.

**Injection contract:** The library **always** documents which **variables** it injects into templates (for example `{{task.input}}`, `{{memory.citations}}`, `{{prior_step_outputs}}`, `{{workspace.root}}`). Templates **must not** execute code; only **string substitution** from an allowlisted context object.

**Pinning:** The resolved prompt bundle (paths + hashes + inline snippets) is **recorded on the run** so replay reproduces the **exact** instructions used for that atomic step.

Illustrative layout (organisation-owned, outside the core package):

```text
personas/
  developer/
    persona.yaml
    tasks/
      code-review.yaml
  marketing/
    persona.yaml
    tasks/
      campaign-brief.yaml
```

---

## 6. Memory subsystem

There are **three kinds of memory**: (1) **handbook pages** humans curate in git, (2) **machine cards** of past runs in SQLite you can search, (3) **scratch paper** for the current stage. **Trust** flows top-down: handbook and structured cards beat vague old chat.

### 6.1 Layers (trust order within a tenant)

When retrieval conflicts, **within the same `companyId`**:

1. **Memory bank** — human-curated Markdown (and optional JSON) under the tenant workspace: principles, ADRs, brand rubrics.
2. **Task outcome capsules** — structured retrospectives (`what_worked`, `mistakes`, paths, validator ids); **FTS5** required; **vectors optional** (e.g. sqlite-vec, Chroma, LanceDB on disk).
3. **LTM / playbooks** — promoted only through **policy + gates** (and often human review for doctrine).
4. **Episodic** — append-only machine log per step (tool names, args hashes, validator output refs).
5. **Working / STM** — stage scratchpad; cleared or archived on stage boundary per policy.

**Run diary:** optional Markdown under `workspaceRoot` (e.g. `docs/agent-runs/…`) mirroring episodic events for humans; **automation** trusts SQLite + validators, not prose alone.

### 6.2 When to read

- **Before** first LLM call for the task: memory bank slice + top‑k retrospective search (filtered by `companyId`, persona, task id, optional path hints).
- **Before replan** (if DAG mode or recovery): query using failure message + validator id + paths.

Inject hits as **citations** (task id, date, path)—not silent facts.

### 6.3 When to write

- **After each confirmed step:** episodic row (and policy-driven staging for “step learnings”).
- **On terminal outcome** (`completed`, `failed`, `cancelled`, `partial`): **retrospective capsule** with redaction gates; FTS index updated immediately; embeddings async if enabled.
- **Promotion** to LTM / memory-bank: **gated**—failed or rejected doctrine must not auto-poison long-term playbooks.

### 6.4 “Never-ending memory” (engineering meaning)

- **Durable stores** + **search** + **tenant isolation**.
- **Mistake clustering** (e.g. embeddings + DBSCAN) may be used for **analytics and prompt hints**, not as ungated truth.
- **Dedupe fingerprints** on mistake categories reduce noise.

---

## 7. Tools & security

Tools are **superpowers with paperwork**—every call is named, schema-checked, allowlisted, logged, and physically limited to the customer’s sandbox folder.

- **ToolGateway / ToolRegistry:** all tools registered with JSON Schema args, side-effect class, rate limits, logging (**tool id, args hash, duration, exit code / byte caps**).
- **Workspace jail:** every path resolves under `workspaceRoot(companyId[, workspaceId])`; reject escapes and cross-tenant ids.
- **Shell:** timeout, max output bytes, deny list (`curl | bash`, destructive `rm`, …); optional subprocess/container backend per deployment.
- **Network:** HTTP/search clients treat responses as **untrusted**; allowlists where applicable.
- **Secrets:** exclude `.env` from model context by default; run secret-scan **validators** before sensitive commits; redact replay exports.

**First-class tool families:** read/search, write/patch, terminal, git, browser/fetch (optional Playwright for JS-heavy pages), org-specific integrations (same gateway rules).

---

## 8. Validators

Validators are **little programs and commands** that return pass/fail. They beat opinions from another LLM.

- **Catalog maps** string `id` → handler (ruff, pytest, JSON Schema, citation checks, …).
- Validators return structured **pass/fail + message + evidence** for the Reviewer and logs (Reviewer may cite them against both Architecture and Implementer outputs).
- **No LLM in the validator catalog** for gating. Advisory LLM scores are optional and **cannot** advance a step alone.

---

## 9. Persistence & tenancy

Each customer gets **their own SQLite filing cabinet** by default so a bug in one query is less likely to leak another customer’s world. If you use one big database instead, **every row carries company id** and tests prove you cannot leak.

**Default:** **one SQLite file (+ WAL) per `companyId`** holding app tables (tasks, plans, episodic metadata, usage) and LangGraph checkpoints for that tenant, with a **per-tenant writer queue** to avoid lock contention.

**Paths:** `data/companies/{companyId}/…` for DB, vectors, and workspace roots—or equivalent manifest. **Alternative** single logical DB: **`company_id` on every row** + mandatory query scoping + Postgres RLS if used—**prove with leak tests**.

**API:** every mutating call carries **`companyId`**; idempotency keys are namespaced `(companyId, key)`; responses echo `companyId`, `traceId`, `taskId`.

---

## 10. Public library surface (stable)

Your app uses a **standard multi-agent mental model**—import **`Specialist`**, **`Squad`**, **`Assignment`**, **`RunOrder`**, call **`launch(inputs=...)`**—and the library hides LangGraph, checkpoints, the three roles per step, memory, and tools. Optionally wrap long-lived host state in **`Pipeline`**, **`@entry`**, **`@follows`**, and call **`pipeline.launch()`** / **`pipeline.blueprint()`** for pipeline-style orchestration. Power users can still drop down to `RunSession` when they need it.

Expose those types and method names as the **stable import surface** (`from persona_lib import Specialist, Squad, Assignment, RunOrder`, plus `Pipeline`, `follows`, `entry`, and project decorators from `persona_lib.project`). Keep `langgraph` imports **only** under `adapters/langgraph/` (or equivalent).

### 10.1 Default integration shape (illustrative Python)

The **names** below are the **contract** for this package’s public API. **One persona YAML** feeds **one** `Squad` factory result.

```python
# Stable imports: decorator + squad + launch pattern for this package.
from persona_lib import Specialist, Squad, Assignment, RunOrder
from persona_lib.project import SquadBase, specialist, assignment, squad, before_launch

@SquadBase
class MarketerPersona:
    """Exactly one persona class per deployment slice; YAML lists map to one materialised coworker."""

    specialists_config = "config/personas/marketer/specialists.yaml"
    assignments_config = "config/personas/marketer/assignments.yaml"

    @before_launch
    def bind_runtime(self, inputs):
        inputs.setdefault("company_id", "acme-corp")
        inputs.setdefault("workspace_root", "/work/acme/marketing")
        return inputs

    @specialist
    def marketer(self) -> Specialist:
        return Specialist(config=self.specialists_config["marketer"], verbose=True)

    @assignment
    def campaign_brief(self) -> Assignment:
        return Assignment(config=self.assignments_config["campaign_brief"])

    @squad
    def squad(self) -> Squad:
        return Squad(
            specialists=self.specialists,
            assignments=self.assignments,
            order=RunOrder.sequential,
            memory=True,
            verbose=True,
        )

result = MarketerPersona().squad().launch(
    inputs={"task_type": "campaign-brief", "product": "NeoToast", "audience": "SMB"},
)

# result.raw, result.json_dict, result.assignments_output, result.token_usage, … (SquadReport-shaped)
# Memory + retrospectives updated inside the library; no extra calls required.

# await MarketerPersona().squad().alaunch(inputs={...})
```

### 10.2 Expandable API catalogue (real-world surface)

Split **“happy path”** (two calls and done) from **operations** (pause, audit, bill), **extensibility** (hooks, custom tools), and **governance** (GDPR, tenancy). Below is the **full method set** a serious v1→v2 library should plan for—not every method ships on day one, but **reserving names and seams** avoids breaking consumers later.

**Design principles**

- **Tiering:** mark calls **stable**, **advanced**, or **operator-only** in docs so you can semver strictly.
- **Sync + async:** every long-running operation has **`…_async` / `await …`** twins where the language expects it.
- **Idempotency:** `submit_task*(…, idempotency_key=…)` matches Stripe-style safe retries.
- **Pagination:** `list_*` returns **cursor + page** objects, not unbounded arrays.
- **Structured errors:** typed exceptions (`TaskNotFound`, `TenantMismatch`, `ValidatorFailed`, `BudgetExceeded`, `HumanGatePending`) with **machine-readable `code`** fields.
- **Events, not only polling:** `stream_task_events` / callbacks for UIs and workers; payloads are **versioned** and **enumerated** (see §10.3). Clients ignore unknown event kinds forward-compatibly.
- **Dry-run and CI:** structural validation without LLM spend (pattern from `terraform plan`, static analysis).

**A. Global runtime & lifecycle**

| Method | Purpose |
|--------|---------|
| `configure` / `init` | One-time or idempotent setup: credentials, default `company_id`, paths, log level, **offline** flag. |
| `reconfigure` | Patch config without dropping loaded personas (keys rotated, model endpoint changed). |
| `shutdown` / `close` | Flush writers, close SQLite pools, stop background embed workers—**required** for clean embed in servers. |
| `version` / `capabilities` | Library semver, supported schema versions, optional features (vectors, Playwright). |

**B. Persona factory (YAML → runnable object)**

| Method | Purpose |
|--------|---------|
| `load_persona` | Load **one** persona YAML (or bundle path); validate; return a **`PersonaHandle`**. |
| `load_persona_bundle` | Load **directory** of personas + shared prompts/schemas (monorepo layout). |
| `reload_persona` | Hot-reload YAML in **dev**; production often returns “load new version under new id”. |
| `unload_persona` | Free graph + caches for a handle. |
| `list_loaded_personas` | What is currently in memory on this process. |
| `describe_persona` | Metadata: task types, tool caps, memory paths, **pinned** YAML hash. |
| `validate_persona_yaml` | **CI / pre-commit**: schema + catalog resolution **without** LLM calls. |
| `list_task_types` | Task ids a persona can run. |
| `get_task_input_schema` / `get_task_output_schema` | JSON Schema for host UIs and API gateways. |
| `Squad(...)` constructor | Conventional kwargs (`specialists`, `assignments`, `order`, `memory`, `verbose`, `stream`, …); lists are **materialised for one persona** from YAML, not arbitrary unrelated teams. |
| `SquadBase` + `@specialist` / `@assignment` / `@squad` + `@before_launch` / `@after_launch` | Decorator workflow; collectors resolve to **one** persona’s specialists/assignments—no multi-unrelated-team authoring in one class. |
| `Pipeline` + `@entry` + `@follows` + `state` + `launch()` + `blueprint()` | Pipeline-style outer API; internally may delegate to the persona **Squad** for the heavy step loop. |

**C. Task execution (jobs)**

| Method | Purpose |
|--------|---------|
| `Squad.launch` / `launch` | Blocking happy path until terminal state or first `awaiting_human` (primary entry). |
| `Squad.alaunch` / `alaunch` | Native async twin. |
| `launch_each` / `alaunch_each` / `launch_async` / `launch_each_async` | Batch and threaded-async variants; inputs carry **`task_type`** per item when needed. |
| `execute_task` (optional alias) | Thin wrapper around **`launch`** for older call sites. |
| `submit_task` | Returns **`task_id` immediately** (worker/HTTP handler pattern). |
| `wait_for_task` | Join on `task_id` with timeout. |
| `get_task` / `list_tasks` | Inspect runs: filters by status, persona, task type, time, **`company_id`**, cursor pagination. |
| `cancel_task` | Cooperative cancel; checkpoints stop advancing. |
| `pause_task` / `resume_task` | Long-running ops / maintenance windows. |
| `stream_task_events` | Async iterator of **typed, versioned events**; schema and reserved `event` kinds in §10.3. |

**D. Human gates & collaboration**

| Method | Purpose |
|--------|---------|
| `approve_gate` / `reject_gate` | Unblock `awaiting_human` with audit note. |
| `submit_gate_context` | Attach files / comments **before** approve (review UI). |
| `list_pending_gates` | Ops dashboard: all tasks waiting on humans for a tenant. |

**E. Follow-ups & scope control**

| Method | Purpose |
|--------|---------|
| `enqueue_followup` | Inject CI comment, ticket, user message—merged under **rules**, never silent scope widen. |
| `list_followups` / `merge_followups_now` | Inspect + force-merge for admin tools. |

**F. Step- and attempt-level control (support / escalation)**

| Method | Purpose |
|--------|---------|
| `get_run_timeline` | Ordered stages/steps with statuses and timestamps. |
| `get_step_detail` | Architecture / Implementer / Reviewer outputs + validator rows + **redacted** tool traces. |
| `list_step_attempts` | Every retry for debugging “why stuck”. |
| `retry_step` | Operator or policy-driven retry from a clean checkpoint. |
| `skip_step` | **Dangerous**—policy-gated escape hatch for broken templates in prod. |

**G. Memory & learning**

| Method | Purpose |
|--------|---------|
| `memory.search` | Hybrid FTS + optional vectors; **always tenant-scoped**. |
| `memory.get_capsule` / `memory.list_capsules` | Audit past lessons. |
| `memory.propose_promotion` | Draft LTM / memory-bank patch; **human or policy** commits. |
| `memory.ingest_bank_file` | Re-index curated Markdown after git pull. |
| `memory.delete_capsule` | GDPR / retention—policy-gated. |
| `memory.refresh_embeddings` | Admin: rebuild vector index after model change. |

**H. Tools & validators (plugins)**

| Method | Purpose |
|--------|---------|
| `tools.register` / `tools.unregister` / `tools.list` / `tools.get_schema` | Plugin surface; **dry-run** validation of args. |
| `validators.register` / `validators.unregister` / `validators.list` | Same for checks. |
| `validators.run` | Run one validator **outside** a task (CI repro). |

**I. Replay, export, compliance**

| Method | Purpose |
|--------|---------|
| `replay.export_bundle` | Redacted bundle: pinned YAML hash, schemas, episodic slice—**for support / regulator**. |
| `replay.import_bundle` | Load fixture into hermetic test. |
| `replay.diff_runs` | “What changed between run A and B?” for postmortems. |

**J. Sessions (explicit `RunSession` for power users)**

| Method | Purpose |
|--------|---------|
| `RunSession.create` | Bind `company_id`, `workspace_id`, persona handle, budgets, callbacks. |
| `session.launch` / `session.submit_task` | Same as global but **defaults** scoped to session. |
| `session.attach_context` | Inject request-scoped metadata (`trace_id`, HTTP user) into logs. |
| `RunDriver.attach(task_id)` / `RunDriver.from_submit` | Bind to an in-flight or completed run for **cancel**, **`stream_task_events` cursor**, and status without holding a **`Squad`** factory (see §10.3). |

**K. Tenancy & data lifecycle**

| Method | Purpose |
|--------|---------|
| `tenants.create_profile` / `tenants.delete_all_data` | Onboarding + **right to erasure** (operator tools). |
| `tenants.open` | Context manager / handle that **forces** `company_id` on every inner call. |

**L. Metering & cost**

| Method | Purpose |
|--------|---------|
| `usage.for_task` / `usage.for_tenant` / `usage.for_persona` | Tokens, USD estimates, wall time—**for billing dashboards**. |

**M. Observability & health**

| Method | Purpose |
|--------|---------|
| `logging.configure_structlog` | JSON logs with `trace_id`, `task_id`, `company_id`. |
| `health.check` / `health.check_llm` / `health.check_disk` | K8s probes + preflight before accepting traffic. |

**N. Hooks & middleware (framework-style extensibility)**

| Method | Purpose |
|--------|---------|
| `hooks.on_task_event` / `hooks.on_tool_call` / `hooks.on_validator_result` | Decorators or async subscribers—**Arize / LangSmith-style** tracing integration without forking core. |
| `middleware.register` | Pre/post around LLM or tool calls (rate limit, PII scrub). |
| `middleware.on_role_message` | Optional chain at **Architecture → Implementer → Reviewer** boundaries: inspect / redact / drop **declared** role payloads before the next role sees them (does not weaken the “no merged private transcript” invariant for the Reviewer). |

**O. Graph / engine introspection (debug & tests only)**

| Method | Purpose |
|--------|---------|
| `engine.compile_plan` | Materialise YAML → internal plan **without** execution (unit tests). |
| `engine.dry_run_task` | Validate gates and tool allowlists; **optional** zero-token smoke. |

**P. Schema & migrations**

| Method | Purpose |
|--------|---------|
| `schema.migrate_sqlite` / `schema.current_version` | Ship DB migrations with the wheel—**avoid hand-edited SQLite**. |

**Q. Batching & throughput**

| Method | Purpose |
|--------|---------|
| `submit_tasks_batch` | Many tasks with **global concurrency cap** and **fair share per `company_id`**. |

**R. CLI parity (optional package extra)**

| Commands mirroring methods | `persona validate`, `persona run`, `persona status`, `persona approve`, `persona memory search`, `persona replay export` — same code paths as the library API. |

**Stability note:** ship **A + C (`launch` / `alaunch` / `submit_task` / `wait`) + B (`load` / `validate`) + H (register)** first, with **default `StopRule` wiring** and **`stream_task_events` v1** (§10.3) so caps and observability are real—not stubbed; add **F, G export, N** as soon as you have real customers; keep **skip_step** and **delete** behind **`operator_mode`** flags.

Internal representation: YAML materializes to an ordered list of **steps** (degenerate DAG) sharing the same checkpoint / progress model as future parallel work.

### 10.3 Stop rules, structured events, run handles, message middleware

**Composable stop rules**  
Termination is not only narrative in §11: expose a small **composable** API (names indicative) so hosts can assemble policies without forking core.

| Type / helper | Role |
|---------------|------|
| **`StopRule`** | Abstract rule evaluated at policy-defined ticks (at least **step boundaries** and **validator batches**). |
| **`TokenBudgetRule`**, **`WallClockRule`**, **`MaxStepAttemptsRule`**, **`MaxLaunchTurnsRule`** | Map directly to token/USD, wall time, per-step retries, and whole-run turn limits. |
| **`HumanPendingRule`** | Treats **`awaiting_human`** as a hard pause until gate resolution or timeout. |
| **`ExternalCancelRule`** | Cooperative cancel wired to **`cancel_task`** / cancellation tokens. |
| **`StopRule.all_of(...)`**, **`StopRule.any_of(...)`** | Compose rules (e.g. “stop if **any** budget trips **or** external cancel”). |

Default rules come from **persona YAML** and **`Squad(...)`** kwargs; **`RunSession`** may apply **stricter overlays** for a worker or tenant.

**Structured event stream (`stream_task_events`)**  
Each yielded value is an envelope, not a raw string:

- **`event_schema_version`** (semver of the envelope shape)  
- **`event`** (string kind)  
- **`task_id`**, **`run_id`** (if distinct), **`stage_id`**, **`step_id`**, **`company_id`**, **`ts`**, **`payload`** (typed dict per kind)

**Reserved `event` kinds** (extend in minor versions; consumers must ignore unknown kinds):

`run_started`, `run_finished`, `stage_entered`, `stage_left`, `step_started`, `step_finished`, `role_started`, `role_finished`, `llm_chunk` (optional when streaming is on), `tool_call_started`, `tool_call_finished`, `validator_started`, `validator_finished`, `review_verdict`, `human_gate_opened`, `human_gate_closed`, `memory_citation_injected`, `capsule_written`, `followup_queued`

For **`role_started` / `role_finished`**, **`payload`** includes **`role`** ∈ `architecture` | `implementer` | `reviewer`.

**Run handle vs squad report**  
- **`SquadReport`**: primary return value of **`launch` / `alaunch`**—aggregate status, token usage, top-level text/JSON, and **summaries** per assignment.  
- **`RunDriver`** (optional, advanced): narrow handle bound to **`task_id`** for **cancellation**, **event cursor resume**, and worker-style polling without rebuilding a **`Squad`**.  
- **`AssignmentOutcome`**: per-assignment structured result inside the run (for UI drill-down and tests).

**Message middleware**  
In addition to **§10.2 N** LLM/tool middleware, **`middleware.on_role_message`** runs only on **declared** payloads at handoff boundaries between the three roles inside a step. It may **redact or drop** a message before the next role consumes it; it must **not** reintroduce hidden chain-of-thought into the Reviewer path.

---

## 11. Reliability & quality gates

Loops have ceilings; money has ceilings; time has ceilings; retries must **actually fix something**; surprise messages cannot rewrite the contract in secret.

- **Stop-rule evaluation:** the active **`StopRule`** set (§10.3) is evaluated on each policy tick; **all** rules that must hold for continuation must pass—composition is how token, wall-clock, retry, human-pending, and cancel policies stay aligned.
- **Hard caps:** retries per step, wall clock, token/USD budgets per task and **per tenant** (each backed by a **`StopRule`** or equivalent default).
- **Progress detector:** retries require changed hashes, validator deltas, or approved evidence—not whitespace churn.
- **Plan / YAML changes:** version bump + audit note; never silently rewrite completed steps.
- **Follow-ups:** queue merged into plans under **rules** (no silent tool widening).
- **Hermetic CI:** fake or recorded LLM backend; **no network** in unit tests; **cross-tenant negative tests** required.

Condensed token budgeting and model-tier routing follow the same principles as the project’s token guidance: measure per step, cap tool output, load memory bank once per step group, escalate on evidence.

---

## 12. Tech stack (April 2026 — patterns)

Pick **one main language** for the first shippable core, keep data **local and simple**, and **pin versions** in your own repo—the table is guidance, not magic constants.

Pin **versions in your repo**; treat the table as **defaults to verify**, not immutable law.

| Layer | Recommendation |
|-------|------------------|
| Runtime language | **Python 3.13+** for first shippable library (ecosystem depth); TS may mirror **schemas** later. |
| Packaging | **uv**, semver, lockfile; wheel/sdist distribution. |
| Orchestration | **LangGraph** (or equivalent) **behind adapter**; SqliteSaver / AsyncSqliteSaver per tenant policy. |
| Schemas | **Pydantic v2** strict / JSON Schema for tool and step outputs. |
| DB | **SQLite 3.47+** WAL; optional **sqlite-vec** for vectors on disk. |
| Retrieval | **FTS5 first**; hybrid with embeddings when cost/quality tradeoff warrants. |
| HTTP / CLI | **httpx**, **Typer** + structured logging (e.g. structlog). |
| Quality | **Ruff**, **Pyright** (or mypy strict), **pytest** + **pytest-asyncio**; offline mode env flag. |
| Embeddings | Local (**nomic**, **bge**, …) or hosted—**separate cost meter** from chat. |
| Chat models | Pin `model_id` per role in **persona YAML**; re-evaluate providers monthly. |

---

## 13. Incremental delivery

Ship a **thin vertical slice** first—one persona, one YAML, full safety story—then add smarter search, then add more personas and optional branching plans.

**Phase A — Shippable vertical slice**

- Facade + LangGraph adapter only.
- Tenant-scoped SQLite + leak tests.
- One **persona YAML** + one **task type** + **Architecture → Implementer → validators → Reviewer** loop per step + episodic + retrospective write/read + replay export + human gate callback + **offline tests**.
- Default **`StopRule`** wiring (§10.3) aligned with §11 caps, plus **`stream_task_events`** with **`event_schema_version`** and the **v1 reserved kinds** subset.

**Phase B — Smarter retrieval**

- Optional vectors, async embed jobs, hybrid ranking, mistake clustering.

**Phase C — Breadth**

- More personas and templates; DAG-first templates on same todo engine; promotion workflows for playbooks.

---

## 14. Failure modes (quick reference)

When something ugly happens in production, these are the agreed directions:

| Risk | Mitigation |
|------|------------|
| Validator missing / wrong id | Mandatory catalog; CI resolves all YAML ids. |
| Cross-tenant leak | Physical DB per tenant default; auth-bound `companyId`; property tests. |
| Bad “learning” | Promotion gates; redaction; no auto-LTM from failed runs. |
| Cost runaway | Per-step and per-tenant caps; trim context before cheaper models. |
| Framework lock-in | Public façade; graph types only in adapter. |
| YAML / shell drift | Validators by id only; single implementation per id. |

---

## 15. Where to go next

What you have here is the **single contract**: what the library guarantees (step loop, memory, tenancy, validators) and how the pieces fit. Longer worked examples, YAML samples, package layout sketches, token math tables, and extended failure notes sit in the project’s companion materials whenever you need copy-paste or extra rationale beyond what is spelled out above.

---

_Document version: 1.8 — Adds §10.3 composable `StopRule`s, versioned `stream_task_events` kinds, `RunDriver` / `AssignmentOutcome`, message-path middleware, and clarified non-goals (handoff, distributed runtime, multimodal bus)._
