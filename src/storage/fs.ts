import { mkdir, writeFile, appendFile, readFile } from "node:fs/promises";
import { dirname } from "node:path";
import { TraceEvent } from "../types.js";

export const ensureDir = async (path: string): Promise<void> => {
  await mkdir(path, { recursive: true });
};

export const writeJson = async (path: string, value: unknown): Promise<void> => {
  await ensureDir(dirname(path));
  await writeFile(path, JSON.stringify(value, null, 2), "utf8");
};

export const appendTrace = async (path: string, trace: TraceEvent): Promise<void> => {
  await ensureDir(dirname(path));
  await appendFile(path, `${JSON.stringify(trace)}\n`, "utf8");
};

export const readJson = async <T>(path: string): Promise<T> => {
  const content = await readFile(path, "utf8");
  return JSON.parse(content) as T;
};
