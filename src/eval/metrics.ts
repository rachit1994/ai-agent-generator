import { TraceEvent } from "../types.js";

export interface AggregateMetrics {
  passRate: number;
  reliability: number;
  p50Latency: number;
  p95Latency: number;
  avgCost: number;
  validityRate: number;
  retryFrequency: number;
}

const percentile = (numbers: number[], p: number): number => {
  if (numbers.length === 0) return 0;
  const sorted = [...numbers].sort((a, b) => a - b);
  const index = Math.floor((sorted.length - 1) * p);
  return sorted[index] ?? 0;
};

export const aggregateMetrics = (events: TraceEvent[]): AggregateMetrics => {
  const finals = events.filter((event) => event.stage === "finalize");
  const total = finals.length || 1;
  const passes = finals.filter((event) => event.score.passed).length;
  const validity = finals.filter((event) => event.score.validity >= 1).length;
  return {
    passRate: passes / total,
    reliability: finals.reduce((acc, e) => acc + e.score.reliability, 0) / total,
    p50Latency: percentile(finals.map((event) => event.latency_ms), 0.5),
    p95Latency: percentile(finals.map((event) => event.latency_ms), 0.95),
    avgCost: finals.reduce((acc, e) => acc + e.estimated_cost_usd, 0) / total,
    validityRate: validity / total,
    retryFrequency: finals.reduce((acc, e) => acc + e.retry_count, 0) / total
  };
};

export const verdictFor = (
  baseline: AggregateMetrics,
  guarded: AggregateMetrics
): "supported" | "partially supported" | "rejected" | "inconclusive" => {
  const passDelta = (guarded.passRate - baseline.passRate) * 100;
  const latencyDelta = baseline.p50Latency === 0 ? 0 : ((guarded.p50Latency - baseline.p50Latency) / baseline.p50Latency) * 100;
  if (passDelta >= 10 && guarded.reliability > baseline.reliability && latencyDelta <= 30) return "supported";
  if (passDelta > 0 && (latencyDelta > 30 || guarded.avgCost > baseline.avgCost)) return "partially supported";
  if (Number.isNaN(passDelta) || Number.isNaN(latencyDelta)) return "inconclusive";
  return "rejected";
};
