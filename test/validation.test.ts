import { describe, expect, test } from "vitest";
import { validateTask, validateTaskText } from "../src/safeguards/validation.js";

describe("validation", () => {
  test("validates task payload shape", () => {
    const payload = validateTask({
      taskId: "t1",
      prompt: "hello",
      expectedChecks: ["non-empty"],
      difficulty: "simple"
    });
    expect(payload.taskId).toBe("t1");
  });

  test("fails empty input", () => {
    expect(() => validateTaskText("  ")).toThrow("invalid_input_empty_task");
  });
});
