
from __future__ import annotations
from sim.llm.ollama_schemas import GenerateRequest, ModelOptions

"""
llm_ollama.py

Legacy unified LLM client for the llm-sim simulation project. This module provides chat and embedding APIs using the Ollama backend, with additional logging and legacy interface support.

**Current Utility (Post-ollama_api.py):**
- This file implements a custom LLM client with logging, retry, and legacy interface logic, but duplicates much of the functionality now available in the more modular and type-safe OllamaAPI class (see ollama_api.py).
- The main differences are:
    - Custom logging to file and console for each request/response.
    - Legacy support for Llama.cpp and ONNX (now deprecated; all calls use Ollama).
    - Some custom retry/backoff and offline fallback logic.
    - Direct use of dict payloads, not Pydantic schemas.
- **If you need advanced logging, legacy support, or offline fallback, use this class. Otherwise, prefer OllamaAPI for new code.**

**Recommended Improvements/Integration:**
- [ ] Refactor to use OllamaAPI for all HTTP calls, passing Pydantic models for type safety.
- [ ] Move logging and retry logic into a shared utility or extend OllamaAPI.
- [ ] Remove legacy/unused code paths (e.g., Llama.cpp, ONNX references).
- [ ] Ensure all API calls use schema validation and error handling as in OllamaAPI.
- [ ] Consider merging this file into ollama_api.py for a single unified client.

CLI Arguments:
- None directly; LLM client is used by simulation modules and scripts.
"""


import sys
import time
import os
import random
import math
import logging
import uuid
from time import sleep
from typing import Optional, Any, Dict, List
import json
from .ollama_api import OllamaAPI
from .ollama_schemas import ChatRequest, ChatMessage, ModelOptions, EmbedRequest


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
GEN_MODEL  = os.environ.get("GEN_MODEL", "llama3.1:8b-instruct-q8_0")
GEN_MODEL_FAST  = os.environ.get("GEN_MODEL_FAST", "llama3.1:8b-instruct-q4_0")
EMB_MODEL  = os.environ.get("EMB_MODEL", "nomic-embed-text")



# generic ai assistant system prompt

AI_ASSISTANT_SYSTEM = (
    "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible."
)


# =========================
# LLM: Legacy Ollama Client
# =========================
#
# This class provides a custom Ollama client with logging, retry, and offline fallback logic.
# It is now largely superseded by OllamaAPI (see ollama_api.py), but still used for:
#   - Custom logging to file/console
#   - Legacy interface compatibility
#   - Offline fallback for embeddings
#   - Ad-hoc retry/backoff logic
#


class LLM:
    """
    Tiny Ollama client with graceful fallbacks for development and offline use.
    Provides chat and embedding APIs, with logging and retry logic.
    
    NOTE: Prefer using OllamaAPI for new code. This class is for legacy support and advanced logging only.
    """


    def __init__(self, base=OLLAMA_URL, gen_model=GEN_MODEL, emb_model=EMB_MODEL, temperature=0.8, caller: Optional[str] = None):
        self.base, self.gen_model, self.emb_model = base.rstrip("/"), gen_model, emb_model
        self.temperature = float(temperature)
        self.messages = None
        self.caller = caller
        self.ollama_api = OllamaAPI(base_url=self.base+"/api")
        



    # _get_timeout and _post removed; all API calls now use OllamaAPI

    def chat(self, prompt: str, system: str = AI_ASSISTANT_SYSTEM, max_tokens: int = 256, seed=1, messages: Optional[list] = None, timeout: int = 250) -> str:
        """
        Sends a chat prompt to the Ollama model and returns the generated response.
        Now uses OllamaAPI and Pydantic schemas for type safety.
        """
        msgs = messages.copy() if messages is not None else []
        msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        chat_messages = [ChatMessage(**m) for m in msgs]
        options = ModelOptions(temperature=self.temperature, seed=seed, num_ctx=4096)
        if max_tokens:
            options.num_predict = max_tokens
        req = ChatRequest(
            model=self.gen_model,
            messages=chat_messages,
            stream=False,
            options=options,
            keep_alive="30m"
        )
        resp = self.ollama_api.chat(req)
        txt = getattr(resp, "message", None)
        content = txt.content.strip() if txt and hasattr(txt, "content") else ""
        # logging removed
        return content



    #common token context lengths 2048, 4096, 8192, 16384, 32768 
    def chat_json(self, prompt: str, system: str = AI_ASSISTANT_SYSTEM, max_tokens: int = 256, seed=1, messages: Optional[list] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Sends a chat request to the Ollama API and returns the response as a JSON object.
        Now uses OllamaAPI and Pydantic schemas for type safety.
        """
        msgs = messages.copy() if messages is not None else []
        msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        chat_messages = [ChatMessage(**m) for m in msgs]
        options = ModelOptions(temperature=self.temperature, seed=seed, num_ctx=8192)
        if max_tokens:
            options.num_predict = max_tokens
        req = ChatRequest(
            model=self.gen_model,
            messages=chat_messages,
            stream=False,
            options=options,
            format="json",
            keep_alive="30m"
        )
        resp = self.ollama_api.chat(req)
        txt = getattr(resp, "message", None)
        content = txt.content.strip() if txt and hasattr(txt, "content") else ""
        # carve JSON
        s, e = content.find("{"), content.rfind("}")
        if s != -1 and e != -1:
            content = content[s:e+1]

        try:
            return json.loads(content)
        except Exception:
            return {"failedJSON": content}

    def embed(self, text: str, timeout: Optional[int] = 60) -> List[float]:
        """
        Requests an embedding for the given text from the Ollama API, or generates a deterministic pseudo-embedding offline.
        Handles both single string and list input, and robustly extracts the embedding from the EmbedResponse schema.
        """
        try:
            req = EmbedRequest(model=self.emb_model, input=text, keep_alive="30m")
            resp = self.ollama_api.embed(req)
            
            # resp should be an EmbedResponse with .embeddings as List[List[float]]
            embeddings = getattr(resp, "embeddings", None)
            if embeddings:
                # If input was a string, return the first embedding
                if isinstance(text, str):
                    return embeddings[0]
                # If input was a list, return the list of embeddings
                return embeddings
        except Exception:
            pass
        # Offline fallback: deterministic pseudo-embedding
        if isinstance(text, str):
            rnd = random.Random(hash(text) & 0xFFFFFFFF)
            return [rnd.uniform(-1, 1) for _ in range(64)]
        elif isinstance(text, list):
            return [[random.Random(hash(t) & 0xFFFFFFFF).uniform(-1, 1) for _ in range(64)] for t in text]
        else:
            return []


# =========================
# LLM_Convo: Stateful LLM Client
# =========================
#
# This class extends LLM to maintain a running message history (conversation state).
#

class LLM_Convo:
    """
    LLM_Convo is a wrapper around LLM that maintains a running message history for conversational context.
    """
    def __init__(self, caller: Optional[str] = None, **llm_kwargs):
        self.llm = LLM(caller=caller, **llm_kwargs)
        self.messages: List[ChatMessage] = []

    def clearmessages(self):
        """Clears the conversation history."""
        self.messages = []

    def chat(self, prompt: str, system: str = AI_ASSISTANT_SYSTEM, max_tokens: int = 256, seed=1, timeout: Optional[int] = None) -> str:
        """
        Sends a chat prompt using the running conversation history.
        Uses Pydantic ChatMessage objects for message history.
        """
        timeout = timeout or 60
        txt = self.llm.chat(
            prompt,
            system=system,
            max_tokens=max_tokens,
            seed=seed,
            messages=[m.dict() for m in self.messages],
            timeout=timeout
        )
        self.messages.append(ChatMessage(role="user", content=prompt))
        self.messages.append(ChatMessage(role="assistant", content=txt))
        return txt

    def chat_json(self, prompt: str, system: str = AI_ASSISTANT_SYSTEM, max_tokens: int = 256, seed=1, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Sends a chat prompt and returns the response as JSON, maintaining conversation history.
        Uses Pydantic ChatMessage objects for message history.
        """
        result = self.llm.chat_json(
            prompt,
            system=system,
            max_tokens=max_tokens,
            seed=seed,
            messages=[m.dict() for m in self.messages],
            timeout=timeout
        )
        self.messages.append(ChatMessage(role="user", content=prompt))
        self.messages.append(ChatMessage(role="assistant", content=json.dumps(result)))
        return result

