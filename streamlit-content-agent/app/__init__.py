from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

import requests

@dataclass
class LLMConfig:
    provider: str = "ollama"  # "openai" or "ollama"
    model: str = "gpt-4o-mini"
    temperature: float = 0.5
    openai_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

class LLMClient:
    def __init__(self, cfg: Optional[LLMConfig] = None) -> None:
        self.cfg = cfg or LLMConfig()
        # Env overrides
        self.cfg.openai_api_key = self.cfg.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.cfg.ollama_base_url = os.getenv("OLLAMA_BASE_URL", self.cfg.ollama_base_url)
        self.cfg.ollama_model = os.getenv("OLLAMA_MODEL", self.cfg.ollama_model)

    def generate(self, prompt: str, *, temperature: Optional[float] = None, model: Optional[str] = None) -> str:
        t = temperature if temperature is not None else self.cfg.temperature
        m = model or self.cfg.model
        if self.cfg.provider == "ollama":
            return self._ollama_generate(prompt, model=self.cfg.ollama_model, temperature=t)
        return self._openai_generate(prompt, model=m, temperature=t)

    # --- Providers ---
    def _openai_generate(self, prompt: str, *, model: str, temperature: float) -> str:
        from openai import OpenAI
        if not self.cfg.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY missing. Add it to .env or Streamlit sidebar.")
        client = OpenAI(api_key=self.cfg.openai_api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()

    def _ollama_generate(self, prompt: str, *, model: str, temperature: float) -> str:
        # Requires `ollama serve` running locally and model pulled.
        r = requests.post(
            f"{self.cfg.ollama_base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
