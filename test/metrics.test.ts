import { describe, expect, test } from "vitest";
import { aggregateMetrics, verdictFor } from "../src/eval/metrics.js";
import { TraceEvent } from "../src/types.js";

const event = (mode: "baseline" | "guarded_pipeline", passed: boolean, latency: number): TraceEvent => ({
  run_id: "r", task_id: "t", mode, model: "m", provider: "ollama", stage: "finalize",
  started_at: new Date().toISOString(), ended_at: new Date().toISOString(),
  latency_ms: latency, token_input: 1, token_output: 1, estimated_cost_usd: 0,
  retry_count: 0, errors: [], score: { passed, reliability: passed ? 1 : 0, validity: 1 }
});

describe("metrics", () => {
  test("aggregates stable stats", () => {
    const m = aggregateMetrics([event("baseline", true, 10), event("baseline", false, 30)]);
    expect(m.passRate).toBe(0.5);
    expect(m.p50Latency).toBe(10);
  });

  test("verdict supports threshold policy", () => {
    const baseline = aggregateMetrics([event("baseline", false, 10), event("baseline", false, 10)]);
    const guarded = aggregateMetrics([event("guarded_pipeline", true, 12), event("guarded_pipeline", true, 12)]);
    expect(verdictFor(baseline, guarded)).toBe("supported");
  });
});
