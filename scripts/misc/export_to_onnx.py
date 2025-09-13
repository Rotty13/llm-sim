from transformers import AutoTokenizer, AutoModelForCausalLM
from optimum.onnxruntime import ORTModelForCausalLM
import torch

model_id = "nvidia/Meta-Llama-3.1-8B-Instruct-ONNX-INT4"  # Replace with your model path or repo
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Export to ONNX
ort_model = ORTModelForCausalLM.from_pretrained(model_id, export=True)
ort_model.save_pretrained("./nvidia_Meta-Llama-3.1-8B-Instruct-ONNX-INT4")