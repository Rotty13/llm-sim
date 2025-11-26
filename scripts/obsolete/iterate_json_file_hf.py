"""
Functional Purpose: Loads, saves, and iterates over JSON files, handling file naming and incremental saving.
Description: Manages JSON file I/O and uses LLM to process and improve JSON data.
Replaced by: iterate_data.py (consolidated)
"""
import json
import re
from click import prompt
from sim.llm.llm_ollama import LLM
import os

base_filepath = None
def load_json_file(relative_path):
    abs_path = os.path.join(os.getcwd(), relative_path)
    #detect number postfix in name and use the base name for saving
    #base name is everything before the last underscore followed by a number
    base, ext = os.path.splitext(abs_path)
    # Extract base name without number postfix
    filename = os.path.splitext(os.path.basename(abs_path))[0]
    # Find the last underscore followed by a number
    last_underscore = filename.rfind('_')
    if last_underscore != -1 and last_underscore + 1 < len(filename) and filename[last_underscore + 1:].isdigit():
        filename = filename[:last_underscore]
    global base_filepath
    base_filepath = os.path.join(os.path.dirname(abs_path), filename)

    abs_path = os.path.join(os.path.dirname(abs_path), base + ext)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(relative_path, data):
    # Save to a new file with incremental numbering to avoid overwriting using base_filename
    if base_filepath is None:
        num = 1
        max_num = 30
        while num <= max_num:
            #include relative base path in new path
            new_path = os.path.join(os.path.dirname(relative_path), f"{base}_{num}{ext}")
            if not os.path.exists(new_path):
                with open(new_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return
            num += 1
        raise RuntimeError(f"Could not save file: all {max_num} incremental files exist.")
    else:
        base = base_filepath
        ext = os.path.splitext(relative_path)[1]
        num = 1
        max_num = 30
        while num <= max_num:
            new_path = f"{base}_{num}{ext}"
            if not os.path.exists(new_path):
                with open(new_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return
            num += 1
        raise RuntimeError(f"Could not save file: all {max_num} incremental files exist.")


llm = LLM(gen_model="llama3.1:8b-instruct-q4_0", caller="iterate_json_file_hf")
llm.temperature = 0.9

def chat_json_with_improvement(json_data, system, max_tokens=4000, timeout=3000):
    # Use chat_json for structured output
    return llm.chat_json(json_data, system=system, max_tokens=max_tokens, timeout=timeout)

def is_fulfilled(response, system_prompt, initial_json, timeout=3000):
    judge_system = "You are a helpful assistant that determines if a response fulfills the user's request. Answer with 'yes' or 'no' followed by a short explanation in parentheses."
    judge_prompt = f"Does the following response fully fulfill the user's request and the initial JSON? Respond with 'yes' or 'no' followed by a short explanation in parentheses.\nInitial JSON:\n{json.dumps(initial_json, indent=2)}\nResponse:\n{json.dumps(response, indent=2)}\n"
    judgment = llm.chat(judge_prompt, system=judge_system, max_tokens=32, timeout=timeout)
    explanation = None
    if '(' in judgment and ')' in judgment:
        explanation = judgment[judgment.find('('):], judgment[judgment.find(')')+1:]
    return 'yes' in judgment.lower(), explanation

def try_attain_fulfillment_loop(response, system_prompt, initial_json, max_retries=3, timeout=3000):
    for attempt in range(max_retries):
        if is_fulfilled(response, system_prompt, initial_json, timeout=timeout)[0]:
            return response
        print(f"Attempt {attempt+1} to improve response for fulfillment.")
        improvement_prompt = f"The previous response did not fully meet the user's request. Please improve it.\nPrevious Response:\n{json.dumps(response, indent=2)}"
        response = chat_json_with_improvement(improvement_prompt, system_prompt, timeout=timeout)
    return response

def iterate_json_file_hf(relative_path, system_prompt, human_feedback=None, max_iterations=3):
    initial_json = load_json_file(relative_path)
    # Combine initial_json and human_feedback into a single text prompt
    if human_feedback and human_feedback.strip().lower() != "no user input" and human_feedback.strip() != "":
        combined_prompt = f"Here is the initial JSON data:\n{json.dumps(initial_json, indent=2)}\n\nHere is the human feedback for improvement:\n{human_feedback}"
    else:
        combined_prompt = f"Here is the initial JSON data:\n{json.dumps(initial_json, indent=2)}"
    
    prev_response = None
    for iteration in range(max_iterations):
        print(f"--- Iteration {iteration + 1} ---")
        if prev_response is None:
            response = chat_json_with_improvement(combined_prompt, system_prompt)
            print("Initial response:", json.dumps(response, indent=2, ensure_ascii=False))
            prev_response = response
            continue
        # For each iteration, combine previous response and human feedback
        if human_feedback and human_feedback.strip().lower() != "no user input" and human_feedback.strip() != "":
            iteration_prompt = f"Here is the previous improved JSON:\n{json.dumps(prev_response, indent=2)}\n\nHere is the human feedback for further improvement:\n{human_feedback}"
        else:
            iteration_prompt = f"Here is the previous improved JSON:\n{json.dumps(prev_response, indent=2)}"
        improved_response = chat_json_with_improvement(iteration_prompt, system_prompt)
        fulfillment, explanation = is_fulfilled(improved_response, system_prompt, initial_json)
        if fulfillment:
            print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
            print(json.dumps(improved_response, indent=2, ensure_ascii=False))
            prev_response = improved_response
            continue
        improved_response = try_attain_fulfillment_loop(improved_response, system_prompt, initial_json)
        fulfillment, explanation = is_fulfilled(improved_response, system_prompt, initial_json)
        if fulfillment:
            print(f"Request judged as fulfilled by LLM ({explanation if explanation else 'No explanation'})")
            print(json.dumps(improved_response, indent=2, ensure_ascii=False))
            prev_response = improved_response
            continue
        #print(json.dumps(improved_response, indent=2, ensure_ascii=False))
        #print out the diff between prev_response and improved_response as a percentage of text size change
        prev_size = len(json.dumps(prev_response))
        improved_size = len(json.dumps(improved_response))
        size_change = improved_size - prev_size
        size_change_pct = (size_change / prev_size) * 100 if prev_size > 0 else 0
        print(f"Size change from previous response: {size_change} bytes ({size_change_pct:.2f}%)")

        prev_response = improved_response
    print(f"Finished response improvement after {iteration+1} iterations.")
    save_json_file(relative_path, prev_response)
    return prev_response

if __name__ == "__main__":
    file_prompt = prompt("Enter the relative path to the JSON file", default="data/places/city_places.json")
    system_prompt = prompt("Enter a system prompt (optional)", default="You are a helpful assistant. Output only the improved JSON. Do not ask questions. If no changes are made, respond with the original JSON.")
    human_feedback = prompt("Enter your feedback for improvement (optional)", default="No user input")
    max_iterations = prompt("Enter max iterations (default 3)", default=3, type=int)
    final_response = iterate_json_file_hf(file_prompt, system_prompt, human_feedback=human_feedback, max_iterations=max_iterations)
    print("Final Improved JSON Response:\n", json.dumps(final_response, indent=2, ensure_ascii=False))
