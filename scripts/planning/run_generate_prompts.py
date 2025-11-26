"""
run_generate_prompts.py

Runs LLM-based prompt generation for all prompt files in a directory. Saves outputs to a specified directory, supporting both JSON and text formats.

Usage:
    python scripts/planning/run_generate_prompts.py
"""
import os
from sim.llm.llm_ollama import LLM

def get_prompt_files(prompt_dir):
    return [os.path.join(prompt_dir, f) for f in os.listdir(prompt_dir)
            if os.path.isfile(os.path.join(prompt_dir, f)) and f.endswith(('.txt', '.json'))]

def save_output(output, prompt_file, output_dir):
    base_name = os.path.splitext(os.path.basename(prompt_file))[0]
    ext = '.json' if output.strip().startswith('{') or output.strip().startswith('[') else '.txt'
    out_path = os.path.join(output_dir, f"{base_name}_output{ext}")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)
    return out_path

def main():
    prompt_dir = os.path.join(os.getcwd(), 'outputs', 'llm_data', 'prompts')
    output_dir = os.path.join(os.getcwd(), 'outputs', 'llm_data', 'prompts_outputs')
    os.makedirs(output_dir, exist_ok=True)
    llm = LLM(caller="run_generate_prompts")
    llm.temperature = 0.7
    prompt_files = get_prompt_files(prompt_dir)
    for prompt_file in prompt_files:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
        print(f"Running prompt: {prompt_file}")
    output = llm.chat(prompt_text, system="", max_tokens=8096, timeout=1000)
    out_path = save_output(output, prompt_file, output_dir)
    print(f"Saved output to: {out_path}")

if __name__ == "__main__":
    main()
