import { generateReport } from "../report/report.js";
import { runBenchmark } from "../runner/benchmark.js";
import { executeSingleTask } from "../runner/runTask.js";
import { parseCommand } from "./parse.js";

const main = async (): Promise<void> => {
  const parsed = parseCommand(process.argv);
  switch (parsed.kind) {
    case "run": {
      const result = await executeSingleTask(parsed.task, parsed.mode);
      console.log(JSON.stringify({ run_id: result.runId, output: result.output }, null, 2));
      return;
    }
    case "benchmark": {
      const result = await runBenchmark(parsed.suite, parsed.mode);
      console.log(JSON.stringify(result, null, 2));
      return;
    }
    case "report": {
      const report = await generateReport(parsed.runId);
      console.log(report);
    }
  }
};

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
