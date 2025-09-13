###DO NOT USE THIS FILE### USE sim/llm/llm.py INSTEAD

"""
llm_llamacpp.py
A minimal wrapper to run Llama.cpp models directly from Python.
"""
import os

from llama_cpp import Llama


class LlamaCppLLM:
    def __init__(self, model_path, n_ctx=2048, n_threads=None, n_gpu_layers=0):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads or os.cpu_count()
        self.n_gpu_layers = n_gpu_layers
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_threads=self.n_threads,
            n_gpu_layers=self.n_gpu_layers
        )

    def generate(self, prompt, max_tokens=256, temperature=0.7, top_p=0.95):
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        return output

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Llama.cpp model directly.")
    parser.add_argument("--model", required=True, help="Path to GGUF model file.")
    parser.add_argument("--prompt", required=True, help="Prompt to send to the model.")
    parser.add_argument("--max_tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top_p", type=float, default=0.95)
    args = parser.parse_args()

    llm = LlamaCppLLM(args.model)
    result = llm.generate(
        args.prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p
    )
    print(result)



