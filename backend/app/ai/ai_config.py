"""AI configuration and the single provider-call entry point.

All provider credentials come from environment variables (see config.py). Nothing here is ever sent to the
frontend. Every call is bounded by a timeout and any failure raises AIUnavailable so callers can fall back.
"""
import logging

import requests
from flask import current_app

log = logging.getLogger(__name__)


class AIUnavailable(Exception):
    pass


def provider():
    return current_app.config.get("AI_PROVIDER", "none")


def is_configured():
    return provider() in ("gemini", "openai") and bool(current_app.config.get("AI_API_KEY"))


def status():
    return {"configured": is_configured(), "provider": provider() if is_configured() else "local-fallback"}


def call_llm(system_prompt, user_prompt, json_mode=False):
    if not is_configured():
        raise AIUnavailable("AI provider not configured")
    cfg = current_app.config
    timeout = cfg["AI_TIMEOUT_SECONDS"]
    try:
        if provider() == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{cfg['AI_MODEL']}:generateContent"
            body = {
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 700},
            }
            if json_mode:
                body["generationConfig"]["responseMimeType"] = "application/json"
            r = requests.post(url, json=body, headers={"x-goog-api-key": cfg["AI_API_KEY"]}, timeout=timeout)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        url = cfg["AI_BASE_URL"].rstrip("/") + "/chat/completions"
        body = {"model": cfg["AI_MODEL"], "temperature": 0.2, "max_tokens": 700,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        r = requests.post(url, json=body, headers={"Authorization": f"Bearer {cfg['AI_API_KEY']}"}, timeout=timeout)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        # never log the key or request body
        log.warning("AI provider call failed: %s", type(exc).__name__)
        raise AIUnavailable("AI provider unavailable") from exc
