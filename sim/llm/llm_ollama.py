from __future__ import annotations
import sys
import time
from pyparsing import Opt
import requests
import json
from typing import Optional
import os, json, requests, random
from typing import Any, Dict, List
import requests, json
import math


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
GEN_MODEL  = os.environ.get("GEN_MODEL", "llama3.1:8b-instruct-q8_0")
GEN_MODEL_FAST  = os.environ.get("GEN_MODEL_FAST", "llama3.1:8b-instruct-q4_0")
EMB_MODEL  = os.environ.get("EMB_MODEL", "nomic-embed-text")

# generic ai assistant system prompt

AI_ASSISTANT_SYSTEM = (
    "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible."
)

class LLM:
    """ Tiny Ollama client with graceful fallbacks for development and offline use.
    This class provides methods to interact with Ollama's chat and embedding APIs, 
    including logging, timeout management, and fallback mechanisms for offline scenarios.
    Attributes:
        base (str): Base URL for the Ollama API.
        gen_model (str): Name of the generation model to use.
        emb_model (str): Name of the embedding model to use.
        temperature (float): Sampling temperature for generation.
        logfile (Optional[IO]): File object for logging interactions.
        messages (Optional[list]): Message history for chat context.
        caller (Optional[str]): Identifier for the caller, used in logging.
        last_system_prompt_logged (Optional[str]): Tracks last logged system prompt.
    Methods:
        initialize_logging(caller):
            Initializes logging directories and log file for the current caller and date.
        _get_timeout(payload, timeout):
            Determines the timeout for API requests based on payload size or user input.
        _post(path, payload, timeout=None):
            Sends a POST request to the Ollama API and returns the parsed JSON response.
        chat(prompt, system=AI_ASSISTANT_SYSTEM, max_tokens=256, seed=1, messages=None, timeout=None):
            Sends a chat prompt to the Ollama model and returns the generated response as a string.
        write_log_entry(system_prompt, prompt, txt, json):
            Writes a log entry for each chat interaction, including system prompt, user prompt, and model response.
        chat_json(prompt, system=AI_ASSISTANT_SYSTEM, max_tokens=256, seed=1, messages=None, timeout=None):
            Sends a chat prompt to the Ollama model and returns the response as a JSON object, with fallback for parsing errors.
        embed(text, timeout=None):
            Requests an embedding for the given text from the Ollama API, or generates a deterministic pseudo-embedding offline.
    """


    def __init__(self, base=OLLAMA_URL, gen_model=GEN_MODEL, emb_model=EMB_MODEL, temperature=0.8, caller: Optional[str] = None):
        self.base, self.gen_model, self.emb_model = base.rstrip("/"), gen_model, emb_model
        self.temperature = float(temperature)
        self.logfile = None
        self.messages = None
        self.caller = caller
        

    def initialize_logging(self, caller):
        logbasepath = "outputs\\llm_logs\\"
        
        #check if date folder exists, if not create it
        date = time.strftime("%Y-%m-%d")
        if not os.path.exists(logbasepath+"{date}\\".format(date=date)):
            os.makedirs(logbasepath+"{date}\\".format(date=date))
            print(f"Created log directory: {logbasepath}\\{date}\\")

        #check if caller folder exists, if not create it
        logfilepath = logbasepath + f"{date}\\{caller}\\"
        if not os.path.exists(logfilepath.format(date=date, caller=caller)):
            os.makedirs(logfilepath.format(date=date, caller=caller))
            print(f"Created log directory: {logfilepath.format(date=date, caller=caller)}")
        

        self.logfile=None
        try:
            path = None
            for tries in range(30):
                post = "" if tries==0 else f"_{tries}"
                logfilename = f"llm_log{post}.txt"
                path=logfilepath + logfilename
                if not os.path.exists(path):
                    break
 
            if path:
                self.logfile = open(path, "a", encoding="utf-8")
                
        except Exception as e:
            print(f"Error opening log file: {e}")
            self.logfile = None

        self.last_system_prompt_logged = None

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

    def chat(self, prompt: str, system: str = AI_ASSISTANT_SYSTEM, max_tokens: int = 256, seed=1, messages: Optional[list] = None, timeout: int = 250, log=True) -> str:
        """
        Sends a chat prompt to the Ollama model and returns the generated response.
        Args:
            prompt (str): The user prompt to send to the model.
            system (str, optional): The system message to set context for the assistant. Defaults to AI_ASSISTANT_SYSTEM.
            max_tokens (int, optional): Maximum number of tokens to generate in the response. Defaults to 256.
            seed (int, optional): Random seed for generation reproducibility. Defaults to 1.
            messages (Optional[list], optional): Previous message history for context. Defaults to None.
            timeout (Optional[int], optional): Timeout for the API request in seconds. Defaults to None.
        Returns:
            str: The generated response from the model.
        """
        # Compose message history
        msgs = messages.copy() if messages is not None else []

        # Always append system message if not present
        msgs.append({"role": "system", "content": system})

        # Append user prompt
        msgs.append({"role": "user", "content": prompt})

        body = {
            "model": self.gen_model,
            "messages": msgs,
            "stream": False,
            "options": {"temperature": self.temperature, "seed": seed, "num_ctx": 4096, "repeat_penalty": 1.05},
            "keep_alive": "30m",  # <-- keep model loaded
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        data = self._post("/api/chat", body, timeout=timeout)
        response=data.get("message")
        txt = (data.get("message") or {}).get("content", "").strip()
        if log:
            self.write_log_entry(system, prompt, txt, False)
        return txt

    def write_log_entry(self, system_prompt, prompt, txt, json):
        if self.caller and not self.logfile:
            self.initialize_logging(self.caller)
        if self.logfile:

            if system_prompt != self.last_system_prompt_logged:
                self.logfile.write(f"System: {system_prompt}\n\n")
                self.last_system_prompt_logged = system_prompt
            
            self.logfile.write(f"User: {prompt}\n\n")
            if json:
                self.logfile.write(f"LLM (JSON): {txt}\n\n")
            else:
                self.logfile.write(f"LLM: {txt}\n\n")

            self.logfile.write("="*40 + "\n\n\n\n")
            self.logfile.flush()

    #common token context lengths 2048, 4096, 8192, 16384, 32768 
    def chat_json(self, prompt: str, system: str = AI_ASSISTANT_SYSTEM, max_tokens: int = 256, seed=1, messages: Optional[list] = None, timeout: Optional[int] = None, log=True) -> Dict[str, Any]:
        """
        Sends a chat request to the Ollama API and returns the response as a JSON object.
        Args:
            prompt (str): The user's input prompt for the chat.
            system (str, optional): The system message to set the assistant's behavior. Defaults to AI_ASSISTANT_SYSTEM.
            max_tokens (int, optional): Maximum number of tokens to generate in the response. Defaults to 256.
            seed (int, optional): Random seed for generation. Defaults to 1.
            messages (Optional[list], optional): Previous message history for context. Defaults to None.
            timeout (Optional[int], optional): Timeout for the API request in seconds. Defaults to None.
        Returns:
            Dict[str, Any]: The parsed JSON response from the assistant. If parsing fails, returns a dict with the raw content under the "failedJSON" key.
        """
        # Compose message history
        msgs = messages.copy() if messages is not None else []

        # Always append system message if not present
        msgs.append({"role": "system", "content": system})

        # Append user prompt
        msgs.append({"role": "user", "content": prompt})

        body = {
            "model": self.gen_model,
            "messages": msgs,
            "stream": False,
            "options": {"temperature": self.temperature, "seed": seed, "num_ctx": 8192},
            "format": "json",
            "keep_alive": "30m",  # <-- keep model loaded
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        data = self._post("/api/chat", body, timeout=timeout)
        response=data.get("message")

        txt = (data.get("message") or {}).get("content", "").strip()
        # carve JSON
        s, e = txt.find("{"), txt.rfind("}")
        if s != -1 and e != -1:
            txt = txt[s:e+1]
        if log:
            self.write_log_entry(system, prompt, txt, True)
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

#copy above class
class LLM_Convo(LLM):
    def __init__(self,  caller: Optional[str] = None):
        super().__init__(caller=caller)
        self.messages = []

    def clearmessages(self):
        self.messages = []

    def chat(self, prompt: str, system: str = AI_ASSISTANT_SYSTEM, max_tokens: int = 256, seed=1, timeout: Optional[int] = None) -> str:
        # Compose message history
        msgs = self.messages
        txt = super().chat(prompt, system=system, max_tokens=max_tokens, seed=seed, messages=msgs, timeout=timeout)
        msgs.append({"role": "user", "content": prompt})
        msgs.append({"role": "assistant", "content": txt})
        return txt

    def chat_json(self, prompt: str, system: str = AI_ASSISTANT_SYSTEM, max_tokens: int = 256, seed=1, timeout: Optional[int] = None) -> Dict[str, Any]:
        msgs = self.messages
        result = super().chat_json(prompt, system=system, max_tokens=max_tokens, seed=seed, messages=msgs, timeout=timeout)
        msgs.append({"role": "user", "content": prompt})
        msgs.append({"role": "assistant", "content": json.dumps(result)})
        return result

