from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def invoke_model(
    prompt: str,
    model: str,
    provider: str,
    provider_base_url: str,
    timeout_ms: int,
    *,
    response_format: str | None = None,
    options: dict | None = None,
    keep_alive: int | str | None = None,
) -> dict:
    if provider == "api":
        return {"text": '{"answer":"","checks":[{"name":"api","passed":false}],"refusal":{"code":"api_disabled","reason":"fallback_disabled_for_sde"}}', "token_input": 0, "token_output": 0}
    payload_obj: dict = {"model": model, "prompt": prompt, "stream": False}
    if response_format is not None:
        payload_obj["format"] = response_format
    if options is not None:
        payload_obj["options"] = options
    if keep_alive is not None:
        payload_obj["keep_alive"] = keep_alive
    payload = json.dumps(payload_obj).encode("utf-8")
    req = Request(
        f"{provider_base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    error = None
    try:
        with urlopen(req, timeout=max(timeout_ms / 1000, 1)) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = ""
        body = {"response": "", "prompt_eval_count": 0, "eval_count": 0}
        error = f"{type(exc).__name__}:{exc.code}:{detail[:200]}"
    except URLError as exc:
        body = {"response": "", "prompt_eval_count": 0, "eval_count": 0}
        error = f"{type(exc).__name__}"
    except Exception as exc:
        body = {"response": "", "prompt_eval_count": 0, "eval_count": 0}
        detail = str(exc)[:500] if str(exc) else ""
        error = f"{type(exc).__name__}:{detail}" if detail else f"{type(exc).__name__}"
    if error is None and isinstance(body, dict) and body.get("error"):
        error = f"ollama_error:{str(body.get('error'))[:200]}"
    return {
        "text": body.get("response", ""),
        "token_input": int(body.get("prompt_eval_count", 0)),
        "token_output": int(body.get("eval_count", 0)),
        "error": error,
        "total_duration": body.get("total_duration"),
        "load_duration": body.get("load_duration"),
        "prompt_eval_duration": body.get("prompt_eval_duration"),
        "eval_duration": body.get("eval_duration"),
    }
