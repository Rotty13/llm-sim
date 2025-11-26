"""
Functional Purpose: Reviews JSON files using LLM and saves review output.
Description: Loads JSON, generates review with LLM, and saves review text to file.
Replaced by: llm_json_tools.py (consolidated)
"""
import json
import os
from click import prompt
from sim.llm.llm_ollama import LLM

def load_json_file(relative_path):
    abs_path = os.path.join(os.getcwd(), relative_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_review_file(review_text, reviewed_filename):
    # Ensure output directory exists
    output_dir = os.path.join(os.getcwd(), "outputs", "llm_data", "json_reviews")
    os.makedirs(output_dir, exist_ok=True)
    # Find next available file name
    base_name = os.path.splitext(os.path.basename(reviewed_filename))[0]
    num = 1
    while True:
        out_path = os.path.join(output_dir, f"{base_name}_review_{num}.txt")
        if not os.path.exists(out_path):
            break
        num += 1
    # Write header and review
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Review of file: {reviewed_filename}\n\n")
        f.write(review_text)
    return out_path


llm = LLM(gen_model="llama3.1:8b-instruct-q4_0", caller="llm_json_file_review")
llm.temperature = 0.7

def review_json_with_llm(json_data, user_prompt, system_prompt=None, max_tokens=2048, timeout=180):
    # Combine JSON and user prompt into a single review prompt
    review_prompt = f"You are to review the following JSON document based on the user's criteria.\n\nJSON Document:\n{json.dumps(json_data, indent=2)}\n\nReview Criteria / User Request:\n{user_prompt}\n\nPlease provide a detailed review, including strengths, weaknesses, and suggestions for improvement if relevant."
    if not system_prompt:
        system_prompt = "You are a helpful assistant. Output only the review. Do not modify the JSON."
    return llm.chat(review_prompt, system=system_prompt, max_tokens=max_tokens, timeout=timeout)

if __name__ == "__main__":
    rel_path = prompt("Enter the relative path to the JSON file", default="data/places/city_places.json")
    user_prompt = prompt("Enter your review criteria or request", default="Review for completeness, clarity, and accuracy.")
    system_prompt = prompt("Enter a system prompt (optional)", default="You are a helpful assistant. Output only the review. Do not modify the JSON.")

    json_data = load_json_file(rel_path)
    review = review_json_with_llm(json_data, user_prompt, system_prompt)
    out_path = save_review_file(review, rel_path)
    print(f"\n--- JSON Review saved to {out_path} ---\n")
    print(review)
