import json
import os
from click import prompt
from sim.llm.llm_ollama import LLM

def load_json_file(relative_path):
    abs_path = os.path.join(os.getcwd(), relative_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(output_path, data):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_incremental_path(base_path, max_num=30):
    base, ext = os.path.splitext(base_path)
    num = 1
    while num <= max_num:
        new_path = f"{base}_{num}{ext}"
        if not os.path.exists(new_path):
            return new_path
        num += 1
    raise RuntimeError(f"Could not save file: all {max_num} incremental files exist.")

llm = LLM(caller="llm_json_file")
llm.temperature = 0.9

def process_json_with_llm(json_data, user_prompt, system_prompt, max_tokens=4096, timeout=1000):
    # Combine JSON and user prompt into a single text prompt
    combined_prompt = f"Here is the JSON data:\n{json.dumps(json_data, indent=2)}\n\nUser Prompt:\n{user_prompt}"
    return llm.chat_json(combined_prompt, system=system_prompt, max_tokens=max_tokens, timeout=timeout)

if __name__ == "__main__":
    rel_path = prompt("Enter the relative path to the JSON file", default="data/places/city_places.json")
    user_prompt = prompt("Enter your prompt for the LLM", default="Describe or improve the JSON.")
    system_prompt = prompt("Enter a system prompt (optional)", default="You are a helpful assistant. Output only the improved JSON. Do not ask questions. If no changes are made, respond with the original JSON.")
    output_path = prompt("Enter output path (optional)", default="")

    json_data = load_json_file(rel_path)
    improved_json = process_json_with_llm(json_data, user_prompt, system_prompt)

    if output_path.strip() == "":
        abs_path = os.path.join(os.getcwd(), rel_path)
        output_path = get_incremental_path(abs_path)

    save_json_file(output_path, improved_json)
    print(f"Saved improved JSON to: {output_path}")
    print(json.dumps(improved_json, indent=2, ensure_ascii=False))
