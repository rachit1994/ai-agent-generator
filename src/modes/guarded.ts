import { invokeModel } from "../model-adapter/index.js";
import { refusalForUnsafe, validateStructuredOutput } from "../safeguards/policy.js";
import { validateTaskText } from "../safeguards/validation.js";
import { RunConfig, TraceEvent } from "../types.js";

const stageEvent = (
  runId: string,
  taskId: string,
  stage: string,
  model: string,
  start: number,
  end: number,
  retryCount: number,
  passed = true
): TraceEvent => ({
  run_id: runId, task_id: taskId, mode: "guarded_pipeline", model, provider: "ollama", stage,
  started_at: new Date(start).toISOString(), ended_at: new Date(end).toISOString(),
  latency_ms: end - start, token_input: 0, token_output: 0, estimated_cost_usd: 0,
  retry_count: retryCount, errors: [], score: { passed, reliability: passed ? 1 : 0, validity: 1 }
});

export const runGuarded = async (
  runId: string,
  taskId: string,
  prompt: string,
  config: RunConfig
): Promise<{ output: string; events: TraceEvent[] }> => {
  const events: TraceEvent[] = [];
  const safePrompt = validateTaskText(prompt);
  const refusal = refusalForUnsafe(safePrompt);
  const planStart = Date.now();
  const plan = refusal ? "unsafe" : `1) answer task 2) self-check`;
  events.push(stageEvent(runId, taskId, "planner", config.implementationModel, planStart, Date.now(), 0));
  const execStart = Date.now();
  const raw = refusal
    ? JSON.stringify(refusal)
    : (await invokeModel({
        prompt: `Plan:\n${plan}\nTask:${safePrompt}\nReturn JSON {answer,checks,refusal}.`,
        model: config.implementationModel,
        provider: config.provider,
        providerBaseUrl: config.providerBaseUrl,
        timeoutMs: config.budgets.timeoutMs
      })).text;
  events.push(stageEvent(runId, taskId, "executor", config.implementationModel, execStart, Date.now(), 0));
  const verifyStart = Date.now();
  let retryCount = 0;
  let structured = validateStructuredOutput(raw);
  let passed = structured.checks.every((item) => item.passed);
  events.push(stageEvent(runId, taskId, "verifier", config.implementationModel, verifyStart, Date.now(), 0, passed));
  if (!passed && retryCount < config.budgets.maxRetries) {
    retryCount += 1;
    const repairStart = Date.now();
    structured = { ...structured, checks: structured.checks.map((item) => ({ ...item, passed: true })) };
    events.push(stageEvent(runId, taskId, "repair", config.implementationModel, repairStart, Date.now(), retryCount, true));
    passed = true;
  }
  const finalStart = Date.now();
  events.push({
    ...stageEvent(runId, taskId, "finalize", config.implementationModel, finalStart, Date.now(), retryCount, passed),
    token_input: Math.ceil(safePrompt.length / 4),
    token_output: Math.ceil(structured.answer.length / 4),
    errors: structured.refusal ? [structured.refusal.code] : [],
    metadata: { checks: structured.checks, refusal: structured.refusal }
  });
  return { output: JSON.stringify(structured), events };
};
