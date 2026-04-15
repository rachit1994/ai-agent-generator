import { z } from "zod";

const outputSchema = z.object({
  answer: z.string().min(1),
  checks: z.array(z.object({ name: z.string(), passed: z.boolean() })).min(1),
  refusal: z
    .object({ code: z.string(), reason: z.string() })
    .nullable()
});

export interface StructuredOutput {
  answer: string;
  checks: Array<{ name: string; passed: boolean }>;
  refusal: { code: string; reason: string } | null;
}

export const refusalForUnsafe = (text: string): StructuredOutput | null => {
  const normalized = text.toLowerCase();
  const unsafe = ["credential", "password dump", "exfiltrate", "rm -rf /"];
  const matched = unsafe.find((entry) => normalized.includes(entry));
  if (!matched) return null;
  return {
    answer: "",
    checks: [{ name: "safety", passed: false }],
    refusal: { code: "unsafe_action_refused", reason: `blocked_keyword:${matched}` }
  };
};

export const validateStructuredOutput = (text: string): StructuredOutput => {
  try {
    const parsed = JSON.parse(text) as unknown;
    return outputSchema.parse(parsed);
  } catch {
    return {
      answer: "",
      checks: [{ name: "schema", passed: false }],
      refusal: { code: "malformed_output", reason: "output_schema_validation_failed" }
    };
  }
};
