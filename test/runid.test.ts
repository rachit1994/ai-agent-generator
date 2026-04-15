import { describe, expect, test } from "vitest";
import { createRunId } from "../src/utils/runId.js";

describe("createRunId", () => {
  test("produces timestamped id", () => {
    const id = createRunId();
    expect(id).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });

  test("produces unique values", () => {
    expect(createRunId()).not.toBe(createRunId());
  });
});
