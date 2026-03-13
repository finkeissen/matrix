from __future__ import annotations
import requests
from typing import Dict, List

class LmStudioOpenAICompatProvider:
    def __init__(self, *, base_url: str, api_key: str = "", timeout_seconds: int = 120):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout_seconds = timeout_seconds

    def chat(self, messages: List[Dict[str, str]], *, model: str, temperature: float, max_tokens: int) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=self.timeout_seconds)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
