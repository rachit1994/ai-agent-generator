import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { readJson, writeJson } from "../storage/fs.js";

interface BenchmarkSummary {
  runId: string;
  suitePath: string;
  suiteVersion: string;
  mode: "baseline" | "guarded_pipeline" | "both";
  provider: string;
  models: { implementation: string; support: string };
  budgets: { maxTokens: number; maxRetries: number; timeoutMs: number };
  passRateDeltaPoints: number;
  medianLatencyDeltaPercent: number;
  perTaskDeltas: Array<{
    taskId: string;
    baselinePassed: boolean | null;
    guardedPassed: boolean | null;
    baselineLatencyMs: number | null;
    guardedLatencyMs: number | null;
    passDelta: number;
    latencyDeltaMs: number;
  }>;
  verdict: "supported" | "partially supported" | "rejected" | "inconclusive";
  baselineMetrics: Record<string, number>;
  guardedMetrics: Record<string, number>;
}

export const generateReport = async (runId: string): Promise<string> => {
  const base = join("outputs", "runs", runId);
  const summary = await readJson<BenchmarkSummary>(join(base, "summary.json"));
  const recommendation = summary.verdict === "supported" ? "continue" : summary.verdict === "partially supported" ? "pivot" : "stop";
  const report = [
    "# MVP Decision Report",
    `- run_id: ${summary.runId}`,
    `- provider: ${summary.provider}`,
    `- mode: ${summary.mode}`,
    `- implementation_model: ${summary.models.implementation}`,
    `- support_model: ${summary.models.support}`,
    `- suite: ${summary.suitePath}`,
    `- suite_version: ${summary.suiteVersion}`,
    `- budgets: tokens=${summary.budgets.maxTokens}, retries=${summary.budgets.maxRetries}, timeout_ms=${summary.budgets.timeoutMs}`,
    `- verdict: ${summary.verdict}`,
    `- recommendation: ${recommendation}`,
    `- pass_rate_delta_points: ${summary.passRateDeltaPoints}`,
    `- median_latency_delta_percent: ${summary.medianLatencyDeltaPercent}`,
    "",
    "## Baseline Metrics",
    ...Object.entries(summary.baselineMetrics).map(([key, value]) => `- ${key}: ${value}`),
    "",
    "## Guarded Metrics",
    ...Object.entries(summary.guardedMetrics).map(([key, value]) => `- ${key}: ${value}`)
    ,
    "",
    "## Per-task deltas",
    ...summary.perTaskDeltas.map((item) =>
      `- ${item.taskId}: pass_delta=${item.passDelta}, latency_delta_ms=${item.latencyDeltaMs}, baseline_pass=${String(item.baselinePassed)}, guarded_pass=${String(item.guardedPassed)}`
    )
  ].join("\n");
  await writeJson(join(base, "report-meta.json"), { recommendation });
  await writeFile(join(base, "report.md"), report, "utf8");
  return report;
};
