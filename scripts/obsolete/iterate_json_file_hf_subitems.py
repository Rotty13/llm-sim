"""
Functional Purpose: Iterates over subitems in JSON files, improving them with LLM and saving results incrementally.
Description: Loads JSON, processes subitems with LLM, and saves improved versions.
Replaced by: iterate_data.py (consolidated)
"""
import json
from click import prompt
from sim.llm.llm_ollama import LLM
import os

def load_json_file(relative_path):
    abs_path = os.path.join(os.getcwd(), relative_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(relative_path, data):
    abs_path = os.path.join(os.getcwd(), relative_path)
    base, ext = os.path.splitext(abs_path)
    num = 1
    max_num = 30
    while num <= max_num:
        new_path = f"{base}_subitems_{num}{ext}"
        if not os.path.exists(new_path):
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return
        num += 1
    raise RuntimeError(f"Could not save file: all {max_num} incremental files exist.")

llm = LLM(gen_model="llama3.1:8b-instruct-q4_0", caller="iterate_json_file_hf_subitems")
llm.temperature = 0.9

def chat_json_with_improvement(json_data, system, max_tokens=4000, timeout=1000):
    return llm.chat_json(json_data, system=system, max_tokens=max_tokens, timeout=timeout)

def is_fulfilled(response, system_prompt, initial_json):
    judge_system = "You are a helpful assistant that determines if a response fulfills the user's request. Answer with 'yes' or 'no' followed by a short explanation in parentheses."
    judge_prompt = f"Does the following response fully fulfill the user's request and the initial JSON? Respond with 'yes' or 'no' followed by a short explanation in parentheses.\nInitial JSON:\n{json.dumps(initial_json, indent=2)}\nResponse:\n{json.dumps(response, indent=2)}\n"
    judgment = llm.chat(judge_prompt, system=judge_system, max_tokens=32)
    explanation = None
    if '(' in judgment and ')' in judgment:
        explanation = judgment[judgment.find('('):], judgment[judgment.find(')')+1:]
    return 'yes' in judgment.lower(), explanation

def try_attain_fulfillment_loop(response, system_prompt, initial_json, max_retries=3):
    for attempt in range(max_retries):
        if is_fulfilled(response, system_prompt, initial_json)[0]:
            return response
        print(f"Attempt {attempt+1} to improve response for fulfillment.")
        improvement_prompt = f"The previous response did not fully meet the user's request. Please improve it.\nPrevious Response:\n{json.dumps(response, indent=2)}"
        response = chat_json_with_improvement(improvement_prompt, system_prompt)
    return response

def iterate_subitems(json_obj, subitem_key, system_prompt, human_feedback=None, max_iterations=3):
    improved_obj = json_obj.copy()
    subitems = json_obj.get(subitem_key, {})
    improved_subitems = {}
    for subname, subobj in subitems.items():
        print(f"Processing subitem: {subname}")
        # Prepare prompt for subobject
        if human_feedback and human_feedback.strip().lower() != "no user input" and human_feedback.strip() != "":
            combined_prompt = f"Here is the initial JSON data for {subname}:\n{json.dumps(subobj, indent=2)}\n\nHere is the human feedback for improvement:\n{human_feedback}"
        else:
            combined_prompt = f"Here is the initial JSON data for {subname}:\n{json.dumps(subobj, indent=2)}"
        response = chat_json_with_improvement(combined_prompt, system_prompt)
        print("Initial response:", json.dumps(response, indent=2, ensure_ascii=False))
        prev_response = response
        for iteration in range(max_iterations):
            print(f"--- Iteration {iteration + 1} for {subname} ---")
            if human_feedback and human_feedback.strip().lower() != "no user input" and human_feedback.strip() != "":
                iteration_prompt = f"Here is the previous improved JSON for {subname}:\n{json.dumps(prev_response, indent=2)}\n\nHere is the human feedback for further improvement:\n{human_feedback}"
            else:
                iteration_prompt = f"Here is the previous improved JSON for {subname}:\n{json.dumps(prev_response, indent=2)}"
            improved_response = chat_json_with_improvement(iteration_prompt, system_prompt)
            fulfillment, explanation = is_fulfilled(improved_response, system_prompt, subobj)
            if fulfillment:
                print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
                print(json.dumps(improved_response, indent=2, ensure_ascii=False))
                prev_response = improved_response
                continue
            improved_response = try_attain_fulfillment_loop(improved_response, system_prompt, subobj)
            fulfillment, explanation = is_fulfilled(improved_response, system_prompt, subobj)
            if fulfillment:
                print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
                print(json.dumps(improved_response, indent=2, ensure_ascii=False))
                prev_response = improved_response
                continue
            prev_size = len(json.dumps(prev_response))
            improved_size = len(json.dumps(improved_response))
            size_change = improved_size - prev_size
            size_change_pct = (size_change / prev_size) * 100 if prev_size > 0 else 0
            print(f"Size change from previous response: {size_change} bytes ({size_change_pct:.2f}%)")
            prev_response = improved_response
        improved_subitems[subname] = prev_response
    improved_obj[subitem_key] = improved_subitems
    return improved_obj

if __name__ == "__main__":
    file_prompt = prompt("Enter the relative path to the JSON file", default="data/places/city_places_1.json")
    subitem_path = prompt("Enter the JSON object path (e.g. 'Government Locations/*')", default="Government Locations/*")
    system_prompt = prompt("Enter a system prompt (optional)", default="You are a helpful assistant. Output only the improved JSON. Do not ask questions. If no changes are made, respond with the original JSON.")
    human_feedback = prompt("Enter your feedback for improvement (optional)", default="No user input")
    max_iterations = prompt("Enter max iterations (default 3)", default=3, type=int)
    json_obj = load_json_file(file_prompt)
    # Parse subitem_path for nested keys and wildcards
    def extract_nested(json_obj, path):
        """Extracts nested value and returns the parent structure around the subobject."""
        parts = path.split('/')
        current = json_obj
        for p in parts:
            if p == '*':
                # Wildcard: return all keys at this level
                return {k: current[k] for k in current}
            if isinstance(current, dict) and p in current:
                current = current[p]
            else:
                return None
        # Reconstruct parent structure
        def build_parent(parts, value):
            if not parts:
                return value
            return {parts[0]: build_parent(parts[1:], value)}
        return build_parent(parts, current)

    extracted_obj = extract_nested(json_obj, subitem_path)
    if extracted_obj is None:
        print(f"Could not find path: {subitem_path}")
        exit(1)
    # If the last part is a wildcard, iterate all keys at that level
    if subitem_path.endswith('/*'):
        parent_path = subitem_path[:-2]
        parent_obj = extract_nested(json_obj, parent_path)
        # Defensive: parent_obj must be a dict with one key (the parent)
        parent_key = parent_path.split('/')[-1]
        if parent_obj and isinstance(parent_obj, dict) and parent_key in parent_obj and isinstance(parent_obj[parent_key], dict):
            subitems = list(parent_obj[parent_key].keys())
            improved_obj = extract_nested(json_obj, parent_path)
            for subname in subitems:
                improved_subitem = iterate_subitems(parent_obj[parent_key], subname, system_prompt, human_feedback=human_feedback, max_iterations=max_iterations)[subname]
                improved_obj[parent_key][subname] = improved_subitem
            save_json_file(file_prompt, improved_obj)
            print("Final Improved JSON Object:\n", json.dumps(improved_obj, indent=2, ensure_ascii=False))
        else:
            print(f"Could not find parent path or subitems: {parent_path}")
            exit(1)
    else:
        # Single subobject
        improved_obj = extract_nested(json_obj, subitem_path)
        # If the extracted object is a dict with one top-level key, iterate that key
        if isinstance(improved_obj, dict) and len(improved_obj) == 1:
            top_key = list(improved_obj.keys())[0]
            improved_subitem = iterate_subitems(improved_obj, top_key, system_prompt, human_feedback=human_feedback, max_iterations=max_iterations)[top_key]
            improved_obj[top_key] = improved_subitem
        save_json_file(file_prompt, improved_obj)
        print("Final Improved JSON Object:\n", json.dumps(improved_obj, indent=2, ensure_ascii=False))
    improved_obj = iterate_subitems(json_obj, subitem_key, system_prompt, human_feedback=human_feedback, max_iterations=max_iterations)
    save_json_file(file_prompt, improved_obj)
    print("Final Improved JSON Object:\n", json.dumps(improved_obj, indent=2, ensure_ascii=False))
