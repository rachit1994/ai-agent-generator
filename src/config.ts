import { RunConfig } from "./types.js";

export const defaultRunConfig: RunConfig = {
  provider: "ollama",
  implementationModel: "qwen2.5:7b-instruct",
  supportModel: "gemma 4",
  providerBaseUrl: "http://127.0.0.1:11434",
  fallbackTriggers: [
    "validity_rate_below_0_85_after_stabilization",
    "guarded_pass_rate_below_baseline_after_two_iterations",
    "median_latency_impractical_for_mvp",
    "fallback_requires_full_ab_rerun_and_report_annotation"
  ],
  budgets: {
    maxTokens: 4096,
    maxRetries: 1,
    timeoutMs: 90_000
  }
};
