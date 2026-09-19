from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import Settings, get_settings


SYSTEM_PROMPT = """You are the local AI review layer for BuktiSaham, an Indonesian equity research system.
You review deterministic analysis; you do not create or change the research action.
Rules:
- Treat every numeric field and the deterministic research_action as immutable input.
- Do not invent prices, financial facts, news, targets, dates, or sources.
- If evidence is incomplete, say so.
- Explain the result in concise plain language for an analyst.
- Return valid JSON with keys: summary, key_drivers, key_risks, caveats, analyst_questions.
- key_drivers, key_risks, caveats, analyst_questions must be arrays of strings.
"""


class OllamaClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def review(self, analysis: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.ai_review_enabled:
            return {"status": "disabled", "provider": "ollama", "model": self.settings.ollama_model}

        payload = {
            "model": self.settings.ollama_model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": "Review this deterministic analysis without changing any values or action:\n"
                    + json.dumps(analysis, ensure_ascii=False, default=str),
                },
            ],
            "options": {"temperature": 0.2},
        }
        try:
            with httpx.Client(timeout=self.settings.ollama_timeout_seconds) as client:
                response = client.post(f"{self.settings.ollama_base_url.rstrip('/')}/api/chat", json=payload)
                response.raise_for_status()
                body = response.json()
            text = body.get("message", {}).get("content", "{}")
            parsed = json.loads(text)
            parsed.update({"status": "ok", "provider": "ollama", "model": self.settings.ollama_model})
            return parsed
        except Exception as exc:
            return {
                "status": "unavailable",
                "provider": "ollama",
                "model": self.settings.ollama_model,
                "error": str(exc),
                "summary": "Local AI review is unavailable; deterministic analysis remains valid.",
                "key_drivers": [],
                "key_risks": [],
                "caveats": ["AI review failure does not change the deterministic research action."],
                "analyst_questions": [],
            }

    def health(self) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.settings.ollama_base_url.rstrip('/')}/api/tags")
                response.raise_for_status()
                models = [m.get("name") for m in response.json().get("models", [])]
            return {
                "status": "ok",
                "provider": "ollama",
                "configured_model": self.settings.ollama_model,
                "model_present": any((m or "").startswith(self.settings.ollama_model) for m in models),
                "models": models,
            }
        except Exception as exc:
            return {"status": "unavailable", "provider": "ollama", "error": str(exc)}
