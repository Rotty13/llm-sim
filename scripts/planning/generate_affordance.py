"""
generate_affordance.py

Uses an LLM to generate and expand lists of action affordances for entities. Outputs affordances in structured JSON format for use in simulation environments.

Usage:
    python scripts/planning/generate_affordance.py
"""
from hmac import new
import re
from click import prompt
from sim.llm.llm_ollama import LLM  
import json

llm = LLM(caller="generate_affordance")
llm.temperature = 0.9


system_prompt_postfix = ('\nOutput as JSON only.\n'
                'Example:'
                '{"name": "chair", "affordances": {'
                '"move": "You can move the chair.",'
                '"sit": "You can sit on the chair.",'
                '...}}')
initial_system_prompt = 'You are to provide a list of action affordances for an entity.\n' + system_prompt_postfix
iteration_system_prompt = "You are to expand this list of affordances.\n" + system_prompt_postfix




initial_prompt = 'Provide a list of action affordances for a "{entity_name}".'
iteration_prompt = ("You are to expand this list of affordances.\n"                          
                                    "Iteration {iteration}:\n"
                                     "{last_response}\n")


def extract_json_from_response(response: str):
    if isinstance(response, dict):
        return response
    try:
        # Attempt to parse the entire response as JSON
        return json.loads(response)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from within the text
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def try_repair_json(brokenjson: str, iteration: int):
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

def chat_json_with_repair(prompt, system, max_tokens=4096, timeout=300, retries=3):
    response = llm.chat_json(prompt, system=system, max_tokens=max_tokens, timeout=timeout)
    if "failedjson" in response:
        brokenjson = response["failedjson"]
        for attempt in range(retries):
            result = try_repair_json(brokenjson, attempt)
            if result:
                if "failedjson" in result:
                    brokenjson = result.get("failedjson", brokenjson)
                else:
                    print(f"Repaired JSON in {attempt} attempts")
                    return result
        print(f"Failed to repair JSON after {retries} attempts.")
        return None
    return response

def valid_affordance_response(response):
    if not response or "affordances" not in response or not isinstance(response["affordances"], dict):
        return False
    for k, v in response["affordances"].items():
        if not isinstance(k, str) or not isinstance(v, str):
            return False
    return True


def generate_affordance(entity_name):
    accumulated_entity = {"name": entity_name, "affordances": {}}

    response = chat_json_with_repair(
        initial_prompt.format(entity_name=entity_name),
        system=initial_system_prompt,
        max_tokens=4096,
        timeout=300
    )
    if not response or not valid_affordance_response(response):
        print(f"Initial response failed due to unrepairable JSON.")
        return None
    print("Initial response:", response)
    accumulated_entity["affordances"].update(response["affordances"])

    def print_affordance_report(iteration=None):
        new_affordances = "\n".join([k for k, v in result["affordances"].items() if k not in accumulated_entity["affordances"]])
        if new_affordances:
            print(f"New affordances found in iteration {iteration}: {new_affordances}")
        else:
            print(f"No new affordances found in iteration {iteration}.")

    prev_response = None
    iterations = 3
    for iteration in range(iterations):
        print(f"--- Iteration {iteration + 1} ---")
        if prev_response:
            response = prev_response

        result = response
        if not result or not valid_affordance_response(result):
            print(f"Iteration {iteration} failed due to unformattable JSON.")
            continue
        
        print_affordance_report(iteration+1)

        accumulated_entity["affordances"].update(result["affordances"])

        prev_response = chat_json_with_repair(
            iteration_prompt.format(iteration=iteration + 1, last_response=json.dumps(accumulated_entity)),
            system=iteration_system_prompt,
            max_tokens=4096,
            timeout=300
        )
    print(f"Finished {entity_name} affordance generation with {iterations} iterations.")
    return accumulated_entity

    
if __name__ == "__main__":
    entity_name = prompt("Enter the entity name", default="chair")
    affordances = generate_affordance(entity_name)
    if affordances:
        print("Generated Affordances:", json.dumps(affordances, indent=2))
    #save data\entities\affordances
    with open(f"data/entities/affordances/{entity_name}_affordances.json", "w", encoding="utf-8") as f:
        json.dump(affordances, f, indent=2)