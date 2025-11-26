"""
Functional Purpose: Iterates over JSON responses, attempts to extract and repair malformed JSON using LLM.
Description: Provides functions to extract JSON from LLM responses, repair broken JSON, and retry extraction using LLM chat.
Replaced by: iterate_data.py (consolidated)
"""
import re
import json
from click import prompt
from sim.llm.llm_ollama import LLM

llm = LLM(gen_model="llama3.1:8b-instruct-q4_0", caller="iterate_json")
llm.temperature = 0.9

def extract_json_from_response(response: str):
    if isinstance(response, dict):
        return response
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                return None
    return None

def try_repair_json(brokenjson: str, iteration: int):
    system_prompt_postfix = '\nOutput as JSON only.'
    repair_system_prompt = "You are to repair JSON into valid JSON format.\n" + system_prompt_postfix + "\n"
    repair_prompt = "Repair the following JSON into valid JSON format.\n"
    retries = 3
    for tries in range(retries):
        result = llm.chat_json(repair_prompt + brokenjson, system=repair_system_prompt, max_tokens=4096, timeout=300)
        if "failedjson" in result:
            brokenjson = result["failedjson"]
            continue
        if result:
            return result
    return None

def chat_json_with_repair(prompt_text, system, max_tokens=4096, timeout=300, retries=3):
    response = llm.chat_json(prompt_text, system=system, max_tokens=max_tokens, timeout=timeout)
    if "failedjson" in response:
        brokenjson = response["failedjson"]
        for attempt in range(retries):
            result = try_repair_json(brokenjson, attempt)
            if result:
                if "failedjson" in result:
                    brokenjson = result.get("failedjson", brokenjson)
                else:
                    print(f"Repaired JSON in {attempt+1} attempts")
                    return result
        print(f"Failed to repair JSON after {retries} attempts.")
        return None
    return response

def iterate_json(initial_prompt, system_prompt, iterations=3):
    response = chat_json_with_repair(initial_prompt, system_prompt)
    print("Initial response:", json.dumps(response, indent=2) if response else response)
    prev_response = response
    for iteration in range(iterations):
        print(f"--- Iteration {iteration + 1} ---")
        prev_json_str = json.dumps(prev_response, indent=2) if prev_response else ""
        iteration_prompt = (f"You are to improve and expand the following JSON response.\nIteration {iteration+1}:\n{prev_json_str}\n")
        improved_response = chat_json_with_repair(iteration_prompt, system_prompt)
        if improved_response and improved_response != prev_response:
            old_len = len(prev_json_str)
            new_json_str = json.dumps(improved_response, indent=2) if improved_response else ""
            new_len = len(new_json_str)
            delta = new_len - old_len
            percent = ((delta / old_len) * 100) if old_len else 0
            print(f"New improvements found in iteration {iteration+1}. Change ({percent:.1f}%)")
            prev_response = improved_response
        else:
            print(f"No new improvements found in iteration {iteration+1}.")
    print(f"Finished JSON improvement with {iterations} iterations.")
    return prev_response

if __name__ == "__main__":
    user_prompt = prompt("Enter your prompt", default="Provide a JSON object describing a person.")
    system_prompt = prompt("Enter a system prompt (optional)", default="You are a helpful assistant. Output only valid JSON.")
    final_response = iterate_json(user_prompt, system_prompt)
    print("Final Improved JSON Response:\n", json.dumps(final_response, indent=2) if final_response else final_response)
