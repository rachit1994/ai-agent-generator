import { ModeType } from "../types.js";

export type ParsedCommand =
  | { kind: "run"; task: string; mode: ModeType }
  | { kind: "benchmark"; suite: string; mode: ModeType | "both" }
  | { kind: "report"; runId: string };

const readFlag = (args: string[], name: string): string | null => {
  const index = args.indexOf(name);
  if (index < 0) return null;
  return args[index + 1] ?? null;
};

export const parseCommand = (argv: string[]): ParsedCommand => {
  const [, , command, ...args] = argv;
  switch (command) {
    case "run": {
      const task = readFlag(args, "--task");
      const mode = readFlag(args, "--mode");
      if (!task || (mode !== "baseline" && mode !== "guarded_pipeline")) throw new Error("invalid_run_args");
      return { kind: "run", task, mode };
    }
    case "benchmark": {
      const suite = readFlag(args, "--suite");
      const mode = readFlag(args, "--mode") ?? "both";
      if (mode !== "baseline" && mode !== "guarded_pipeline" && mode !== "both") throw new Error("invalid_benchmark_args");
      if (!suite) throw new Error("invalid_benchmark_args");
      return { kind: "benchmark", suite, mode };
    }
    case "report": {
      const runId = readFlag(args, "--run-id");
      if (!runId) throw new Error("invalid_report_args");
      return { kind: "report", runId };
    }
    default:
      throw new Error("unknown_command");
  }
};
