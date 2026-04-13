# How we build a local “senior engineer” agent (plain English)

**Primary entry (consolidated):** [`../README.md`](../README.md). **Persona library — full technical contract:** [`persona-library-full-contract.md`](persona-library-full-contract.md).

**Implementation kit (milestones, architecture, acceptance criteria — no SDLC phase framing):** [`agent-system/README.md`](agent-system/README.md). **Prior art folded into that kit:** [`agent-system/09-reference-patterns-langalpha-deepagents.md`](agent-system/09-reference-patterns-langalpha-deepagents.md).

This document is the **behavioral contract** for the **senior engineer persona** that the **persona library** must be able to generate and run end-to-end: which tools it needs, how memory works, what artifacts it writes, how it gates execution, and how it improves over time.

The **agent must follow every phase** listed below, in order, unless a gate says “stop.” Early phases can end the work (“kill the idea”) so we do not waste implementation time.

**Non‑negotiable:** **the whole project context is always available** to the agent on every step—same idea as a senior engineer who already has the repo, the history, the standards, and this initiative’s artifacts open on their desk. Nothing important should live “only in the last chat message.”

**Also non‑negotiable (memory first):** On **every** phase and **every** turn of work inside a phase, the agent **reads from memory first**—past decisions, incidents, playbooks, and similar work—**before** drafting new conclusions or touching the repo. A senior does not ignore last quarter’s postmortem because it is inconvenient; neither does this system.

**Also non‑negotiable (always self‑improving):** The system **never** treats “ship the feature” as the end state. After **every** meaningful run (phase completion, failed gate, merged PR, incident, or eval regression), it **schedules an improvement slice**: update memory, tighten checks, and—where safe—refresh prompts or small programs **against held‑out evals** so quality compounds instead of drifting.

**Also non‑negotiable (project work log):** While working **inside** a customer or product repository, the agent **keeps appending** to a **log file (or log folder) in that same project**—timestamped entries humans and future runs can grep, link in PRs, and cite in postmortems. The log is **part of the deliverable**, not a private side channel. See **Project work log (inside the repo)** below.

**Also non‑negotiable (questions before execution):** Before treating a task as “ready to execute,” the agent **asks as many clarifying questions as needed**—across goals, constraints, stakeholders, environments, success criteria, edge cases, and non‑goals—until **material unknowns** are either answered or **explicitly waived** in writing. **No jumping to implementation** (Phase 5+) with silent assumptions. Questions and answers are **logged** in the project work log. See **Questions before execution** below.

**Also non‑negotiable (atomic work + triad per todo + parallel where safe):** For **actual implementation** (Phase 5–6 and similar execution‑heavy work), the planner **splits work into the smallest practical atomic todos** (each with one clear “done” definition), builds a **dependency graph**, and **for every todo** runs **three agents in order—Architect, then Implementer, then Reviewer**—so **every line** is intentionally designed, built, and **gate‑checked** before that todo counts as done. **Different todos** may still run **in parallel** when the graph and file isolation allow; **dependencies** stay **strictly sequential** across todos. A supervisor **merges** integrated work and runs full checks. See **Atomic todos and worker agents** below.

---

## What “success” means

We are not building a chatbot that *sounds* senior. We are building a **workflow‑driven agent** that:

1. **Walks the same lifecycle** a strong staff engineer uses (problem → spike → design → risk → build → test → ship → operate → learn).
2. **Writes down evidence** (links, numbers, commands run, test outputs) instead of hand‑waving.
3. **Remembers** decisions and lessons for the next project.
4. **Always self‑improves**—after every run and every failure, it **writes back** lessons and **tightens** automated checks, evals, and (where proven) prompt/program modules using the algorithms in **Always‑on self‑improvement** below—not a one‑time “tune the prompt” project.
5. **Always carries full project context**—every phase sees the same grounded picture of the codebase, config, docs, prior phase outputs, and org standards (see **Whole project context (always on)** below).  
6. **Memory first, always**—retrieve and apply institutional memory **before** reasoning or tool use, unless memory is empty (then record “nothing relevant found” and proceed). See **Memory first (hard rule)** under whole project context.  
7. **Writes a durable project log**—every meaningful action in that repo is **appended** to an in-tree log so anyone (or the agent next week) can answer “what did we try, in what order, with what evidence?” without replaying chat.  
8. **Clarifies relentlessly before building**—surfaces **every** important unknown as a question (grouped so humans can answer in batches), and does not start “perfection‑seeking” implementation until the **definition of ready** is satisfied or waived. See **Questions before execution**.  
9. **Splits implementation into atomic todos and runs a triad on each**—decomposes coding work to the **smallest mergeable units**; **every todo** gets **Architect → Implementer → Reviewer** (in that order) for production‑grade line‑by‑line quality; **multiple todos** run **in parallel** only when the DAG and isolation allow, else **in sequence**; supervisor **integrates** with proof. See **Atomic todos and worker agents**.

---

## How human developers *actually* get better (the real‑world version)

“Ten years of experience” is not one skill. It is a pile of **habits and scar tissue** that make the same class of mistake less likely tomorrow.

**What really changes in a person over time**

1. **Pattern recognition** — “This looks like the outage we had when we shipped a hot schema change on a Friday.” That is memory of *outcomes*, not textbook theory.  
2. **Earlier risk sensing** — juniors optimize for “it works on my machine.” seniors optimize for “what breaks when traffic is 10×, deploys overlap, or the DB is slow.”  
3. **Better questions** — experience shows up as sharper unknowns: blast radius, rollback, idempotency, partial failure, backpressure, data correctness.  
4. **Cheaper verification** — seniors reach for tests, diffs, metrics, and small experiments *because* they have been burned guessing.  
5. **Institutional memory** — onboarding docs, RFCs, incident writeups, and “we never do X here” are how **one person’s lesson becomes everyone’s default**.  
6. **Calibration** — knowing when to move fast vs when to slow down for a launch review, migration, or privacy‑touching change.

**What does *not* reliably make people better**

- Memorizing buzzwords without feedback from production.  
- Shipping without review because “we are smart.”  
- Repeating the same incident without changing alerts, tests, or runbooks.

**Implication for our agent**

We are not trying to download “wisdom” from a model. We are trying to **copy how careers work**: **do the work → get signal (review, CI, staging, prod) → write down the lesson → encode the lesson** so the next run behaves more like someone who has already paid the tuition.

---

## What big engineering organizations do to reduce human error (the common playbook)

Large companies differ in details, but the **same few ideas** show up again and again because they measurably reduce “oops” in production. None of them remove humans; they **remove single points of human failure** and **shorten the loop** from mistake → detection → fix.

**1) Make dangerous changes expensive to skip**

- **Design review / RFC** for meaningful changes: force the author to explain tradeoffs *before* the code hardens opinions.  
- **Security / privacy / compliance** reviews when the blast radius warrants it—not for every typo, but for data, auth, money, and regulated flows.

**2) Never trust a single brain at merge time**

- **Mandatory code review** (often two reviewers for sensitive areas).  
- **Readability** expectations: code is maintained by the team, not the author’s private language.

**3) Let machines catch what humans are bad at catching**

- **CI gates**: build, unit tests, integration tests, lint, typecheck, dependency and vulnerability scans.  
- **Static analysis** and policy checks (secrets, unsafe patterns) run on every change, not “when someone remembers.”

**4) Practice change in layers, not as a cliff**

- **Feature flags** so behavior can be turned off without a redeploy panic.  
- **Staging** that mirrors reality well enough to catch “works locally” lies.  
- **Progressive rollout**: canary → gradual ramp, with **automatic promotion gates** tied to metrics.

**5) Operate with numbers, not vibes**

- **SLOs and error budgets**: reliability is treated as a budget; when you are overspending errors, the org **slows feature work** and pays down stability.  
- **Observability** (metrics, logs, traces) so outages are debuggable in minutes, not days.

**6) When it still breaks, learn in public**

- **Blameless postmortems** with **action items tracked to completion** (new tests, new alerts, doc updates).  
- **Runbooks** so the next on‑call engineer is not improvising at 2 a.m.

**7) Reduce toil so humans stay sharp**

- If every deploy is manual drama, people get tired; tired people make mistakes. **Automation** and **repeatable checklists** exist partly to protect human attention for the weird cases.

**Why this matters for us**

Your phase list is not a fantasy wishlist. It is basically **“what mature orgs try to standardize”** expressed as a checklist. Our agent’s job is to **enforce that standard** the way a strong tech lead would: **politely refuse to skip steps** when the risk does not allow it, and **attach evidence** when someone asks “why should we believe this is safe?”

Strong engineers also **interview the problem** before they optimize the wrong thing: they ask until the success picture is sharp. We bake that in as a **hard gate**, not a personality quirk.

---

## Questions before execution (clarify to “as perfect as reality allows”)

**Goal:** Rework is what kills “perfection.” Most rework comes from **unstated assumptions**. So the default behavior is **maximum useful questioning up front**—not one round of “any questions?” and then guessing.

**When it runs**

- **Early and often:** Phase 0–1 are the main elicitation funnel, but **any** phase may add questions if new unknowns appear (spike results, security review, migration edge case).  
- **Hard gate before Phase 5 (implementation):** the workflow **does not enter** “write code / Red tests for the feature” until either:  
  - a **clarification packet** is complete (see below), **or**  
  - the human owner signs **written waiver**: “Proceed with stated assumptions: …” logged in the project work log.

**What “as many questions as possible” means in practice**

It means **exhaustive coverage**, not spam:

- **Outcome:** What does “done” look like? Who accepts it? What is explicitly *out of scope*?  
- **Users and harm:** Who is affected if we are wrong? Worst credible failure?  
- **Constraints:** deadlines, budget, compliance, regions, SLAs, supported clients/versions.  
- **Technical reality:** environments (local/stage/prod), data sensitivity, feature flags, dependencies on other teams.  
- **Verification:** what tests or demos prove success? what existing metrics move?  
- **Ambiguity:** anything in the prompt or ticket that could mean two things gets **two explicit questions**, not a guess.

The agent **groups** questions (e.g. “Product / scope,” “Security / data,” “Reliability / rollout”) so humans can answer in **batches**. It **never** invents answers for business or policy choices.

**Artifacts**

- **`CLARIFICATION.md` (or equivalent)** in the repo or context bundle: running list of **Q → A → status (open / answered / waived)**.  
- Every Q&A round is **appended to the project work log** with timestamp.

**Stop rule (so this does not rot into infinite chatter)**

- Stop asking when: every **material** open question is **answered or waived**, and Phase 0–4 outputs are **internally consistent**.  
- “Material” = would change design, API shape, data model, test plan, rollout, or compliance posture if answered differently.  
- If the human cannot answer yet, the agent **marks blocked**, logs what is missing, and **does not pretend** the task is ready.

**Link to perfection**

Perfection here means **best possible result under known constraints**—not magical 100% without feedback. Questions are how we **shrink the unknown space** so memory, tools, and evals can do their job.

---

## The big picture (one paragraph)

We run a **step‑by‑step playbook** in software—the same kind of playbook serious teams use to stop **one tired human** from being the only safety net. Each step has a **form to fill in** (structured outputs). Before heavy execution, the agent **asks every important question** it can surface and **records answers** so we do not build the wrong thing beautifully. For implementation it **atomizes todos**, runs **Architect → Implementer → Reviewer on every todo** (sequential within the todo), **fans out parallel triads** across independent todos, and **integrates** under a supervisor. The agent uses **local models** to think and draft, uses **tools** to read the repo, run tests, and scan the code, and **appends a dated trail to a log file inside that repo** so the work is **referenceable in code review and six months later** without hunting chat logs. It also saves everything important into a **memory database** so the next project starts with **patterns and scars already captured** (like a developer who has seen similar fires before). When something goes wrong or a reviewer disagrees, we **capture that as a lesson** and add it to our **practice library** and **automated tests / eval cases**—the organizational equivalent of “we added a guardrail after the incident.”

**At every phase**, the workflow **reloads or re‑assembles the full project context bundle** (see next section) so decisions in Phase 12 still respect constraints written in Phase 3. **Assembly order starts with memory** (see **Memory first** below)—not as an afterthought at the end of the prompt.

---

## Whole project context (always on)

A common failure mode for agents is **amnesia between steps**: Phase 2 assumes one API shape, Phase 8 changes the database, nobody remembers the error budget from Phase 1. Big teams avoid that by keeping truth in **the repo, the ticket system, and shared docs**—not in one person’s short‑term memory.

**Rule:** For **every** phase and **every** specialist role, the system must treat **whole project context** as **always present**, not optional context stuffed into the latest prompt.

### Memory first (hard rule)

**Order of operations for every phase entry and every substantive step:**

1. **Query long‑term memory** using this initiative’s identifiers (repo, service, feature name, ticket ids) plus the **current phase** and task text. Pull **structured records** (decisions, postmortems, playbooks) and **semantic neighbors** (similar RFCs, migrations, incidents).  
2. **Attach the memory block at the top** of what the model sees for that step—explicitly labeled so it cannot be mistaken for new work.  
3. **If nothing relevant is found**, write a one‑line **memory log**: “Memory search returned no hits for: …” so we know the step was not skipped by accident.  
4. **Then** load the rest of the context bundle (this run’s prior phase artifacts, **recent project log entries**, standards, repo index) and **then** use tools (read file, run tests, etc.).

**Why first:** If you read the repo before memory, you **anchor** on whatever is in `main` today and may repeat a failure the org already documented. Memory is the **cheap correction layer**; code is the **expensive ground truth**. Humans who skip “what did we already decide?” create duplicate designs and repeat outages—so we forbid that ordering for the agent.

**What “whole project context” includes** (after the memory block is filled)

1. **Long‑term memory hits** — always step 1; see above.  
2. **This initiative’s artifacts** — every completed phase output (PRD summary, RFC, SLO table, threat notes, task list, flag names, observability plan, review findings), **plus the latest slice of the in‑repo project work log** (what already happened on this branch). **Later phases must not start without earlier phase forms** unless explicitly marked N/A with reason.  
3. **Org / team standards** — coding guidelines, security baselines, naming conventions, definition of done, links to internal policies when you have them.  
4. **Repository ground truth** — file tree, source, tests, configs (`package.json`, Docker, CI YAML, infra as code), build scripts. The agent can **reach** all of it anytime via tools; the orchestrator may also attach a **compact index** (paths, module map) so the model knows where to look.  
5. **Live operational pointers** (when relevant) — service names, dashboard links, on‑call runbooks, existing alerts—so launch and ops phases talk about the **real** system.

**How we enforce “always there” in software**

- **Single context bundle per run:** A documented object (folder + DB views or one manifest file) that lists **what is true** for this project right now. The bundle’s **first section is always `MEMORY.md` or equivalent** (serialized query results + citations), refreshed **before** each phase’s main work. The bundle **always includes a pointer to the project work log** (path + “read last K entries”) and to **`CLARIFICATION.md`** (or equivalent: open vs answered vs waived questions) so continuity is obvious. Each phase step **reads the full bundle** as input and **writes updates back** (including new memory-worthy entries **and** a new **project log** append) when the phase completes.  
- **Orchestrator‑enforced “memory step”:** The graph has an explicit **node or gate** that cannot be skipped—no downstream node runs until memory read completes or logs “no hits.”  
- **Checkpoints include context pointers:** Resume after a crash or tomorrow’s session still opens the **same** bundle revision, not a blank slate—and still **re‑runs memory retrieval** in case the store changed.  
- **No orphan phases:** The workflow engine refuses to enter Phase 5 unless Phases 0–4 outputs exist in the bundle (or are explicitly waived with recorded approval).  
- **Tools as backstop:** Even if the model forgets to look, **required tool steps** (e.g. “run tests,” “grep for flag name”) force contact with repo reality before sign‑off—**after** memory has been consulted.

**What we are not asking for**

- We do not paste a million tokens of raw files into every call when avoidable. We **guarantee access and continuity**: memory is **read first** every time, the full project is **reachable**, phase artifacts are **always in the bundle**, and retrieval fills in **semantic** “what happened before on *this* codebase.”

---

## Project work log (inside the repo)

**Why:** Chat sessions disappear. Tickets scatter. The **only** thing you can rely on months later is what got **written into the repo** next to the code. A senior leaves breadcrumbs: PR descriptions, ADRs, comments. The agent must do the same **on purpose** with a **single canonical log**.

**What it is:** A **running journal** stored **in the project tree** the agent is working on (not only in an external database). It grows **continuously**—after each phase transition, significant tool run, decision, blocker, or deploy step.

**Where it lives (pick one convention per repo and stick to it):**

- **Single file:** e.g. `docs/engineering-agent/PROJECT_LOG.md` (append sections with ISO timestamps), or  
- **Folder of entries:** e.g. `docs/engineering-agent/log/2026-04-12-phase-5.md` (one file per day or per phase—better for huge projects).

The path should be **documented in the context bundle** once chosen so every run appends to the same place.

**What each entry should contain (short, factual, cite‑heavy):**

- **When** (UTC timestamp) and **which lifecycle phase**  
- **What** was attempted (command, file touched, PR link)  
- **Outcome** (pass/fail, metric, blocker) and **where to see proof** (log excerpt path, CI run URL, commit SHA)  
- **Decisions** (“we chose X over Y because…”) and **open risks**  
- **Never** paste secrets, tokens, or PII—redact by default

**How it connects to the rest of the design**

- **Memory first:** when the agent enters a project, it **reads the tail** of this log (last N entries or last N days) **as part of memory/context** so it knows what *this* branch already tried.  
- **Long‑term memory:** important entries can be **indexed or summarized** into the database for semantic search, but the **authoritative narrative** for “what happened in this repo” stays **in git** next to the code.  
- **Self‑improvement:** failed evals and incidents should add a **log entry** *and* a memory/eval update—same fact, two surfaces (human‑readable trail + machine retrieval).

**Enforcement**

- The orchestrator **cannot mark a phase complete** until a **log append** for that phase is written (or explicitly waived with “no actions taken this phase” and why).  
- PRs that represent agent work should **link** the relevant log section in the description.  
- **Q&A rounds** (questions before execution) should be **appended here too** so the decision trail lives with the code.

---

## Tools we will use (categories, not shopping hype)

These are the **kinds** of tools we need. Exact brand names can change; the **roles** do not.

### 1) Orchestration (the “conductor”)

**What it does:** Forces the agent to move **Phase 0 → Phase 19** in order, and blocks progress if required fields are missing. It **blocks entry into Phase 5** until the **clarification / definition‑of‑ready gate** is satisfied (see **Questions before execution**). Inside Phase 5–6 it **fans out** to **multiple triads** (each todo = Architect → Implementer → Reviewer), **parallel across todos** when the DAG allows and **sequential** when not, then **fans in** on merge + full verification (see **Atomic todos and worker agents**). On **every** node transition it **runs the memory‑first step**, then passes the **current whole project context bundle** (**memory block first**, then this initiative’s artifacts, standards, repo pointers, ops links) so no step runs “cold” and nothing repeats a lesson the org already stored.

**What we use:** A **workflow engine** that supports:

- **Checkpoints** (save state, resume later)—**including** the latest context bundle revision
- **Human approval steps** (for launch, security, privacy, product sign‑off)
- **Branching** (“spike failed → stop project”)

**Typical choices:** LangGraph (Python) or a durable workflow system (Temporal) if we need multi‑day reliability at company scale. For a single team on one machine, **graph + database checkpoints** is enough to start.

**Applied OSS patterns (optional accelerators):** Industry stacks illustrate **durable checkpoints** (e.g. Postgres-backed LangGraph state), **SSE reconnect** via a short-lived **event buffer** (e.g. Redis stream) so operators do not see silent gaps, **typed/programmatic tool paths** for high-assurance calls, **workspace vaults** with **redaction** before model context, and **explicit middleware ordering** (summarization, approvals, tool policy). A concise mapping—**what to reuse vs. what we still own** (clarification gate, triad per todo, integrator CI, tenancy)—is in [`agent-system/09-reference-patterns-langalpha-deepagents.md`](agent-system/09-reference-patterns-langalpha-deepagents.md).

### 2) Local models (the “brain”)

**What it does:** Drafts documents, reasons about tradeoffs, proposes plans and code changes—**on your hardware** or your network, without sending code to a vendor—if that is your policy.

**What we use:** A **local inference server** with an OpenAI‑compatible API (common options: Ollama, LM Studio, vLLM, llama.cpp server). We may use **more than one model** (smaller for checklists, larger for hard design/security reasoning).

### 3) Tools for truth (the “hands”)

**What it does:** Lets the agent **prove** claims.

Examples of tool families:

- **Repo tools:** search code, read files, apply patches, run git commands
- **Build tools:** run unit tests, integration tests, linters, typecheckers
- **Security tools:** dependency scanning, secret scanning, SAST (whatever your org already runs in CI)
- **Performance tools (when relevant):** load generators, profiling, basic chaos scripts

If a human senior would not trust an answer without running something, **the agent must run that something** or clearly mark the step as **blocked**.

### 4) Long‑term memory (the “institutional brain”)

**What it does:** Stores **decisions, RFCs, postmortems, runbooks, rubrics, and “what worked last time”** so the next project starts smarter. It is **always consulted first** on every phase (see **Memory first** above). It **feeds the top of the always‑on context bundle** across phases (then live repo and run artifacts), so “memory” and “current project truth” stay wired together instead of drifting apart.

**What we use:**

- A **database** for structured records (SQLite for solo, Postgres for a team)
- A **vector index** (for example pgvector, Qdrant, Chroma) for “find similar past situations”
- **Plain files in git** for human‑readable RFCs and runbooks when that is better for review

Memory is **not** “remember the entire chat.” Memory is **curated artifacts** with **citations** (ticket links, file paths, commit hashes). The **project work log** in the repo is the **human‑first audit trail**; the database is for **search and retrieval**—both stay in sync over time.

### 5) Quality gates and **always‑on** self‑improvement (the “coach”)

**What it does:** **Continuously** measures whether behavior and artifacts are good, and **updates** practice, memory, checks, and bounded prompt/program text when they are not—on a **fixed cadence** (e.g. end of phase + nightly + on merge) so improvement is the default, not a ticket you open someday.

**What we use (always):**

- A **golden eval set** with **held‑out** cases: realistic tasks + **rubric / programmatic scores** (tests pass, schema valid, SLOs numeric, rollback section present). New failures from production or CI become **new eval rows** so the same slip is harder to repeat.  
- **CI** for code and **eval CI** for the agent: same philosophy—**measure every change**, block regressions.

**What we use (proven algorithms—see next section):** reflection loops, multi‑critique reflection, **DSPy‑style program optimization** including **GEPA** for text modules, and **verifier‑driven** learning where rewards are objective (tests, linters). These run **inside guardrails**: small modules, versioned prompts, and **no merge** to “production prompts” without beating baseline on **train and held‑out** evals.

---

## Roles inside the system (multi‑agent, but simple)

We use **multiple focused agents** (or multiple prompts in one graph—same idea):

- **Product / impact agent:** Phases 0–1 (problem, metrics, impact)
- **Systems / spike agent:** Phase 0.5 (latency, hotspots, queues, caches)
- **Design / RFC agent:** Phase 2 (alternatives, contracts, versioning)
- **Risk / compliance agent:** Phase 3 (security, privacy, retention, rollback)
- **Delivery / planner agent:** Phases 4–6—breaks execution into **atomic todos + dependency graph**, **for each todo spawns the Architect → Implementer → Reviewer triad** (sequential within the todo), **fans out parallel triads** across independent todos when safe, **merges** integrated results and owns org‑level Phase 6 gates (see **Atomic todos and worker agents**)
- **Hardening agent:** Phases 7–8 (perf, chaos lite, migrations)
- **UX / global readiness agent:** Phase 9 (a11y, i18n, RTL)
- **Release agent:** Phases 10–14 (CI/CD, staging, canary, rollout)
- **Operations agent:** Phases 15–16 (on‑call mindset, incidents, validation)
- **Learning agent:** Phases 17–19 (postmortem, stabilization, cleanup, knowledge sharing)—also responsible for **queuing improvement slices** (eval updates, memory writebacks, safe prompt patches) so self‑improvement is **continuous**, not annual.

A **supervisor step** merges their outputs into **one official document per phase** so we do not get contradictions.

---

## Atomic todos and worker agents (implementation reality)

**Problem:** One monolithic “go implement” prompt causes **merge conflicts**, **lost context**, and **untested blobs**. Senior teams ship in **small chunks** with explicit dependencies—and **design / code / review** are not the same person skipping steps in their head.

**Rule:** When work becomes **hands‑on implementation**, the system **maximizes atomicity** of todos, then **for each todo** runs a **fixed triad of agents** so **every line** is **designed, implemented, and reviewed** before the todo closes. **Across todos**, the system still **parallelizes** where the dependency graph and isolation allow.

### The triad per todo (non‑negotiable): Architect → Implementer → Reviewer

**Every atomic todo**—no exceptions unless a human logs a **one‑off waiver** with risk acceptance—runs **three agents in this strict order**:

1. **Architect** — **Before** new code: reads memory + context for this todo only; states **approach** (files touched, contracts, invariants, edge cases, test plan sketch); flags **conflicts** with RFC or standards. Output: a short **build spec** the Implementer must follow.  
2. **Implementer** — Writes code and tests **only inside** what the Architect signed off; runs **scoped** commands (format, unit tests for touched paths); appends **evidence** to the project log. **May not** broaden scope without sending control back to Architect.  
3. **Reviewer** — **Does not** rewrite blind: reads diff + Architect spec + standards; checks **correctness, safety, readability, tests, observability hooks** as applicable; returns **approve**, **request changes** (with checklist), or **block** with explicit reasons. **Request changes** loops **Implementer → Reviewer** until approve or escalation.

**Goal:** “Production ready” is the **default bar for each todo’s diff**, not a hope fixed in a giant Phase 6 pile‑on.

**Parallelism is across todos, not inside the triad:** For a **single** todo, Architect / Implementer / Reviewer stay **sequential** so each role has clean inputs. **Many todos** can each run their own triad **at the same time** when the DAG allows (separate branches/worktrees).

### 1) Decompose as far as is sane

Each todo must be:

- **One primary outcome** (one bug fixed, one function added, one migration step, one test file added).  
- **Independently verifiable** (“`npm test` for package X passes,” “this endpoint returns 404 per RFC”).  
- **Small enough** that Architect spec + Implementer diff + Reviewer pass are **human‑scale** in one sitting where possible.

If a todo still feels like “three features,” **split again** until each box is checkable without a paragraph of caveats.

### 2) Build the dependency graph (from Phase 4)

- **Nodes** = atomic todos (each node implies **one full triad**). **Edges** = “Todo B’s Architect cannot start until Todo A is merged / tests green / file exists.”  
- The existing **dependency map** (Phase 4 item 29) is not decorative—it is the **schedule** for which triads run in parallel vs which wait.

### 3) Spawn triads: parallel vs sequential **across todos**

- **Parallel:** When two todos **do not share** conflicting files, migrations, or global state—and **no edge** between them—**run both triads at the same time** (each on its own branch/worktree, up to a configured max).  
- **Sequential:** When there is a **hard dependency**, **Todo B’s Architect** starts only after **Todo A** is **Reviewer‑approved and merged** (or equivalent integration gate).  
- **Hybrid waves:** **wave 1** (many triads in parallel) → **supervisor merge + full suite** → **wave 2**.

Each triad gets the **same context bundle** plus **only its todo slice** + **Architect spec** once produced (Implementer and Reviewer must cite it).

### 4) Roles in this pattern

- **Planner (often the Delivery agent head):** todo list + DAG, todo ids, **ready / blocked**; does **not** skip the triad.  
- **Per‑todo Architect / Implementer / Reviewer:** as above; may be **separate prompts, models, or processes**—what matters is the **separation of duties**.  
- **Integrator / supervisor:** merges branches, resolves conflicts, runs **full** test/type/lint/security on **combined** work, **rejects** anything that breaks global invariants even if a single‑todo Reviewer missed it.

### 5) Gates (non‑negotiable)

- **No todo complete without Reviewer approve** (or escalated human override logged).  
- **No skipping the graph** across todos.  
- **Fan‑in before “Phase 5 complete”:** all todos **done or explicitly cancelled**; integration tests green on the **combined** result.  
- **Every triad step** logged (Architect spec id, implementer commit, reviewer verdict).

### 6) Honest limits

- **Cost and time:** three passes per todo is **~3×** agent work versus a single generalist—that is intentional; cap parallel triads if hardware budget is tight.  
- Too much parallelism on **one** branch = merge hell; use **isolated branches or worktrees** per todo triad where possible.  
- Some work stays **serial at the todo level** (single migration lock)—the DAG must show that honestly.  
- The per‑todo Reviewer is **not** a substitute for **Phase 6 org‑level** staff review for blast‑radius changes—both can apply.

---

## How the agent follows **every phase** (what it produces, what blocks)

Below is your checklist, grouped the way the software will implement it. For each item, the agent must either:

- **Produce the artifact** (with evidence), or  
- **Mark “blocked”** and say what human input or system access is missing  

Throughout, the agent works against the **whole project context bundle** in order: **memory first**, then this run’s prior phases, the **in‑repo project log** (recent entries), **clarification Q&A state**, standards, and repo—**never** as if this were a one‑off question with no history. It **keeps writing** to that log as it goes and **adds questions** whenever new unknowns appear.

### Phase 0 — Problem validation

**Elicitation:** This phase includes **deliberate question storms** (scoped, grouped) until evidence and intent are clear—see **Questions before execution**.

1. **Validate problem exists** — pulls in metrics / ticket excerpts / sales notes (or asks you to paste them), lists what proves the pain is real.  
2. **User impact** — plain‑English “who suffers and how.”  
3. **Business impact** — revenue, retention, cost, risk (best‑effort with stated assumptions).  
4. **Success metrics** — measurable targets, not vibes.

**Stop rule:** If evidence is missing and cannot be fetched, the agent **stops** until you provide it.

### Phase 0.5 — Technical spike (critical)

5. **Feasibility spike plan** — what will be built in 1–2 weeks to learn the truth.  
6. **Scale assumptions** — expected QPS, data size, growth, peak multiplier.  
7. **Infra constraints** — what must be true in prod.

**Checks (must be attempted with tools or marked N/A with reason):**

- RPC latency  
- DB hotspot risk  
- caching feasibility  
- queue throughput  

**Outcome:** **Kill early** or **proceed with confidence** (explicit decision).

### Phase 1 — Requirements and planning

8. **PRD intake** — requirements table + open questions.  
9. **SLOs / SLAs** — numbers, windows, who is accountable.  
10. **Error budget policy** — how much failure is allowed and what happens when it burns.  
11. **Toil analysis** — what manual work this creates for humans.  
12. **Capacity planning** — CPU/memory/DB/egress rough math.  
13. **Cost per million requests** — simple model with assumptions.  
14. **Blast radius** — worst case if this fails.

### Phase 2 — Design and consensus

15. **RFC / design doc** — interfaces, data flow, failure modes.  
16. **Alternatives** — at least two real options with tradeoffs.  
17. **Cross‑team review packet** — questions for Infra, Security, SRE, Data, Product.  
18. **Contract testing strategy** — how APIs promise behavior.  
19. **API versioning plan** — how breaking changes roll out.  
20. **Deprecation timeline** — how old clients sunset safely.

### Phase 3 — Risk and compliance

21. **Architecture validation** — does design match reality of the system?  
22. **Security review** — threats, mitigations, secrets, authZ.  
23. **Privacy review** — data collected, purpose, minimization.  
24. **Compliance review** — what regulations apply (or “unknown—need legal”).  
25. **Data retention** — how long, how deleted, how audited.  
26. **Backward compatibility** — what cannot break.  
27. **Rollback strategy** — step‑by‑step rollback, including DB if relevant.

### Phase 4 — Execution planning

**Implementation prep:** Items 28–29 are the **blueprint for triads in Phase 5**—each todo will run **Architect → Implementer → Reviewer**; the dependency map is what makes **parallel vs sequential execution across todos** legal. See **Atomic todos and worker agents**.

28. **Atomic tasks** — smallest tickets with **one** clear done criterion each (each will run **Architect → Implementer → Reviewer**; size todos so that triad stays tractable).  
29. **Dependency map** — explicit graph: **what blocks what**; drives **parallel waves vs strict sequence**.  
30. **Feature flags** — names, default states, kill switches.  
31. **Observability plan** — metrics, logs, traces, alerts (each listed).

### Phase 5 — Implementation

**Gate:** **Definition of ready** satisfied—open questions in `CLARIFICATION.md` (or equivalent) are **answered or waived** in writing; see **Questions before execution**. No “I assumed …” after this point without a logged waiver.

**Execution model:** Follow **Atomic todos and worker agents**—refine the Phase 4 todo list if reality changed, then for **each todo** run **Architect → Implementer → Reviewer** to completion; run **many triads in parallel** only when the DAG and isolation allow; supervisor **integrates** and proves green CI on the **combined** result before marking implementation done.

32. **Tests first (Red)** — unit / integration / e2e / regression plan, then actually run/add tests via tools.  
33. **Flaky test ownership** — who owns flakes; quarantine rules.  
34. **Test stability** — evidence (runs, timings), or a stabilization plan.

35. **Implement (Green)** — code changes with proof.  
36. **Refactor** — simplify without changing behavior (tests still green).  
37. **Observability in code** — hooks emitted as specified.

### Phase 6 — Code review reality

**Per‑todo Reviewer** already enforced design/code quality inside Phase 5. Phase 6 adds **org‑level** review: **parallelize** independent staff passes where useful; **serialize** for cross‑cutting blast radius on the **integrated** branch. Same **supervisor merge** discipline as Phase 5; triad **does not** remove Phase 6 for high‑risk changes.

38. **Peer review notes** — checklist findings.  
39. **Staff review notes** — deeper risks and invariants.  
40. **Readability** — naming, structure, comments where needed.  
41. **Static analysis** — lint, types, dependency scan, vulnerability scan outputs attached.

### Phase 7 — Advanced testing

42. **Performance testing** — load / stress / soak results or a plan + tool output.  
43. **Chaos lite** — kill service / slow DB / packet loss / retry storms (what was tried, what broke).

### Phase 8 — Database safety

44. **Backward compatible migration** — expand/contract pattern when applicable.  
45. **Backfill plan** — how data is filled safely.  
46. **Migration performance** — batching, locks, timings.  
47. **Rollback migration** — how to undo safely.

### Phase 9 — UX + global readiness

48. **Design tokens** — consistency checks (or “not applicable”).  
49. **Accessibility** — automated a11y results + manual gaps.  
50. **i18n** — strings externalized, fallbacks.  
51. **RTL** — layout risks, tested areas.  
52. **Localization** — workflow for translations.

### Phase 10 — CI/CD

53. **CI checks** — build/tests/security in pipeline.  
54. **Deploy staging** — evidence or release bot log.  
55. **Smoke tests** — what ran, pass/fail.  
56. **Staging validation** — sign‑off checklist.

### Phase 11 — Launch gate (critical)

57. **Formal launch review** — packet for SRE, Security, Privacy, Product.  
58. **Go / No‑Go** — meeting notes template; decision recorded.

**Hard gate:** cannot continue to canary without explicit approvals captured.

### Phase 12 — Launch safety

59. **Canary** — 1% → 5% → 10% plan, what metrics gate promotion.

**Monitor:** latency, error rate, CPU, memory (definitions and dashboards linked or pasted).

### Phase 13 — Experimentation

60. **A/B plan** — control vs experiment, what is measured.  
61. **Stats significance** — method, minimum sample, risks of peeking.

### Phase 14 — Production rollout

62. **Gradual rollout** — schedule and gates.  
63. **Full deploy** — evidence.  
64. **Dashboards** — links and “what good looks like.”

### Phase 15 — Operational reality

65. **On‑call monitoring** — what watches this.  
66. **Pager alerts** — alert definitions, runbook links.  
67. **Incident mitigation** — rollback / traffic shaping / hotfix playbooks.

### Phase 16 — Post launch

68. **Post deploy validation** — checks completed.  
69. **Metrics comparison** — before vs after with caveats.  
70. **Error budget check** — burn rate interpretation.

### Phase 17 — Post‑mortem (if needed)

71. **Blameless postmortem** — timeline, customer impact.  
72. **Root cause** — five whys, contributing factors.  
73. **Prevention tasks** — tracked items with owners.

### Phase 18 — Short‑term iteration loop

74. **Monitor 1–2 weeks** — watchlist.  
75. **Hotfixes** — what shipped, why.  
76. **Tune metrics** — thresholds updated.  
77. **Perf regressions** — fixes with proof.  
78. **Stabilize rollout** — declare “steady state.”

### Phase 19 — Long‑term maintenance

79. **Remove feature flags** — safe removal plan.  
80. **Tech debt cleanup** — list + prioritization.  
81. **Docs updated** — what changed for the next engineer.  
82. **Runbooks updated** — how to operate and fix.  
83. **Knowledge sharing** — notes for the team memory store.

---

## Long‑term memory (explained simply)

In a real company, “memory” is messy: wikis, Slack threads, tickets, design docs, incident reports, and people’s heads. Mature orgs **fight drift** by pushing the important stuff into **durable artifacts** people can find next quarter.

We copy that idea on purpose.

Think of three filing cabinets (they all **merge into the top of the context bundle** after a **memory‑first query** each time):

1. **Project cabinet** — everything for *this* initiative (RFC, tasks, test logs).  
2. **Company cabinet** — policies, standards, past incidents, reusable playbooks.  
3. **Similar problems cabinet** — semantic search (“have we seen a migration like this before?”).

**Read order:** hit these stores **before** opening arbitrary repo paths or generating new text, so prior lessons shape the question you ask of the code.

Every time a phase completes, we store:

- **The final structured output** (the form)  
- **Evidence attachments** (command outputs, links)  
- **A short “decision log”** (what we chose and why)

That is how tomorrow’s run starts closer to **“I remember the last time we did this”** instead of **“minute zero, no context.”** It is the same mechanism as a senior engineer who files a good RFC and a good postmortem: **the next person inherits the thinking**, not just the code.

---

## Always‑on self‑improvement (safely, with real algorithms)

**Self‑improvement is not magic and not optional.** In healthy orgs it is **discipline after feedback**, on a loop. Here we **encode** that loop so it runs **after every meaningful outcome**, not only after incidents.

### The human parallel (what big orgs actually do)

1. **Detect** quickly (alerts, dashboards, customer signal).  
2. **Stop the bleeding** (rollback, flag off, throttle).  
3. **Explain** without blame (timeline, root causes, contributing factors).  
4. **Prevent recurrence** with boring fixes: tests, guardrails, docs, safer defaults.  
5. **Track** prevention tasks until done—otherwise “lessons learned” is theater.

### The machine parallel (what we run on a schedule)

**After each phase, failed gate, merge, or deploy:**

1. **Log** what happened (traces, scores, diff summaries)—**append to the in‑repo project log** first so the customer repo stays the source of narrative truth.  
2. **Write memory** (decision log, postmortem snippet, “what not to do again”) with citations—mirror or summarize from the project log when useful.  
3. **Add or tighten verifiers**: new unit/integration/e2e tests, new **eval rubric** rows, new CI policy checks.  
4. **Reflection pass (Reflexion‑style):** a dedicated step produces a **short written critique** of the failure or weak score, grounded in evidence—not a rewrite of history. That text is **stored in memory** and **prepended** on similar tasks later (this is the proven **Reflexion** pattern: learn from verbal feedback and past trajectories without updating neural weights).  
5. **Multi‑critique when stakes are high (MAR‑style):** for security, launch, or migration phases, use **more than one critique persona** (or model) plus a **judge** that merges critiques into one reflection, to cut **confirmation bias** (recent multi‑agent extensions to Reflexion show why separating *act*, *diagnose*, and *aggregate* helps).  
6. **Program / prompt optimization (DSPy family, including GEPA):** for **small, bounded** text modules (e.g. “SLO section generator,” “rollback checklist summarizer”), run an optimizer that proposes new instructions using **execution traces + scores** and, in **GEPA**, **reflective text feedback** and search over prompt variants with **Pareto** tradeoff awareness—**only** promotions that beat the current prompt on **train and held‑out** evals. *GEPA* (“Reflective Prompt Evolution…”, 2025) is the current generation of this line: treat prompts as **evolvable programs** with **verifiable** metrics.  
7. **Verifiable rewards (RLVR mindset):** wherever the truth is **objective**—tests pass, schema validates, linter clean—treat that as the **reward signal** for picking among candidates (best‑of‑N, rerank, or offline preference data). **Reinforcement learning with verifiable rewards** is the research name for “stop training against a mushy reward model when you can run the compiler.” Our **CI + eval harness** is the practical face of that for code and for agent artifacts.  
8. **Human gate for sensitive deltas:** security/compliance wording, production kill switches, and **any** prompt that ships to prod-facing behavior require **approval** or **shadow + A/B** before replace.

**Cadence (so “always” is real):**

- **Micro:** end of every phase → memory + eval backlog triage.  
- **Meso:** every merge → CI + eval regression.  
- **Macro:** nightly/weekly → run fuller eval matrix, consider DSPy/GEPA refresh on approved modules.

**What we will not pretend**

- No silent rewrite of security/compliance text.  
- No prompt “improvement” that only wins on **training** evals—**held‑out** set and canary behavior matter.  
- No skipping tracked prevention tasks.

### Quick reference — proven building blocks we lean on

| Idea | What it gives you | Plain English |
|------|-------------------|---------------|
| **Golden evals + held‑out set** | Regression signal | “Did we get worse?” is a **number**, not a vibe. |
| **Reflexion** | Trajectory + language critique → memory | Fail once, **capture why**, do better on retry. |
| **Multi‑agent / judged reflection (MAR‑style)** | Less self‑delusion | Several critics + a judge **merge** feedback. |
| **DSPy / MIPRO / GEPA** | Data‑driven prompt/program edits | Improve **instructions** using traces and scores; **GEPA** adds strong **reflective** search. |
| **RLVR / test‑as‑reward** | Honest reward | When the **compiler and tests** say yes, reward is not fake. |
| **Best‑of‑N / rerank** | Cheap win at inference | Try a few drafts, **keep the one verifiers like**. |

### Optional deep dives (papers and docs)

**Core agent loops (already in our stack):**

- **Reflexion** (language agents improve from verbal feedback): https://arxiv.org/abs/2303.11366  
- **DSPy GEPA** (reflective prompt evolution with metrics and traces): https://dspy.ai/api/optimizers/GEPA  
- **Multi‑agent reflection** (separate critics + judge; reduces shared blind spots): https://arxiv.org/abs/2512.20845  
- **RL with verifiable rewards** (overview and paper hub): https://huggingface.co/papers/2511.15248 and curated list https://github.com/opendilab/awesome-RLVR  

**Second‑pass pointers (CS / AI / math — see Latest research section):**

- **Agentic SE survey:** https://arxiv.org/abs/2510.09721  
- **Multi‑agent coordination survey:** https://arxiv.org/abs/2502.14743  
- **Formal verification benchmarks (Lean):** https://arxiv.org/abs/2505.23135 · **VeriBench:** https://openreview.net/forum?id=P7NUVF6wo4  
- **LLM + symbolic execution for specs (SESpec):** https://arxiv.org/abs/2506.09550  
- **Sequential / anytime‑valid inference:** https://arxiv.org/abs/2501.03982 · https://arxiv.org/abs/2210.08589  
- **Neuro‑symbolic planning (Metagent‑P):** https://aclanthology.org/2025.findings-acl.1169/  
- **Petri‑style human–AI orchestration (HE2‑Net):** https://arxiv.org/abs/2505.00018  

**April 2026 arXiv snapshot (see “Latest research” section for mapping):**

- **Agentic SE survey (2026):** https://arxiv.org/abs/2601.09822  
- **daVinci‑Dev (agent‑native mid‑training):** https://arxiv.org/abs/2601.18418 · **HiMem:** https://arxiv.org/abs/2601.06377  
- **KLong (long‑horizon agents):** https://arxiv.org/abs/2602.17547 · **ESAA (event sourcing for agents in SE):** https://arxiv.org/abs/2602.23193  
- **SWE‑Adept:** https://arxiv.org/abs/2603.01327 · **AriadneMem:** https://arxiv.org/abs/2603.03290 · **Kumiho (graph belief revision):** https://arxiv.org/abs/2603.17244 · **All‑Mem:** https://arxiv.org/abs/2603.19595 · **Gödel‑Code‑Prover:** https://arxiv.org/abs/2603.19329  
- **VeriAct:** https://arxiv.org/abs/2604.00280 · **Model‑Bench:** https://arxiv.org/abs/2604.01851 · **MemMachine:** https://arxiv.org/abs/2604.04853  
- **GEPA paper (reflective prompt evolution):** https://arxiv.org/abs/2507.19457  

These are **references**, not dependencies—you implement the **same loops** with your stack; the names help you search for battle‑tested patterns.

---

## Latest research — second pass (CS, AI, mathematics, and this playbook) **— as of April 2026**

Research is **not one thread**—it is parallel progress in **computer science** (correctness, specs, concurrency), **artificial intelligence** (agents, planning, memory, learning), and **mathematics / statistics** (optimization, sequential inference, causality). Our doc already encodes **engineering practice**; this section maps **each major sub‑part** of that practice to **where science is actively advancing** so we can **upgrade components** without rewriting the whole lifecycle.

**How to use this:** Pick the **subsystem** you are tuning (memory, triad, experiments, migrations…), read the **1–3 pointers**, implement the **small next step**. Re‑run this scan **quarterly** or when quality plateaus.

**Scope note (April 2026):** The tables below mix **durable 2025 foundations** (still the right textbooks) with **Jan–Apr 2026 preprints** where arXiv already shows a clear shift—especially **agentic SDLC**, **lifelong memory**, and **verification‑beyond‑“verifier says OK”**. Preprints can revise; **anchor process changes** in your **project log** with version + date.

---

### Surveys and taxonomies (orienting the whole field)

| Topic | What it synthesizes | Link | How it sharpens *this* playbook |
|-------|----------------------|------|----------------------------------|
| **Agentic software engineering** | Benchmarks + solution patterns (planning, memory, tools) across SDLC‑like tasks | https://arxiv.org/abs/2510.09721 | Use as a **checklist** against our Phases 0–19: where are we “prompt‑only” vs **tool‑grounded** vs **eval‑measured**? |
| **Multi‑agent coordination** | Who coordinates whom, how, under heterogeneity and scale (includes LLM‑MAS) | https://arxiv.org/abs/2502.14743 | Informs **supervisor vs worker triads**, **parallel vs sequential** todos, and **communication budgets** between agents. |
| **Agentic SE — challenges & opportunities (2026 survey)** | Systematic view of LLM **multi‑agent** systems across the SDLC (orchestration, human–agent, compute) | https://arxiv.org/abs/2601.09822 | Use to **diff** our lifecycle against current failure modes (coordination cost, evaluation gaps) when planning Q2 upgrades. |

---

### April 2026 snapshot — high‑signal arXiv threads (Jan → Apr)

Short list of **fresh** work that **directly touches** subsystems in this document (titles shortened; follow links for details).

| arXiv | Theme | Why it matters for *this* playbook |
|-------|--------|-----------------------------------|
| https://arxiv.org/abs/2601.18418 | **Agent‑native mid‑training** for SE (daVinci‑Dev) | Optional path: **specialize** a local Implementer on **org‑native** trajectories—not required for v1, but the dominant “make the model fit the workflow” research line in early 2026. |
| https://arxiv.org/abs/2601.06377 | **Hierarchical long‑horizon memory** (HiMem) | Reinforces **layered memory + reconsolidation**—same direction as our “filing cabinets,” with explicit **episode vs note** structure. |
| https://arxiv.org/abs/2602.17547 | **Extremely long‑horizon agents** (KLong) | Supports **multi‑week** lifecycle runs: training ideas (trajectory split + progressive RL) are for **model builders**; orchestration still needs **checkpoints + logs** either way. |
| https://arxiv.org/abs/2602.23193 | **Event sourcing for autonomous agents in SE** (ESAA) | Strong alignment with our **append‑only project log + replay**: treat agent mutations as **events** with **boundary contracts** and **replay** for audit/debug. |
| https://arxiv.org/abs/2603.01327 | **Two‑agent deep codebase SWE** (SWE‑Adept) | **Localize** (agent‑directed search) then **resolve** (adaptive planning + Git discipline)—maps cleanly to **splitting Implementer** sub‑behaviors on large repos. |
| https://arxiv.org/abs/2603.03290 | **Lifelong memory “maze”** (AriadneMem) | **Entropy / conflict‑aware** coarsening—use as a recipe for **memory hygiene** jobs so retrieval does not rot as volume grows. |
| https://arxiv.org/abs/2603.17244 | **Graph‑native cognitive memory + belief revision** (Kumiho) | **Formal AGM‑style semantics** on a **versioned property graph**—upgrade path for **high‑stakes** institutional memory (who believed what, when, and why it was retracted). |
| https://arxiv.org/abs/2603.19595 | **Lifelong topology memory** (All‑Mem) | **SPLIT / MERGE / UPDATE** operators with **non‑destructive** evidence—operationalizes “consolidation without amnesia.” |
| https://arxiv.org/abs/2603.19329 | **Hierarchical proof search in Lean** (Gödel‑Code‑Prover) | Pushes **proof decomposition + RL** for code verification—relevant if you expand the **formal methods** slice of the Reviewer/Architect. |
| https://arxiv.org/abs/2604.00280 | **Specs that pass the verifier but lie** (VeriAct + Spec‑Harness) | **Critical:** “Verifier green” ≠ **correct spec**. Reviewer must add **completeness / harness** checks—exactly our **production‑ready** bar for contracts. |
| https://arxiv.org/abs/2604.01851 | **LLMs formally modeling programs** (Model‑Bench) | Surfaces the **program‑modeling bottleneck** for model checking—Architect **sketches** formal models only where tooling exists; expect **low baseline** today. |
| https://arxiv.org/abs/2604.04853 | **Ground‑truth‑preserving memory** (MemMachine) | Argues for **less lossy** long‑term storage of episodes vs aggressive summarization—pairs with our **project log + curated memory** split. |

---

### Computer science (verification, specifications, orchestration)

These lines matter for **Phases 2–3 (contracts, risk)**, **5–8 (implementation, DB safety)**, and the **Reviewer** in each triad.

| Sub‑part of our doc | Research thread | Representative work | Concrete upgrade |
|----------------------|-----------------|----------------------|------------------|
| **Tests as gate (“production ready”)** | **Formal verification** of LLM‑generated code is much harder than “compiles + unit tests”; proof obligations lag code/spec quality | **VERINA** (verifiable codegen in Lean): https://arxiv.org/abs/2505.23135 · **VeriBench** (end‑to‑end Lean 4 verification benchmark): https://openreview.net/forum?id=P7NUVF6wo4 · Dual perspective on LLMs and **code verification**: https://www.frontiersin.org/articles/10.3389/fcomp.2025.1655469 · **Gödel‑Code‑Prover** (hierarchical proof search, Lean 4, Mar 2026): https://arxiv.org/abs/2603.19329 | For **critical** paths only: add optional **proof / spec sketch** tasks in the Architect step; treat **tests** as necessary but not sufficient where math or security invariants demand it. |
| **Contract testing, invariants, “what must always hold”** | **Specification mining + LLMs + symbolic methods** — **and** “verifier‑green but wrong spec” (2026) | **ClassInvGen** (class invariants + tests): https://arxiv.org/abs/2502.18917 · **Loop invariants + static analysis + LLM** (ACInv line): https://arxiv.org/abs/2412.10483 · **SESpec** (symbolic execution + LLM for specs): https://arxiv.org/abs/2506.09550 · **VeriAct** (agentic JML synthesis + **Spec‑Harness** beyond verifier pass, Mar–Apr 2026): https://arxiv.org/abs/2604.00280 · **Model‑Bench** (LLMs → formal models for model checking, Apr 2026): https://arxiv.org/abs/2604.01851 | Architect emits **executable contracts** where tooling exists; Implementer proves via **solver/tests**; Reviewer runs **harness / completeness** checks—not **only** “verifier said OK.” Treat Model‑Bench‑style modeling as **aspirational** on critical services. |
| **Phase DAG, gates, parallel triads** | **Formal models of concurrency and workflow** (deadlock, fairness, guard conditions) | **HE2‑Net** position paper—Petri‑net family for human–AI collaboration, guards, promotion after tests/peer checks: https://arxiv.org/abs/2505.00018 | Optionally **model the lifecycle + todo DAG** as a net (or state machine with proofs); use for **“can we parallelize this edge?”** and **“is this gate reachable?”** analysis—not mandatory day one. |
| **Project log + audit / replay** | **Event sourcing** for agent mutations in SE (Feb 2026) | **ESAA**: https://arxiv.org/abs/2602.23193 | Strengthen **append‑only logs** with **event envelopes** (schema version, causation id) so replay and **cross‑model** workers stay debuggable—matches ESAA’s boundary‑contract story. |

---

### Artificial intelligence (agents, planning, memory, critics)

| Sub‑part of our doc | Research thread | Representative work | Concrete upgrade |
|----------------------|-----------------|----------------------|------------------|
| **Long‑horizon phases + replanning** | **Neuro‑symbolic planning** (neural world models + symbolic checks) | **Metagent‑P** (planning–verification–execution–reflection; open‑world): https://aclanthology.org/2025.findings-acl.1169/ · Neuro‑symbolic + security survey direction: https://arxiv.org/abs/2509.06921 | Add an explicit **verify** micro‑step after Architect plan before Implementer codes; align with our triad but cite **metacognitive** loop language for prompts. |
| **Repo‑scale Implementer (localization vs patch)** | **Specialized agent roles on real codebases** (early 2026) | **SWE‑Adept** (localize + resolve with Git discipline): https://arxiv.org/abs/2603.01327 | For large repos, **split** Implementer into **(a) search/locate** and **(b) patch/verify** sub‑runs with shared **event log**—reduces “edit the wrong file” failures. |
| **Memory first + institutional memory** | **Structured consolidation**, hierarchy, forgetting — **2026 wave** | **TeleMem** (Jan 2026): https://arxiv.org/abs/2601.06037 · **MemVerse**: https://arxiv.org/abs/2512.03627 · **Memora**: https://arxiv.org/abs/2602.03315 · **HiMem** (Jan 2026): https://arxiv.org/abs/2601.06377 · **AriadneMem** (Mar 2026): https://arxiv.org/abs/2603.03290 · **All‑Mem** (Mar 2026): https://arxiv.org/abs/2603.19595 · **Kumiho / graph belief revision** (Mar 2026): https://arxiv.org/abs/2603.17244 · **MemMachine** (Apr 2026): https://arxiv.org/abs/2604.04853 | **Layers + consolidation + non‑destructive evidence** are now **standard research vocabulary**—map All‑Mem’s operators to your **memory janitor** job; use **MemMachine / TeleMem** arguments to resist **lossy** “summarize everything” shortcuts; use **Kumiho** when you need **auditable belief change** (compliance). |
| **Implementer / Reviewer quality** | **Inference‑time scaling + learned or rubric critics** | OpenHands **SWE‑Bench Verified + critic reranking**: https://www.openhands.dev/blog/sota-on-swe-bench-verified-with-inference-time-scaling-and-critic-model · **Learning to verify** trajectories (rubric features, prod proxies): https://www.openhands.dev/blog/20260305-learning-to-verify-ai-generated-code | Keep **best‑of‑N** patches per todo; build a **versioned rubric** that scores **traces**, not only final diff; log **post‑merge survival** for future critic training. |
| **Math‑heavy invariants (optional niche)** | **LLM + proof assistant** | **Lean Copilot** (tactics, premise selection, proof search): https://arxiv.org/abs/2404.12534 | If you adopt Lean/Verus/etc. on critical kernels, Copilot‑class tools sit **inside** the Implementer/Reviewer loop. |
| **Self‑improvement (Reflexion, MAR, GEPA, RLVR)** | Already linked in **Optional deep dives** and **Always‑on self‑improvement** | See above sections | Treat **GEPA** as **multi‑objective evolutionary optimization** over prompts (quality/latency/cost); treat **RLVR** as **reward engineering** tied to **compiler/tests**—both are active **AI + optimization** research fronts, not fads. |

---

### Mathematics and statistics (experiments, optimization, inference)

**April 2026 note:** This pass did **not** surface a new **canonical** arXiv replacement for the **sequential / anytime‑valid** row below; those citations remain the right **statistical hygiene** for Phase 13 until a newer survey is adopted—re‑check **JRSS‑B / JASA / Bernoulli** on your next literature sweep.

| Sub‑part of our doc | Research thread | Representative work | Concrete upgrade |
|----------------------|-----------------|----------------------|------------------|
| **Phase 13 — A/B, peeking, “significance”** | **Sequential / anytime‑valid inference** (valid monitoring at arbitrary stopping times) | **“Anytime validity is free”** (inducing sequential tests): https://arxiv.org/abs/2501.03982 · **Anytime‑valid linear models** (regression‑adjusted causal inference; Netflix‑style): https://arxiv.org/abs/2210.08589 · **Sequential A/B on counting processes** (MLR 2025): https://proceedings.mlr.press/v258/lindon25a.html · Sequential CIs for two proportions (applications): https://www.mdpi.com/2227-7390/13/1/161 | Replace naive “peek until significant” with a **sequential design** library or external review for high‑stakes experiments; document **stopping rules** in the launch packet. |
| **Phase 12–14 — canary / gradual rollout** | **Bandits, control theory, reliability math** (error budgets already in doc) | Classical **SPC / sequential analysis** connects to the same peeking math; multi‑objective rollout is **constrained optimization** | Treat promotion gates as **hypothesis tests** or **Bayesian** decision rules with **pre‑registered** thresholds; align **error budget** burn with **statistical** stopping when experiments gate launches. |
| **DSPy / GEPA self‑improvement** | **Evolutionary multi‑objective optimization**, genetic algorithms, Pareto fronts | Paper (v2 revised **Feb 2026**): https://arxiv.org/abs/2507.19457 · DSPy overview: https://dspy.ai/api/optimizers/GEPA/overview/ | Log **Pareto front** snapshots when optimizing prompts (quality vs tokens vs latency); pick promotions only on **held‑out**—this is explicit **applied math**, not vibes. |

---

### Multi‑agent dynamics (cross‑cutting AI + social science)

| Risk / opportunity | Work | Implication for triads + supervisor |
|--------------------|------|--------------------------------------|
| **When debate helps** | Controlled study: https://huggingface.co/papers/2511.07784 | Invest in **diverse** agents/prompts; do not expect topology alone to save weak models. |
| **Persuasion / consensus bias** | Adversarial influence in multi‑agent LLM groups: https://www.nature.com/articles/s41598-026-42705-7 | Log dissent; use **tools** and **independent** Reviewer prompts; limit **unbounded** “group think” rounds. |

---

### Consolidated upgrade backlog (prioritized by leverage)

| Priority | Subsystem (in our doc) | Science lens | Next step |
|----------|-------------------------|----------------|-----------|
| 1 | **Phase 13 experiments** | **Statistics** — anytime / sequential inference | Adopt a **sequential** or **preregistered** analysis template; ban raw peeking on high‑stakes metrics. |
| 2 | **Reviewer + contracts** | **CS** — VeriAct / Spec‑Harness lesson | Add **completeness & harness** checks so “verifier green” cannot smuggle wrong JML‑style specs (Apr 2026). |
| 3 | **Reviewer + Implementer** | **AI** — critics, inference scaling | Ship **rubric YAML** + **best‑of‑N** for hard todos; log traces for future critic training. |
| 4 | **Project log + multi‑worker** | **CS** — event sourcing (ESAA) | Standardize **event envelopes** + **replay** for agent mutations (Feb 2026). |
| 5 | **Memory pipeline** | **AI + systems** — 2026 lifelong memory | Pilot **All‑Mem‑style** topology operators OR **MemMachine‑style** low‑loss episode retention on top of weekly consolidation. |
| 6 | **Huge‑repo Implementer** | **AI** — SWE‑Adept | Split **localize vs resolve** sub‑runs with shared log (Mar 2026). |
| 7 | **Architect specs** | **CS** — spec / invariant synthesis | Pilot **SESpec‑style** loop on one service: symbolic segments + LLM specs + tests. |
| 8 | **Critical correctness** | **CS + math** — formal methods | Pilot **Gödel‑Code‑Prover**‑class **decomposed** proof attempts on one Lean module if team has skills (Mar 2026). |
| 9 | **Orchestration graph** | **CS** — Petri nets / HAACS | Sketch phase+todos as **HE2‑style** guarded net if parallel triads cause incidents. |
| 10 | **Replanning after spike** | **AI** — neuro‑symbolic | Add **verify** step after Architect plans using Metagent‑P‑style language in prompts. |

**Versioning:** When you adopt a new paper’s idea, add a **one‑line citation + date** to `PROJECT_LOG.md` so the org knows **why** the process changed.

**Cadence:** Re‑scan **quarterly** across **three** trackers: (1) arXiv / ACL / ICML / NeurIPS **agent + SE** keywords, (2) **FSE/ICSE** agentic SE, (3) **JASA / JRSS‑B / sequential analysis** for experimentation. Update this section when a subsystem’s **best known method** moves. **Last full pass for this doc:** **April 2026** (arXiv cs.SE / cs.AI / cs.CL + selected blogs).

---

## Honest limits (so we do not fool ourselves)

- The agent cannot replace **accountability** and **org politics**—it can **prepare packets** and **enforce completeness**.  
- Local models may be weaker on subtle security reasoning; the workflow should **require tool evidence** and **human sign‑off** at the launch gate.  
- “Production ready” means **green CI + real observability + rollback**, not confident language.  
- **Optimizers can overfit** your eval suite if it is tiny or stale; you must **grow and diversify** evals the same way you grow tests—otherwise “self‑improving” becomes “self‑gaming.”  
- **Formal verification and sequential experiment design** are powerful but **specialist**—adopt them where blast radius justifies the cost, not as blanket requirements for every todo.

---

## One‑sentence summary

We implement your lifecycle as a **checkpointed workflow** that mirrors how **mature engineering orgs** reduce human error—reviews, CI gates, staged rollout, observability, and blameless learning—plus **exhaustive clarification before execution**, **implementation split into atomic todos**, each executed by an **Architect → Implementer → Reviewer** triad (with **parallel triads across todos** when the DAG allows), under a supervisor, **tool‑verified outputs**, **long‑term memory read first on every phase**, **whole project context on every phase**, an **append‑only project log inside the repo** for later humans and later runs, and **always‑on self‑improvement** (evals, Reflexion/MAR‑style critique, **DSPy/GEPA**‑style bounded optimization, **verifiable** rewards from tests/CI) so quality **compounds** instead of resetting each chat.
