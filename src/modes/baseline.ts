import { invokeModel } from "../model-adapter/index.js";
import { refusalForUnsafe, validateStructuredOutput } from "../safeguards/policy.js";
import { validateTaskText } from "../safeguards/validation.js";
import { RunConfig, TraceEvent } from "../types.js";

export const runBaseline = async (
  runId: string,
  taskId: string,
  prompt: string,
  config: RunConfig
): Promise<{ output: string; events: TraceEvent[] }> => {
  const started = Date.now();
  const safePrompt = validateTaskText(prompt);
  const refusal = refusalForUnsafe(safePrompt);
  const outputText = refusal
    ? JSON.stringify(refusal)
    : (await invokeModel({
        prompt: `Return JSON {answer,checks,refusal}. Task: ${safePrompt}`,
        model: config.implementationModel,
        provider: config.provider,
        providerBaseUrl: config.providerBaseUrl,
        timeoutMs: config.budgets.timeoutMs
      })).text;
  const ended = Date.now();
  const output = validateStructuredOutput(outputText);
  const event: TraceEvent = {
    run_id: runId,
    task_id: taskId,
    mode: "baseline",
    model: config.implementationModel,
    provider: config.provider,
    stage: "finalize",
    started_at: new Date(started).toISOString(),
    ended_at: new Date(ended).toISOString(),
    latency_ms: ended - started,
    token_input: Math.ceil(safePrompt.length / 4),
    token_output: Math.ceil(output.answer.length / 4),
    estimated_cost_usd: 0,
    retry_count: 0,
    errors: output.refusal ? [output.refusal.code] : [],
    score: {
      passed: output.checks.every((item) => item.passed),
      reliability: output.checks.filter((item) => item.passed).length / output.checks.length,
      validity: 1
    }
  };
  return { output: outputText, events: [event] };
};
