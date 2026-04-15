import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { defaultRunConfig } from "../config.js";
import { aggregateMetrics, verdictFor } from "../eval/metrics.js";
import { runBaseline } from "../modes/baseline.js";
import { runGuarded } from "../modes/guarded.js";
import { appendTrace, ensureDir, writeJson } from "../storage/fs.js";
import { validateTask } from "../safeguards/validation.js";
import { createRunId } from "../utils/runId.js";
import { TaskPayload, TraceEvent } from "../types.js";

const readSuite = async (suitePath: string): Promise<TaskPayload[]> => {
  const content = await readFile(suitePath, "utf8");
  return content.split("\n").filter(Boolean).map((line) => validateTask(JSON.parse(line)));
};

interface PerTaskDelta {
  taskId: string;
  baselinePassed: boolean | null;
  guardedPassed: boolean | null;
  baselineLatencyMs: number | null;
  guardedLatencyMs: number | null;
  baselineRetryCount: number | null;
  guardedRetryCount: number | null;
  passDelta: number;
  latencyDeltaMs: number;
}

const findFinalize = (events: TraceEvent[], taskId: string): TraceEvent | null => {
  return events.find((event) => event.task_id === taskId && event.stage === "finalize") ?? null;
};

const perTaskDeltas = (tasks: TaskPayload[], baselineEvents: TraceEvent[], guardedEvents: TraceEvent[]): PerTaskDelta[] => {
  return tasks.map((task) => {
    const baselineFinal = findFinalize(baselineEvents, task.taskId);
    const guardedFinal = findFinalize(guardedEvents, task.taskId);
    const baselinePass = baselineFinal?.score.passed ?? null;
    const guardedPass = guardedFinal?.score.passed ?? null;
    const baselineLatency = baselineFinal?.latency_ms ?? null;
    const guardedLatency = guardedFinal?.latency_ms ?? null;
    const baselineRetry = baselineFinal?.retry_count ?? null;
    const guardedRetry = guardedFinal?.retry_count ?? null;
    return {
      taskId: task.taskId,
      baselinePassed: baselinePass,
      guardedPassed: guardedPass,
      baselineLatencyMs: baselineLatency,
      guardedLatencyMs: guardedLatency,
      baselineRetryCount: baselineRetry,
      guardedRetryCount: guardedRetry,
      passDelta: (guardedPass ? 1 : 0) - (baselinePass ? 1 : 0),
      latencyDeltaMs: (guardedLatency ?? 0) - (baselineLatency ?? 0)
    };
  });
};

export const runBenchmark = async (
  suitePath: string,
  mode: "baseline" | "guarded_pipeline" | "both" = "both"
): Promise<{ runId: string; verdict: string }> => {
  const tasks = await readSuite(suitePath);
  const runId = createRunId();
  const outputDir = join("outputs", "runs", runId);
  await ensureDir(outputDir);
  const baselineEvents: TraceEvent[] = [];
  const guardedEvents: TraceEvent[] = [];
  for (const task of tasks) {
    if (mode === "baseline" || mode === "both") {
      const baseline = await runBaseline(runId, task.taskId, task.prompt, defaultRunConfig);
      baselineEvents.push(...baseline.events);
    }
    if (mode === "guarded_pipeline" || mode === "both") {
      const guarded = await runGuarded(runId, task.taskId, task.prompt, defaultRunConfig);
      guardedEvents.push(...guarded.events);
    }
  }
  for (const event of [...baselineEvents, ...guardedEvents]) await appendTrace(join(outputDir, "traces.jsonl"), event);
  await writeJson(join(outputDir, "config-snapshot.json"), defaultRunConfig);
  const baselineMetrics = aggregateMetrics(baselineEvents);
  const guardedMetrics = aggregateMetrics(guardedEvents);
  const verdict = mode === "both" ? verdictFor(baselineMetrics, guardedMetrics) : "inconclusive";
  const passRateDeltaPoints = (guardedMetrics.passRate - baselineMetrics.passRate) * 100;
  const medianLatencyDeltaPercent = baselineMetrics.p50Latency === 0
    ? 0
    : ((guardedMetrics.p50Latency - baselineMetrics.p50Latency) / baselineMetrics.p50Latency) * 100;
  const summary = {
    runId,
    suitePath,
    suiteVersion: "mvp-tasks-v1",
    mode,
    provider: defaultRunConfig.provider,
    models: {
      implementation: defaultRunConfig.implementationModel,
      support: defaultRunConfig.supportModel
    },
    budgets: defaultRunConfig.budgets,
    baselineMetrics,
    guardedMetrics,
    passRateDeltaPoints,
    medianLatencyDeltaPercent,
    perTaskDeltas: perTaskDeltas(tasks, baselineEvents, guardedEvents),
    verdict
  };
  await writeJson(join(outputDir, "summary.json"), summary);
  return { runId, verdict };
};
