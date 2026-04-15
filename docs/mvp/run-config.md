# MVP Run Config Defaults

- provider: `ollama`
- implementation model: `qwen2.5:7b-instruct`
- support model: `gemma4:latest`
- provider base URL: `http://127.0.0.1:11434`

## Budgets

- timeout per task: `90000 ms`
- retry cap per task: `1`
- token budget per task: `4096`

## API Fallback Trigger Rules

1. Structured-output validity drops below 85% after stabilization.
2. Guarded pass rate remains below baseline after two iterations with model-quality evidence.
3. Local median latency is impractical for MVP runtime.
4. If fallback is used, rerun full A/B and document provider/model/reason in report output.
