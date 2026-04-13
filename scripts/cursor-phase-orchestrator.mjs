#!/usr/bin/env node
/**
 * Orchestrates repeated Cursor CLI (`agent`) invocations for phased delivery.
 *
 * Prerequisites:
 *   - Cursor CLI installed; `agent` on PATH (or set CURSOR_AGENT_CMD).
 *   - For headless CI: CURSOR_API_KEY (see https://cursor.com/docs/cli/headless )
 *
 * Usage:
 *   node scripts/cursor-phase-orchestrator.mjs
 *
 * Environment:
 *   CURSOR_AGENT_CMD     — executable name or path (default: "agent")
 *   CURSOR_AGENT_ARGS    — extra args before the prompt, space-separated (default: "-p --force")
 *   CURSOR_REPO_ROOT     — cwd for each agent run (default: parent of scripts/)
 *   CURSOR_PHASE_CHECKLIST — path to phased checklist md (default: docs/implementation/2026-04-13-persona-agent-platform-phased-checklist.md)
 *   CURSOR_ORCH_LOG      — append JSON lines with per-run metadata (optional)
 *   DRY_RUN=1            — print prompts only, do not spawn agent
 *
 * @see https://cursor.com/docs/cli/headless
 */

import { spawn } from "node:child_process";
import { appendFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = process.env.CURSOR_REPO_ROOT ?? path.resolve(__dirname, "..");
const CHECKLIST_REL =
  process.env.CURSOR_PHASE_CHECKLIST ??
  "docs/implementation/2026-04-13-persona-agent-platform-phased-checklist.md";
const CHECKLIST_PATH = path.isAbsolute(CHECKLIST_REL)
  ? CHECKLIST_REL
  : path.join(REPO_ROOT, CHECKLIST_REL);

const AGENT_CMD = process.env.CURSOR_AGENT_CMD ?? "agent";
const AGENT_ARGS = (process.env.CURSOR_AGENT_ARGS ?? "-p --force")
  .trim()
  .split(/\s+/)
  .filter(Boolean);
const ORCH_LOG = process.env.CURSOR_ORCH_LOG ?? "";
const DRY_RUN = process.env.DRY_RUN === "1" || process.env.DRY_RUN === "true";

const OUTER_ROUNDS = 30;
const FIX_PASSES = 10;
const TEST_PASSES = 10;

function logOrchestration(entry) {
  if (!ORCH_LOG) {
    return;
  }
  const line = `${JSON.stringify({ t: new Date().toISOString(), ...entry })}\n`;
  try {
    mkdirSync(path.dirname(ORCH_LOG), { recursive: true });
  } catch {
    // ignore if dirname is "."
  }
  appendFileSync(ORCH_LOG, line, "utf8");
}

function buildPrompts(outerIndex) {
  const base = `Repository root: ${REPO_ROOT}. Primary phased checklist (follow it exactly): ${CHECKLIST_PATH}. This is orchestration round ${outerIndex} of ${OUTER_ROUNDS} (outer loop).`;

  const buildNext = `${base}

You are the implementation agent. Identify the **next** program phase that is not yet fully complete according to the checklist (read the checklist file). **Build only that phase**, executing its numbered steps in order, matching repo conventions. Do not skip human-only gates—if blocked, write a short BLOCKED note with what is needed and stop that phase's implementation work.`;

  const fixRemainder = (fixRound) => `${base}

**Remediation pass ${fixRound} of ${FIX_PASSES} for the current phase.**

List everything still incomplete or incorrect for the **current** phase per the checklist (and any acceptance criteria in linked docs). Fix what you can in-repo (code, tests, config). If something cannot be fixed without a human, document it clearly.`;

  const verifyTests = (testRound) => `${base}

**Verification pass ${testRound} of ${TEST_PASSES} for the current phase.**

Prove the implementation matches the phase goal using **automated tests** (run the project's test commands yourself). If tests are missing for this phase's goal, add minimal tests that fail if the goal is not met, then make them pass. Report pass/fail and what you ran.`;

  const documentPhase = `${base}

**Phase documentation.**

Write or update an in-repo artifact (e.g. append to the project work log or a phase notes file under docs/implementation/) summarizing:
- What was completed this phase in this orchestration round
- Whether the phase goal is achieved (yes/no/partial) with evidence (tests, CI, checklist line references)
- What remains, if anything

Keep it factual and grep-friendly.`;

  return { buildNext, fixRemainder, verifyTests, documentPhase };
}

function runAgent(label, prompt) {
  const args = [...AGENT_ARGS, prompt];
  if (DRY_RUN) {
    process.stdout.write(`\n--- DRY_RUN ${label} ---\n${AGENT_CMD} ${args.map((a) => JSON.stringify(a)).join(" ")}\n`);
    return Promise.resolve(0);
  }
  return new Promise((resolve, reject) => {
    const child = spawn(AGENT_CMD, args, {
      cwd: REPO_ROOT,
      stdio: "inherit",
      env: process.env,
    });
    child.on("error", reject);
    child.on("close", (code, signal) => {
      if (signal) {
        reject(new Error(`${label}: terminated by signal ${signal}`));
        return;
      }
      resolve(code ?? 1);
    });
  });
}

async function main() {
  process.stdout.write(
    `Cursor phase orchestrator\n  repo: ${REPO_ROOT}\n  checklist: ${CHECKLIST_PATH}\n  agent: ${AGENT_CMD} ${AGENT_ARGS.join(" ")}\n  outer rounds: ${OUTER_ROUNDS}, fix passes: ${FIX_PASSES}, test passes: ${TEST_PASSES}\n  dry run: ${DRY_RUN}\n\n`,
  );

  for (let outer = 1; outer <= OUTER_ROUNDS; outer += 1) {
    const prompts = buildPrompts(outer);

    const steps = [
      ["build_next_phase", prompts.buildNext],
      ...Array.from({ length: FIX_PASSES }, (_, i) => [
        `fix_remainder_${i + 1}`,
        prompts.fixRemainder(i + 1),
      ]),
      ...Array.from({ length: TEST_PASSES }, (_, i) => [
        `verify_tests_${i + 1}`,
        prompts.verifyTests(i + 1),
      ]),
      ["document_phase", prompts.documentPhase],
    ];

    for (const [label, prompt] of steps) {
      logOrchestration({ outer, label, status: "start" });
      const code = await runAgent(`${outer}/${OUTER_ROUNDS} ${label}`, prompt);
      logOrchestration({ outer, label, status: "end", exitCode: code });
      if (code !== 0) {
        process.stderr.write(
          `\nOrchestrator: agent exited with code ${code} (${label}, round ${outer}). Stopping.\n`,
        );
        process.exit(code);
      }
    }
  }

  process.stdout.write(`\nCompleted all ${OUTER_ROUNDS} outer rounds (${OUTER_ROUNDS * (1 + FIX_PASSES + TEST_PASSES + 1)} agent invocations).\n`);
}

main().catch((err) => {
  process.stderr.write(`${err.stack ?? err}\n`);
  process.exit(1);
});
