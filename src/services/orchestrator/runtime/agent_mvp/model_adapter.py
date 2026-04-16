from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen


def invoke_model(prompt: str, model: str, provider: str, provider_base_url: str, timeout_ms: int) -> dict:
    if provider == "api":
        return {"text": '{"answer":"","checks":[{"name":"api","passed":false}],"refusal":{"code":"api_disabled","reason":"fallback_disabled_for_mvp"}}', "token_input": 0, "token_output": 0}
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = Request(
        f"{provider_base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=max(timeout_ms / 1000, 1)) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except URLError:
        body = {"response": "", "prompt_eval_count": 0, "eval_count": 0}
    return {
        "text": body.get("response", ""),
        "token_input": int(body.get("prompt_eval_count", 0)),
        "token_output": int(body.get("eval_count", 0)),
    }
