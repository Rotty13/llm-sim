"""
llm_json_tools.py
Purpose: Processes and reviews JSON files using LLM, saving improved or reviewed outputs.
Key Functions: process_json_with_llm, review_json_with_llm, load_json_file, save_json_file, save_review_file
LLM Usage: Uses LLM for JSON improvement and review.
"""

import json
import os
from click import prompt
from sim.llm.llm_ollama import LLM

llm = LLM(gen_model="llama3.1:8b-instruct-q4_0", caller="llm_json_tools")
llm.temperature = 0.9

def load_json_file(relative_path):
    abs_path = os.path.join(os.getcwd(), relative_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(output_path, data):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_review_file(review_text, reviewed_filename):
    output_dir = os.path.join(os.getcwd(), "outputs", "llm_data", "json_reviews")
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(reviewed_filename))[0]
    num = 1
    while True:
        out_path = os.path.join(output_dir, f"{base_name}_review_{num}.txt")
        if not os.path.exists(out_path):
            break
        num += 1
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Review of file: {reviewed_filename}\n\n")
        f.write(review_text)
    return out_path

def process_json_with_llm(json_data, user_prompt, system_prompt, max_tokens=4096, timeout=1000):
    combined_prompt = f"Here is the JSON data:\n{json.dumps(json_data, indent=2)}\n\nUser Prompt:\n{user_prompt}"
    return llm.chat_json(combined_prompt, system=system_prompt, max_tokens=max_tokens, timeout=timeout)

def review_json_with_llm(json_data, user_prompt, system_prompt=None, max_tokens=2048, timeout=180):
    review_prompt = f"You are to review the following JSON document based on the user's criteria.\n\nJSON Document:\n{json.dumps(json_data, indent=2)}\n\nReview Criteria / User Request:\n{user_prompt}\n\nPlease provide a detailed review, including strengths, weaknesses, and suggestions for improvement if relevant."
    if not system_prompt:
        system_prompt = "You are a helpful assistant. Output only the review. Do not modify the JSON."
    return llm.chat(review_prompt, system=system_prompt, max_tokens=max_tokens, timeout=timeout)

if __name__ == "__main__":
    mode = prompt("Choose mode (review/improve)", default="improve")
    rel_path = prompt("Enter the relative path to the JSON file", default="data/places/city_places.json")
    user_prompt = prompt("Enter your prompt or review criteria", default="Describe or improve the JSON.")
    system_prompt = prompt("Enter a system prompt (optional)", default="You are a helpful assistant. Output only the improved JSON or review.")
    output_path = prompt("Enter output path (optional)", default="")
    json_data = load_json_file(rel_path)
    if mode == "improve":
        improved_json = process_json_with_llm(json_data, user_prompt, system_prompt)
        if output_path.strip() == "":
            abs_path = os.path.join(os.getcwd(), rel_path)
            output_path = abs_path.replace('.json', '_improved.json')
        save_json_file(output_path, improved_json)
        print(f"Saved improved JSON to: {output_path}")
        print(json.dumps(improved_json, indent=2, ensure_ascii=False))
    else:
        review = review_json_with_llm(json_data, user_prompt, system_prompt)
        out_path = save_review_file(review, rel_path)
        print(f"\n--- JSON Review saved to {out_path} ---\n")
        print(review)
