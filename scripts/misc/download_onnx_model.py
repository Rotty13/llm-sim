"""
download_onnx_model.py

Downloads ONNX model files and related configuration from Hugging Face Hub for LLM inference. Used to set up local ONNX models for accelerated inference.

Usage:
    python scripts/misc/download_onnx_model.py
"""
from huggingface_hub import hf_hub_download
from huggingface_hub import hf_hub_download
import os

# Model repo and files
repo_id = "nvidia/Meta-Llama-3.1-8B-Instruct-ONNX-INT4"
files = [
    "model_int4.onnx",  # main ONNX model file
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "special_tokens_map.json"
]

output_dir = "onnx_model"
os.makedirs(output_dir, exist_ok=True)

for filename in files:
    print(f"Downloading {filename}...")
    hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=output_dir,
        local_dir_use_symlinks=False
    )
print("All files downloaded to ./onnx_model/")
