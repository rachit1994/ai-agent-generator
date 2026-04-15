import { ProviderType } from "../types.js";

export interface ModelRequest {
  prompt: string;
  model: string;
  provider: ProviderType;
  providerBaseUrl: string;
  timeoutMs: number;
}

export interface ModelResponse {
  text: string;
  tokenInput: number;
  tokenOutput: number;
}

const callOllama = async (req: ModelRequest): Promise<ModelResponse> => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), req.timeoutMs);
  try {
    const res = await fetch(`${req.providerBaseUrl}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: req.model, prompt: req.prompt, stream: false }),
      signal: controller.signal
    });
    if (!res.ok) throw new Error(`ollama_http_${res.status}`);
    const body = (await res.json()) as { response: string; prompt_eval_count?: number; eval_count?: number };
    return {
      text: body.response,
      tokenInput: body.prompt_eval_count ?? 0,
      tokenOutput: body.eval_count ?? 0
    };
  } finally {
    clearTimeout(timer);
  }
};

const callApiFallback = async (req: ModelRequest): Promise<ModelResponse> => {
  return {
    text: `api-fallback-disabled-for-mvp: ${req.prompt.slice(0, 80)}`,
    tokenInput: 0,
    tokenOutput: 0
  };
};

export const invokeModel = async (req: ModelRequest): Promise<ModelResponse> => {
  switch (req.provider) {
    case "ollama":
      return callOllama(req);
    case "api":
      return callApiFallback(req);
  }
};
