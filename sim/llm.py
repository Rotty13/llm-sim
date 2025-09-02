# LLM client and related constants
import requests
import json

OLLAMA_URL = "http://localhost:11434"
GEN_MODEL = "llama3.1:8b-instruct-q8_0"
EMB_MODEL = "nomic-embed-text"

class OllamaClient:
    def __init__(self, base_url=OLLAMA_URL, gen_model=GEN_MODEL, emb_model=EMB_MODEL, temperature=0.5):
        self.base = base_url.rstrip("/")
        self.gen_model = gen_model
        self.emb_model = emb_model
        self.temperature = temperature

    def generate(self, prompt: str, system: str = "", max_tokens: int = None) -> str:
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
        r = requests.post(f"{self.base}/api/chat", json=body, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    def generateJSON(self, prompt: str, system: str = "", max_tokens: int = None, force_json: bool = True) -> str:
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
        r = requests.post(f"{self.base}/api/chat", json=body, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    def embed(self, text: str):
        r = requests.post(f"{self.base}/api/embeddings", json={"model": self.emb_model, "prompt": text}, timeout=120)
        r.raise_for_status()
        return r.json()["embedding"]
from __future__ import annotations
import os, json, requests, random
from typing import Any, Dict, List
import requests, json

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


    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base}{path}"
        r = requests.post(url, json=payload, timeout=30)
        # Print raw body on non-200 so you can see Ollama's error text
        if r.status_code != 200:
            raise RuntimeError(f"Ollama {path} HTTP {r.status_code}: {r.text}")
        try:
            return r.json()
        except Exception as e:
            raise RuntimeError(f"Ollama {path} returned non-JSON: {r.text[:500]}") from e

    def chat(self, prompt: str, system: str = BELIEF_LOCK_SYSTEM, max_tokens: int = 256, seed=1, fast=False) -> Dict[str, Any]:
        body = {
            "model": self.gen_model,
            "messages": [{"role":"system","content":system},{"role":"user","content":prompt}],
            "stream": False,
            "options": {"temperature": self.temperature, "seed": seed, "num_ctx": 4096,"repeat_penalty": 1.05,},
            "keep_alive": "30m",  # <-- keep model loaded
        }
        data = self._post("/api/chat", body)
        txt = (data.get("message") or {}).get("content", "").strip()
        return txt
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        r = requests.post(f"{self.base}/api/chat", json=body, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    def chat_json(self, prompt: str, system: str = BELIEF_LOCK_SYSTEM, max_tokens: int = 256, seed=1, fast=False) -> Dict[str, Any]:
        body = {
            "model": self.gen_model,
            "messages": [{"role":"system","content":system},{"role":"user","content":prompt}],
            "stream": False,
            "options": {"temperature": self.temperature, "seed": seed, "num_ctx": 4096},
            "format": "json",
            "keep_alive": "30m",  # <-- keep model loaded
        }
        data = self._post("/api/chat", body)
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

    def embed(self, text: str) -> List[float]:
        data = self._post("/api/embeddings", {"model": self.emb_model, "prompt": text, "keep_alive":"30m"})
        if "embedding" in data:
            return data["embedding"]
        # offline fallback: deterministic pseudo-embedding
        rnd = random.Random(hash(text) & 0xFFFFFFFF)
        return [rnd.uniform(-1, 1) for _ in range(64)]

# a singleton for convenience
llm = LLM()
