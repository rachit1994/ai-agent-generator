import { describe, expect, test } from "vitest";
import { parseCommand } from "../src/cli/parse.js";

describe("parseCommand", () => {
  test("parses run command", () => {
    const parsed = parseCommand(["node", "cli", "run", "--task", "hello", "--mode", "baseline"]);
    expect(parsed).toEqual({ kind: "run", task: "hello", mode: "baseline" });
  });

  test("rejects invalid mode", () => {
    expect(() => parseCommand(["node", "cli", "run", "--task", "hello", "--mode", "bad"])).toThrow("invalid_run_args");
  });

  test("parses benchmark and report", () => {
    expect(parseCommand(["n", "c", "benchmark", "--suite", "data/mvp-tasks.jsonl"])).toEqual({
      kind: "benchmark",
      suite: "data/mvp-tasks.jsonl",
      mode: "both"
    });
    expect(parseCommand(["n", "c", "benchmark", "--suite", "data/mvp-tasks.jsonl", "--mode", "baseline"])).toEqual({
      kind: "benchmark",
      suite: "data/mvp-tasks.jsonl",
      mode: "baseline"
    });
    expect(parseCommand(["n", "c", "report", "--run-id", "abc"])).toEqual({ kind: "report", runId: "abc" });
  });
});
