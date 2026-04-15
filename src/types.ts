export type ProviderType = "ollama" | "api";
export type ModeType = "baseline" | "guarded_pipeline";

export interface GuardrailBudgets {
  maxTokens: number;
  maxRetries: number;
  timeoutMs: number;
}

export interface RunConfig {
  provider: ProviderType;
  implementationModel: string;
  supportModel: string;
  providerBaseUrl: string;
  fallbackTriggers: string[];
  budgets: GuardrailBudgets;
}

export interface TaskPayload {
  taskId: string;
  prompt: string;
  expectedChecks: string[];
  difficulty: "simple" | "medium" | "failure-prone";
}

export interface TraceEvent {
  run_id: string;
  task_id: string;
  mode: ModeType;
  model: string;
  provider: ProviderType;
  stage: string;
  started_at: string;
  ended_at: string;
  latency_ms: number;
  token_input: number;
  token_output: number;
  estimated_cost_usd: number;
  retry_count: number;
  errors: string[];
  score: { passed: boolean; reliability: number; validity: number };
  metadata?: Record<string, unknown>;
}
