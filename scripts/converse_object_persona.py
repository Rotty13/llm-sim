
import argparse
import json
import os
import yaml
from sim.llm.llm_ollama import llm
chat_json = llm.chat_json



#Uses an llm(json) to chat with the personification of an object with the goal of extracting behaviour and interactions
def converse_with_object(object_name, persona,  prompt, system_prompt=None):
    """
    Uses an LLM to chat with the personification of an object.
    Args:
        object_name (str): Name of the object.
        persona (str): Persona description for the object.
        prompt (str): User prompt/question.
    Returns:
        dict: LLM response as structured JSON.
    """
    system_prompt = (
        f"Your name is {object_name} and you are a {persona}. "
        f"Your persona is {persona}. "
        " Respond with json only."
    )
    response = chat_json(prompt=prompt, system=system_prompt, max_tokens=2048)
    return response


def main():
    parser = argparse.ArgumentParser(description="Chat with the personification of an object.")
    parser.add_argument("--objectname", default="shovel", help="Name of the object to personify.")
    parser.add_argument("--persona", default="a shovel", help="Persona description for the object.")
    args = parser.parse_args()

    #object specification
    objectSpec: dict = {
        "objectname": args.objectname,
        "persona": args.persona
    }
    # Initial prompt (fix: use objectname)
    initial_prompt = (f"State your category and a brief description of your purpose. "
                      "Define your states, actions, and possible interactions with humans in JSON format.")


    # Step 1: Get initial object definition from LLM
    print("Sending initial prompt to LLM...")
    initial_response = converse_with_object(
        objectSpec["objectname"],
        objectSpec["persona"],
        initial_prompt
    )
    print("Initial LLM Response:", initial_response)

    # Try to update objectSpec with the LLM's response (assume dict or parse if string)
    if isinstance(initial_response, dict):
        objectSpec.update(initial_response)
    else:
        try:
            import json
            objectSpec.update(json.loads(initial_response))
        except Exception:
            objectSpec["llm_response_raw"] = initial_response


    # Step 2: Follow-up requests for more details (up to 3 times)
    for i in range(3):
        #Prompt giving current specification and requesting more details
        followup_prompt=(f"Based on the current specification: {objectSpec}, provide more details about your states, actions, and interactions. "
                        "Expand on any areas that seem underdeveloped or unclear. Respond in JSON format.")
        if not followup_prompt.strip():
            print("No follow-up prompt entered. Skipping.")
            continue
        followup_response = converse_with_object(
            objectSpec["objectname"],
            objectSpec["persona"],
            followup_prompt
        )
        print(f"LLM Follow-up Response #{i+1}:", followup_response)
        # Try to update objectSpec with the LLM's response
        if isinstance(followup_response, dict):
            objectSpec.update(followup_response)
        else:
            try:
                import json
                objectSpec.update(json.loads(followup_response))
            except Exception:
                objectSpec[f"llm_followup_raw_{i+1}"] = followup_response


    # Step 3: Save final objectSpec to YAML in ./data/
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'object')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{objectSpec['objectname']}_persona.yaml")
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(objectSpec, f, allow_unicode=True, sort_keys=False)
    print(f"Final objectSpec saved to {output_path}")

if __name__ == "__main__":
    main()