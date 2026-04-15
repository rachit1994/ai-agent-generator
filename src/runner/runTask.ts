import { join } from "node:path";
import { defaultRunConfig } from "../config.js";
import { aggregateMetrics } from "../eval/metrics.js";
import { runBaseline } from "../modes/baseline.js";
import { runGuarded } from "../modes/guarded.js";
import { appendTrace, ensureDir, writeJson } from "../storage/fs.js";
import { createRunId } from "../utils/runId.js";
import { ModeType } from "../types.js";

export const executeSingleTask = async (task: string, mode: ModeType): Promise<{ runId: string; output: string }> => {
  const runId = createRunId();
  const outputDir = join("outputs", "runs", runId);
  await ensureDir(outputDir);
  const result = mode === "baseline"
    ? await runBaseline(runId, "manual-task", task, defaultRunConfig)
    : await runGuarded(runId, "manual-task", task, defaultRunConfig);
  for (const event of result.events) await appendTrace(join(outputDir, "traces.jsonl"), event);
  await writeJson(join(outputDir, "config-snapshot.json"), defaultRunConfig);
  await writeJson(join(outputDir, "summary.json"), {
    runId,
    mode,
    provider: defaultRunConfig.provider,
    model: defaultRunConfig.implementationModel,
    metrics: aggregateMetrics(result.events)
  });
  return { runId, output: result.output };
};
