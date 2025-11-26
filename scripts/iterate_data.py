"""
iterate_data.py
Purpose: Iterates and improves JSON/text data using LLM, with robust repair and fulfillment logic.
Key Functions: chat_with_improvement, chat_json_with_improvement, extract_json_from_response, try_repair_json, iterate_data, iterate_subitems
LLM Usage: Uses LLM for iterative improvement and repair of data.
"""

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

def try_repair_json(brokenjson: str, retries: int = 3):
    system_prompt_postfix = '\nOutput as JSON only.'
    repair_system_prompt = "You are to repair JSON into valid JSON format.\n" + system_prompt_postfix + "\n"
    repair_prompt = "Repair the following JSON into valid JSON format.\n"
    for tries in range(retries):
        result = llm.chat_json(repair_prompt + brokenjson, system=repair_system_prompt, max_tokens=4096, timeout=300)
        if "failedjson" in result:
            brokenjson = result["failedjson"]
            continue
        if result:
            return result
    return None
import json
import re
import os
from click import prompt
from sim.llm.llm_ollama import LLM

llm = LLM(gen_model="llama3.1:8b-instruct-q4_0", caller="iterate_data")
llm.temperature = 0.9

def load_json_file(relative_path):
    abs_path = os.path.join(os.getcwd(), relative_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(output_path, data):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_incremental_path(base_path, suffix="", max_num=30):
    base, ext = os.path.splitext(base_path)
    num = 1
    while num <= max_num:
        new_path = f"{base}{suffix}_{num}{ext}"
        if not os.path.exists(new_path):
            return new_path
        num += 1
    raise RuntimeError(f"Could not save file: all {max_num} incremental files exist.")

def chat_with_improvement(prompt_text, system, max_tokens=4096, timeout=300):
    return llm.chat(prompt_text, system=system, max_tokens=max_tokens, timeout=timeout)

def chat_json_with_improvement(json_data, system, max_tokens=4096, timeout=300):
    return llm.chat_json(json_data, system=system, max_tokens=max_tokens, timeout=timeout)

def is_fulfilled(response, system_prompt, initial):
    judge_system = "You are a helpful assistant that determines if a response fulfills the user's request. Answer with 'yes' or 'no' followed by a short explanation in parentheses."
    judge_prompt = f"Does the following response fully fulfill the user's request and the initial input? Respond with 'yes' or 'no' followed by a short explanation in parentheses.\nInitial Input:\n{json.dumps(initial, indent=2) if isinstance(initial, dict) else initial}\nResponse:\n{json.dumps(response, indent=2) if isinstance(response, dict) else response}\n"
    judgment = llm.chat(judge_prompt, system=judge_system, max_tokens=32)
    explanation = None
    if '(' in judgment and ')' in judgment:
        explanation = judgment[judgment.find('('):], judgment[judgment.find(')')+1:]
    return 'yes' in judgment.lower(), explanation

def try_attain_fulfillment_loop(response, system_prompt, initial, max_retries=3):
    for attempt in range(max_retries):
        if is_fulfilled(response, system_prompt, initial)[0]:
            return response
        print(f"Attempt {attempt+1} to improve response for fulfillment.")
        improvement_prompt = f"The previous response did not fully meet the user's request. Please improve it.\nPrevious Response:\n{json.dumps(response, indent=2) if isinstance(response, dict) else response}"
        response = chat_with_improvement(improvement_prompt, system_prompt)
    return response

def iterate_data(initial, system_prompt, iterations=3, mode="json", human_feedback=None, subitem_key=None):
    prev_response = initial
    for iteration in range(iterations):
        print(f"--- Iteration {iteration + 1} ---")
        if human_feedback:
            iteration_prompt = f"Improve the following data based on user feedback.\nIteration {iteration+1}:\n{human_feedback}\nData:\n{json.dumps(prev_response, indent=2) if mode == 'json' else prev_response}"
        else:
            iteration_prompt = f"Improve and expand the following data.\nIteration {iteration+1}:\n{json.dumps(prev_response, indent=2) if mode == 'json' else prev_response}"
        if mode == "json":
            improved_response = chat_json_with_improvement(prev_response, system_prompt)
        else:
            improved_response = chat_with_improvement(iteration_prompt, system_prompt)
        fulfillment, explanation = is_fulfilled(improved_response, system_prompt, initial)
        if fulfillment:
            print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
            prev_response = improved_response
            continue
        improved_response = try_attain_fulfillment_loop(improved_response, system_prompt, initial)
        fulfillment, explanation = is_fulfilled(improved_response, system_prompt, initial)
        if fulfillment:
            print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
            prev_response = improved_response
            continue
        print(improved_response)
        prev_response = improved_response
    print(f"Finished improvement after {iterations} iterations.")
    return prev_response

def iterate_subitems(json_obj, subitem_key, system_prompt, human_feedback=None, iterations=3):
    improved_obj = json_obj.copy()
    subitems = json_obj.get(subitem_key, {})
    improved_subitems = {}
    for subname, subobj in subitems.items():
        print(f"Processing subitem: {subname}")
        combined_prompt = f"Here is the initial JSON data for {subname}:\n{json.dumps(subobj, indent=2)}"
        if human_feedback:
            combined_prompt += f"\nHuman feedback: {human_feedback}"
        response = chat_json_with_improvement(combined_prompt, system_prompt)
        print("Initial response:", json.dumps(response, indent=2, ensure_ascii=False))
        prev_response = response
        for iteration in range(iterations):
            print(f"--- Iteration {iteration + 1} for {subname} ---")
            iteration_prompt = f"Improve the following subitem.\nIteration {iteration+1}:\n{json.dumps(prev_response, indent=2)}"
            improved_response = chat_json_with_improvement(iteration_prompt, system_prompt)
            fulfillment, explanation = is_fulfilled(improved_response, system_prompt, subobj)
            if fulfillment:
                print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
                prev_response = improved_response
                continue
            improved_response = try_attain_fulfillment_loop(improved_response, system_prompt, subobj)
            fulfillment, explanation = is_fulfilled(improved_response, system_prompt, subobj)
            if fulfillment:
                print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
                prev_response = improved_response
                continue
            print(improved_response)
            prev_response = improved_response
        improved_subitems[subname] = prev_response
    improved_obj[subitem_key] = improved_subitems
    return improved_obj

if __name__ == "__main__":
    mode = prompt("Choose mode (json/text)", default="json")
    rel_path = prompt("Enter the relative path to the file", default="data/places/city_places.json")
    system_prompt = prompt("Enter a system prompt", default="You are a helpful assistant. Output only the improved data.")
    iterations = int(prompt("Number of iterations", default="3"))
    human_feedback = prompt("Enter human feedback (optional)", default=None)
    subitem_key = prompt("Enter subitem key (optional)", default=None)
    if mode == "json":
        initial = load_json_file(rel_path)
        if subitem_key:
            improved = iterate_subitems(initial, subitem_key, system_prompt, human_feedback, iterations)
        else:
            improved = iterate_data(initial, system_prompt, iterations, mode, human_feedback)
        output_path = get_incremental_path(os.path.join(os.getcwd(), rel_path))
        save_json_file(output_path, improved)
        print(f"Saved improved JSON to: {output_path}")
    else:
        initial = prompt("Enter initial text", default="Describe the process of photosynthesis.")
        improved = iterate_data(initial, system_prompt, iterations, mode, human_feedback)
        print("Final Improved Text:\n", improved)
