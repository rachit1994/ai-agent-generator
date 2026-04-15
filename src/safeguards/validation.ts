import { z } from "zod";
import { TaskPayload } from "../types.js";

const taskSchema = z.object({
  taskId: z.string().min(1),
  prompt: z.string().min(1),
  expectedChecks: z.array(z.string()).min(1),
  difficulty: z.enum(["simple", "medium", "failure-prone"])
});

export const validateTask = (value: unknown): TaskPayload => {
  return taskSchema.parse(value);
};

export const validateTaskText = (task: string): string => {
  const trimmed = task.trim();
  if (trimmed.length === 0) throw new Error("invalid_input_empty_task");
  return trimmed;
};
