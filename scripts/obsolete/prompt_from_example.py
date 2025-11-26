"""
Functional Purpose: Generates LLM prompts from example files for JSON generation.
Description: Reads example files, uses LLM to create generic prompts, and saves output.
Replaced by: generate_prompt.py (consolidated)
"""
import os
from click import prompt
from sim.llm.llm_ollama import LLM

def read_file_contents(rel_path):
    abs_path = os.path.join(os.getcwd(), rel_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_prompt_file(prompt_text, example_filename):
    output_dir = os.path.join(os.getcwd(), "outputs", "prompts")
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(example_filename))[0]
    num = 1
    while True:
        out_path = os.path.join(output_dir, f"{base_name}_prompt_{num}.txt")
        if not os.path.exists(out_path):
            break
        num += 1
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Prompt generated from file: {example_filename}\n\n")
        f.write(prompt_text)
    return out_path

llm = LLM(gen_model="llama3.1:8b-instruct-q4_0", caller="prompt_from_example")
llm.temperature = 0.7

def generate_prompt_with_llm(file_contents, user_input, max_tokens=8096, timeout=1000):
    llm_prompt = f"{file_contents}"
    system_prompt = f"You are a prompt engineer. You are to design a prompt for an LLM that can be used to generate a generic version of the given json example. Incorporate these user instructions carefully: {user_input}. Only output the prompt, do not include any explanations. Output prompt should always include a simple example."
    return llm.chat(llm_prompt, system=system_prompt, max_tokens=max_tokens, timeout=timeout)

if __name__ == "__main__":
    rel_path = prompt("Enter the relative path to the .json file", default="data/places/city_places.json")
    user_input = prompt("Enter additional user input for the prompt (optional)", default="")
    file_contents = read_file_contents(rel_path)
    prompt_text = generate_prompt_with_llm(file_contents, user_input)
    out_path = save_prompt_file(prompt_text, rel_path)
    print(f"\n--- Prompt saved to {out_path} ---\n")
    print(prompt_text)
