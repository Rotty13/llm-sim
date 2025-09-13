###DO NOT USE THIS FILE### USE sim/llm/llm.py INSTEAD
# LLM client and related constants
from __future__ import annotations

import os
import json
import random
from re import S
from typing import Any, Dict, List, Optional
import numpy as np
import onnxruntime as ort



# Path to your ONNX model (update this after conversion)
ONNX_MODEL_PATH = os.environ.get(
    "ONNX_MODEL_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "onnx_model",
        "Meta-Llama-3.1-8B-Instruct-ONNX-INT4",
        "model.onnx"
    )
)

BELIEF_LOCK_SYSTEM = (
    "You are a human in a small city. You are not an AI. Stay in-world; "
    "never mention models/simulations."
)



class LLM:
    """TensorRT ONNX client for Llama3.1:8b-instruct-q4_0."""
    _shared_session = None
    _shared_onnx_path = None

    def __init__(self, onnx_path=ONNX_MODEL_PATH, temperature=0.5):
        self.onnx_path = onnx_path
        self.temperature = float(temperature)
        # Reuse session if possible
        if LLM._shared_session is None or LLM._shared_onnx_path != self.onnx_path:
            available_providers = ort.get_available_providers()
            if "CUDAExecutionProvider" in available_providers:
                providers = ["CUDAExecutionProvider"]
                try:
                    so = ort.SessionOptions()
                    # (optional) you can also reduce opt level if you want
                    so.graph_optimization_level =  ort.GraphOptimizationLevel.ORT_DISABLE_ALL

                    LLM._shared_session = ort.InferenceSession(path_or_bytes=self.onnx_path, sess_options=so, providers=providers)
                    LLM._shared_onnx_path = self.onnx_path
                except Exception as e:
                    raise RuntimeError(f"Failed to create InferenceSession: {e}")
            else:
                raise RuntimeError("CUDAExecutionProvider is not available. Please install onnxruntime-gpu and ensure your CUDA environment is set up.")
        self.session = LLM._shared_session

    def chat(self, prompt: str, system: str = BELIEF_LOCK_SYSTEM, max_tokens: int = 256, seed=1, fast=False) -> str:
        from transformers import AutoTokenizer
        local_tokenizer_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "onnx_model",
            "Meta-Llama-3.1-8B-Instruct-ONNX-INT4"
        )
        if os.path.exists(os.path.join(local_tokenizer_path, "tokenizer.json")):
            tokenizer = AutoTokenizer.from_pretrained(local_tokenizer_path)
        else:
            model_id = "nvidia/Meta-Llama-3.1-8B-Instruct-ONNX-INT4"
            tokenizer = AutoTokenizer.from_pretrained(model_id)
        input_text = system + "\n" + prompt
        inputs = tokenizer(input_text, return_tensors="np")
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        # Prepare ONNX inputs (add required keys)
        batch_size, seq_len = input_ids.shape
        # position_ids: usually arange(seq_len) for each batch, must be int64
        position_ids = np.arange(seq_len, dtype=np.int64).reshape(1, -1)
        # past_key_values: for first step, all zeros
        # The model expects 32 layers (for 8B), each with key and value (shape: [batch, num_heads, 0, head_dim])
        # For first step, past_key_values.*.key/value are zeros with shape [batch, num_heads, 0, head_dim]
        # We'll create empty arrays for each required input
        ort_inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "position_ids": position_ids,
        }
        # Add all required past_key_values.*.key/value as empty arrays
        num_layers = 32
        num_heads = 8  # from config.json: num_key_value_heads
        head_dim = 128  # typical for 8B
        for i in range(num_layers):
            ort_inputs[f"past_key_values.{i}.key"] = np.zeros((batch_size, num_heads, 0, head_dim), dtype=np.float16)
            ort_inputs[f"past_key_values.{i}.value"] = np.zeros((batch_size, num_heads, 0, head_dim), dtype=np.float16)

        # Run inference (single step for test)
        ort_outs = self.session.run(None, ort_inputs)

        # Postprocess output: assume ort_outs[0] is logits for next token
        logits = ort_outs[0]
        if not isinstance(logits, np.ndarray):
            logits = np.array(logits)
        if logits.ndim == 3:
            last_logits = logits[:, -1, :]
        elif logits.ndim == 2:
            last_logits = logits[0]
        else:
            last_logits = logits
        next_token_id = int(np.argmax(last_logits, axis=-1))
        generated_ids = input_ids.tolist()[0] + [next_token_id]
        response = tokenizer.decode(generated_ids, skip_special_tokens=True)
        return response.strip()

    def embed(self, text: str) -> List[float]:
        # Placeholder: you need a separate ONNX model for embeddings
        # Or use a compatible ONNX embedding model
        rnd = random.Random(hash(text) & 0xFFFFFFFF)
        return [rnd.uniform(-1, 1) for _ in range(64)]

# a singleton for convenience
llm = LLM()
