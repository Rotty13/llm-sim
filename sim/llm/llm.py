# LLM client and related constants
from __future__ import annotations
import requests
import json
from typing import Optional
import os, json, requests, random
from typing import Any, Dict, List
import requests, json
import math

OLLAMA_URL = "http://localhost:11434"
GEN_MODEL = "llama3.1:8b-instruct-q4_0"
EMB_MODEL = "nomic-embed-text"

class OllamaClient:
    def __init__(self, base_url=OLLAMA_URL, gen_model=GEN_MODEL, emb_model=EMB_MODEL, temperature=0.5):
        self.base = base_url.rstrip("/")
        self.gen_model = gen_model
        self.emb_model = emb_model
        self.temperature = temperature

    def _get_timeout(self, payload, timeout):
        if timeout is not None:
            return timeout
        # Scale timeout with payload size, min 30s, max 300s
        size = len(json.dumps(payload))
        return min(30 + size // 100, 300)

    def generate(self, prompt: str, system: str = "", max_tokens: Optional[int] = None, timeout: Optional[int] = None) -> str:
        body = {
            "model": self.gen_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": 4096,
                "seed": 1,
                "repeat_penalty": 1.05,
            }
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        t = self._get_timeout(body, timeout)
        r = requests.post(f"{self.base}/api/chat", json=body, timeout=t)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    def generateJSON(self, prompt: str, system: str = "", max_tokens: Optional[int] = None, force_json: bool = True, timeout: Optional[int] = None) -> str:
        body = {
            "model": self.gen_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": 4096,
                "seed": 1,
                "repeat_penalty": 1.05,
            }
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        if force_json:
            body["format"] = "json"
        t = self._get_timeout(body, timeout)
        r = requests.post(f"{self.base}/api/chat", json=body, timeout=t)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    def embed(self, text: str, timeout: Optional[int] = None):
        payload = {"model": self.emb_model, "prompt": text}
        t = self._get_timeout(payload, timeout)
        r = requests.post(f"{self.base}/api/embeddings", json=payload, timeout=t)
        r.raise_for_status()
        return r.json()["embedding"]


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
GEN_MODEL  = os.environ.get("GEN_MODEL", "llama3.1:8b-instruct-q8_0")
GEN_MODEL_FAST  = os.environ.get("GEN_MODEL_FAST", "llama3.1:8b-instruct-q4_0")
EMB_MODEL  = os.environ.get("EMB_MODEL", "nomic-embed-text")

BELIEF_LOCK_SYSTEM = (
    "You are a human in a small city. You are not an AI. Stay in-world; "
    "never mention models/simulations."
)

class LLM:
    """Tiny Ollama client with graceful fallbacks for dev/offline use."""
    def __init__(self, base=OLLAMA_URL, gen_model=GEN_MODEL_FAST, emb_model=EMB_MODEL, temperature=0.5):
        self.base, self.gen_model, self.emb_model = base.rstrip("/"), gen_model, emb_model
        self.temperature = float(temperature)

    def _get_timeout(self, payload, timeout):
        if timeout is not None:
            return timeout
        size = len(json.dumps(payload))
        return min(30 + size // 100, 300)

    def _post(self, path: str, payload: dict, timeout: Optional[int] = None) -> dict:
        url = f"{self.base}{path}"
        t = self._get_timeout(payload, timeout)
        r = requests.post(url, json=payload, timeout=t)
        # Print raw body on non-200 so you can see Ollama's error text
        if r.status_code != 200:
            raise RuntimeError(f"Ollama {path} HTTP {r.status_code}: {r.text}")
        try:
            return r.json()
        except Exception as e:
            raise RuntimeError(f"Ollama {path} returned non-JSON: {r.text[:500]}") from e

    def chat(self, prompt: str, system: str = BELIEF_LOCK_SYSTEM, max_tokens: int = 256, seed=1, fast=False, timeout: Optional[int] = None) -> Dict[str, Any]:
        body = {
            "model": self.gen_model,
            "messages": [{"role":"system","content":system},{"role":"user","content":prompt}],
            "stream": False,
            "options": {"temperature": self.temperature, "seed": seed, "num_ctx": 4096,"repeat_penalty": 1.05,},
            "keep_alive": "30m",  # <-- keep model loaded
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        data = self._post("/api/chat", body, timeout=timeout)
        txt = (data.get("message") or {}).get("content", "").strip()
        return txt

    def chat_json(self, prompt: str, system: str = BELIEF_LOCK_SYSTEM, max_tokens: int = 256, seed=1, fast=False, timeout: Optional[int] = None) -> Dict[str, Any]:
        body = {
            "model": self.gen_model,
            "messages": [{"role":"system","content":system},{"role":"user","content":prompt}],
            "stream": False,
            "options": {"temperature": self.temperature, "seed": seed, "num_ctx": 4096},
            "format": "json",
            "keep_alive": "30m",  # <-- keep model loaded
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        data = self._post("/api/chat", body, timeout=timeout)
        txt = (data.get("message") or {}).get("content", "").strip()
        # carve JSON
        s, e = txt.find("{"), txt.rfind("}")
        if s != -1 and e != -1:
            txt = txt[s:e+1]
        try:
            return json.loads(txt)
        except Exception:
            # ultra-minimal fallback
            return {"failedJSON": txt}

    def embed(self, text: str, timeout: Optional[int] = None) -> List[float]:
        payload = {"model": self.emb_model, "prompt": text, "keep_alive":"30m"}
        data = self._post("/api/embeddings", payload, timeout=timeout)
        if "embedding" in data:
            return data["embedding"]
        # offline fallback: deterministic pseudo-embedding
        rnd = random.Random(hash(text) & 0xFFFFFFFF)
        return [rnd.uniform(-1, 1) for _ in range(64)]

# a singleton for convenience
llm = LLM()
