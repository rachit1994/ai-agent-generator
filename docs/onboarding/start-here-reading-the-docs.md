# Reading the documentation — where to start

This page is an easy on-ramp: **where to start**, **why the project exists**, and **what each “version” means** in everyday language. You can follow the ideas here even if you are not diving into Python yet.

**If you are an LLM or any automated reader:** treat this page as **routing instructions**. Prefer **short** docs first (`action-plan.md`, then `../sde/what.md`, then `../coding-agent/execution.md`). For **what the CLI implements today** vs common open-source harness patterns, read [`../sde/core-features-and-upstream-parity.md`](../sde/core-features-and-upstream-parity.md). Do **not** treat research papers or the long master architecture as permission to skip **V1** checks (HS01–HS06; **HS04** also reflects **static code gates** when `static_gates_report.json` is present). When you summarize for a human, say **what must be true on disk** (artifacts + gates), not only model intent.

---

## Words you will keep seeing

| Word | In everyday terms |
|------|-------------------|
| **SDE** | A **local tool** you run on a machine. It helps AI “workers” complete coding tasks in a structured way. |
| **Agent** | An AI step that behaves like a **teammate who still needs review** — it proposes work; it does not get the final say on quality or safety by itself. |
| **Orchestrator** | The **manager** in software: order, rules, and records. It is not “the chat”; it is the process wrapped around the model. |
| **CTO gates** | **Quality checks** (reliability, delivery, governance) — the bar you would expect before calling something shippable. |
| **Hard-stop (HS01, HS02, …)** | A **rule that must pass** or the work cannot be marked good — like a release checklist with teeth. |
| **Version (V1–V7)** | **Stages of one product**, not seven separate products. Each stage adds more real-world process (planning, reviews, memory, and so on). |
| **Spec** | A **written agreement** in Markdown: what the system should do and what files or scores prove it. |

---

## Why this project exists

**The pain point:** A lot of AI coding demos look fine on a single short task. They rarely behave like a **real team**: no solid plan, no second pair of eyes, no proof that tests passed, no clear answer to “why did the system choose this?”

**The approach:** Run AI more like a **small company**:

- **Plan** before big builds (discovery, open questions, written docs).
- **Someone else reviews** before moving on (same idea as code review).
- **Tests and checks** have to pass before anyone says “done.”
- The system **writes down what it learned** so the next stretch of work goes smoother.
- **Several streams of work** can run at once only when the rules keep people from overwriting each other.

**In one line:** One SDE-shaped program should be able to push a **real product** (say, a web app with UI, API, database, and tests) toward something you could **honestly ship** — with **evidence** and **gates**, not just a chat log.

The long-range blueprint is [AI-Professional-Evolution-Master-Architecture.md](../architecture/AI-Professional-Evolution-Master-Architecture.md). The **day-to-day story** of how work should flow is [action-plan.md](action-plan.md).

---

## What each version adds (V1–V7)

Think of a ladder: each step adds trust and process. **Together** they tell one product story.

| Version | Short label | When this step is “real,” what you get |
|---------|-------------|----------------------------------------|
| **V1** — Execution | **Trust base** | Every run leaves a **clear paper trail**: scores, reviews, limits, safety signals. You can audit what happened. |
| **V2** — Planning | **Planning first** | Before heavy coding: **discovery**, **questions**, **docs**, **locked plan**, plus a **learning log** of what you figured out. |
| **V3** — Completion | **Build and prove** | Work in **small steps** with **review between steps**, then **tests/checks**, then an explicit **“definition of done.”** |
| **V4** — Events | **Replay and audit** | Important decisions live in a store you can **replay** — harder to hide or hand-wave mistakes. |
| **V5** — Memory | **Institutional memory** | Lessons **carry across tasks**, with rules so bad or conflicting “facts” do not quietly take over. |
| **V6** — Evolution | **Learn and level up** | After rough spots: **reflection**, **targeted practice**, **canary** tries before changing how the system runs; **promotion** only with evidence. |
| **V7** — Organization | **Many hands, clear lanes** | **Parallel work**, **leases** on folders (“only you edit this area now”), and **permissions** so streams do not collide. |

**Rule that never moves:** V1’s safety rules **always come first**. Later versions add speed and learning **inside** those rules — never by deleting them.

---

## A simple reading order

**About half an hour:** read these three, in order.

1. **[action-plan.md](action-plan.md)** — the story from “what we want” to “how work flows” (sections 1–2 are the lightest).
2. **[sde/what.md](../sde/what.md)** — what the **tool** does today (`run`, `benchmark`, `report`).
3. **[coding-agent/execution.md](../coding-agent/execution.md)** — the **Goal** and **“How the runtime drives a full-stack task.”** That is where CTO-style gates really show up.

**If you have a full day:** keep going in this order.

4. **[coding-agent/planning.md](../coding-agent/planning.md)** — **“How planning and learning work in practice.”**
5. **[coding-agent/completion.md](../coding-agent/completion.md)** — **“How the build loop works in practice.”**
6. **[architecture-goal-completion.md](../architecture/architecture-goal-completion.md)** — what “all versions done” **does** and **does not** mean next to the huge master doc.
7. Skim **[coding-agent/events.md](../coding-agent/events.md)**, **[coding-agent/memory.md](../coding-agent/memory.md)**, **[coding-agent/evolution.md](../coding-agent/evolution.md)**, **[coding-agent/organization.md](../coding-agent/organization.md)** — each opens with a **“How … works in practice”** section.

**If you lose the thread:** open **[README.md](../README.md)** one level up — it is the full map and links out to research.

---

## Docs vs code (simple picture)

- **Docs** = the **recipe and the house rules** (“what good looks like”).
- **Code** = the **kitchen** trying to cook to that recipe.

Right now, **later steps (roughly V4–V7) exist more on paper than in code**. That is on purpose: agree the contract, then build toward it. If a spec describes something you do not see in code yet, you are usually looking at the **target**, not a mistake in how you read.

**Ready to open files?** Use the companion guide: **[start-here-reading-the-code.md](start-here-reading-the-code.md)**.

---

## Quick “what should I open?”

| You want to… | Open |
|----------------|------|
| Describe the product in a short conversation | [action-plan.md](action-plan.md) §1–2 |
| Talk about quality gates | [coding-agent/execution.md](../coding-agent/execution.md) (balanced gates + hard-stops) |
| Walk someone through the docs set | This page, then [README.md](../README.md) |
| Walk someone through the code layout | [start-here-reading-the-code.md](start-here-reading-the-code.md) |
| See the full long-term picture | [AI-Professional-Evolution-Master-Architecture.md](../architecture/AI-Professional-Evolution-Master-Architecture.md) (long — better as reference than first read) |

---

## Changelog

- **2026-04-18:** First version of this guide.
