import { randomUUID } from "node:crypto";

export const createRunId = (): string => {
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  return `${stamp}-${randomUUID().slice(0, 8)}`;
};
