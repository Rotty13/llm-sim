"""
city_planner_json_collab.py

A collaborative script with three LLM personas:
- City Planner: Designs city structure and features.
- Agent Simulator Designer: Advises on simulation requirements and agent population.
- NL-to-JSON Agent: Converts natural language city descriptions into structured JSON.

Usage:
    python city_planner_json_collab.py --city_desc "A coastal city with parks, schools, and a bustling downtown."

The City Planner and Simulator Designer discuss and refine the city plan, then the NL-to-JSON Agent generates the JSON representation.
"""

import json
import click
from numpy import full


# Actual LLM chat implementation using llm.chat_json

# Import LLM and instantiate if needed
from sim.llm.llm_ollama import LLM

llm = LLM(caller="city_planner_json_collab")
llm.temperature = 0.9



def llm_chat(persona, message, context=None, messages=None, max_tokens=8192):
    """Call LLM with persona and message, return response text. Supports messages for context."""
    if persona == "city_planner":
        system_prompt = (
            "You are an expert City Planner\n"
            "Goal: Provide city planning information. Do not include people or agent details."
            "Answer the question directly in a natural manner in short responses. Condensed responses are preferred. 3 sentences max." 
        )
        prompt_str = message
        prompt_str += "\nAnswer the question directly in a natural manner in short responses. Condensed responses are preferred. 3 sentences max."
        llm.temperature = 0.7
        response = llm.chat(prompt_str, system=system_prompt, max_tokens=max_tokens, timeout=120, messages=messages)
        return str(response)
    elif persona == "simulator_designer":
        system_prompt = (
            "You are the expert Simulation Designer. Your goal is to create a simulation-ready, condensed, structured representation of the city described below. "
            "Goal: convert the city description into a representation fit for text based agent simulation focusing on verisimilitude, focusing on places, zones, infrastructure, and features, but excluding any people or agent population. Keep the output concise and structured. "
            
        )
        prompt_str = (
            "You must output your new city representation after the line '#representation'. "
            "Refine the city representation based on the original description and any new context.\n"
            "You must output your new city representation after the line '#representation'. "
            "Self-iterate and refine your design. "
            "If self-iterating, only output the new representation after '#representation'. "
            "Only gather information from the City Planner. "
            "If you want more information about the city, ask the City Planner a single specific question. "
            "If you do not need more information, continue refining your representation. "
            "Format as follows: #City Planner|What is the name of the city? "
            "#representation and #City Planner| should not appear in the same response. "
            "Only output #representation or #City Planner|question. "
            "Don't repeat previously asked questions. Ask a variety of questions."
        )
        if message:
            prompt_str = str(message)
        if context:
            prompt_str += f"\nContext: {context}"
        llm.temperature = 0.6
        response = llm.chat(prompt_str, system=system_prompt, max_tokens=max_tokens, timeout=120, messages=messages)
        return str(response)
    elif persona == "nl_to_json":
        system_prompt = (
            "You are an expert NL-to-JSON Agent\n"
            "Goal: Convert structured city descriptions into valid JSON objects. use doublequotes Do not include any people or agent population." \
            "Output strictly in JSON format." \
            "Do not include any explanations or text outside the JSON." \
        )
        prompt_str = f"City Representation: {message}"
        if context:
            prompt_str += f"\nContext: {context}"
        llm.temperature = 0.2
        response = llm.chat_json(prompt_str, system=system_prompt, max_tokens=2*8192, timeout=2*120)
        if isinstance(response, dict):
            return response.get("text") or response.get("json") or str(response)
        return str(response)
    else:
        # fallback
        system_prompt = f"Persona: {persona}"
        prompt_str = f"Message: {message}"
        if context:
            prompt_str += f"\nContext: {context}"
        response = llm.chat(prompt_str, system=system_prompt, messages=messages)
        return str(response)



@click.command()

def main():
    """Collaborative city planner with LLM personas."""
    city_desc = click.prompt('Enter a description of the city', type=str)




    # Simulation Designer is the director, self-iterates, asks City Planner if needed
    designer_context = None
    designer_representation = None
    planner_msg = None
    user_city_desc = city_desc


    # Maintain message history for designer and planner
    designer_questions = []
    planner_history = []
    for i in range(10):
        # Inject persistent representation before other instructions
        persistent_rep = designer_representation if designer_representation else user_city_desc

        # Build designer messages, prepending previous questions as assistant role messages
        messages = []
        if designer_questions:
            # Prepend each previous question as an assistant message
            for q in designer_questions:
                messages.append({"role": "assistant", "content": f"Previously asked: {q}"})
        # Add current representation
        messages.append({"role": "assistant", "content": f"current representation:\n{persistent_rep}\n"})
        if designer_context:
            messages.append({"role": "user", "content": designer_context})

        # Director asks itself if it needs more info
        need_info_prompt = (
            "Given the current city representation, do you need more information from the City Planner to improve the simulation design? Answer 'yes' or 'no'."
        )
        need_info_response = llm_chat("simulator_designer", need_info_prompt, max_tokens=250, messages=messages)
        need_info = need_info_response.strip().lower()
        if need_info.startswith("yes"):
            # Ask a specific question to the city planner
            ask_question_prompt = (
                "What is the most important missing detail you need from the City Planner to improve the simulation design? Phrase as a direct question."
            )
            designer_question = llm_chat("simulator_designer", ask_question_prompt, messages=messages)
            designer_output = f"#City Planner|{designer_question.strip()}"

            # Check if designer asked a question to the city planner
            question = None
            split_tokens = ["#City Planner|"]
            for token in split_tokens:
                if token in designer_output:
                    question = designer_output.split(token,1)[-1].strip()
                    question = question.split("?")[0].strip()  # Take up to the question mark
                    question += "?"  # Add back the question mark
                    break
            if question:
                designer_questions.append(question)
                print(f"[Simulation Designer, round {i+1}]:", f"#City Planner|{question}")
                planner_messages = []
                planner_messages.append({"role": "user", "content": "Base description of the city: " + user_city_desc})
                planner_messages.extend(planner_history)
                # Planner keeps full chat history
                planner_history.append({"role": "user", "content": question})
                planner_msg = llm_chat("city_planner", question, messages=planner_messages, max_tokens=250)
                planner_history.append({"role": "assistant", "content": planner_msg})
                print(f"[City Planner, round {i+1}]:", planner_msg)
                designer_context = planner_msg
            else:
                designer_context = None
                print(f"[City Planner, round {i+1}]:", designer_output)
        else:
            # Refine current representation
            refine_prompt = (
                "Output a refined representation after '#representation'."
            )
            designer_output = llm_chat("simulator_designer", refine_prompt, messages=messages)
            # Extract the updated representation from designer_output
            # Use only the content after '#representation'
            rep_token = "#representation"
            if rep_token in designer_output:
                designer_representation = designer_output.split(rep_token,1)[-1].strip()
                print(f"[Simulation Designer, round {i+1}]:", designer_representation)
            else:
                designer_context = None
                print(f"[City Planner, round {i+1}]:", designer_output)

        


    # NL-to-JSON Agent converts to JSON
    json_output = llm_chat("nl_to_json", designer_representation)
    print("[NL-to-JSON Agent]:", json_output)


    # Optionally, save JSON
    try:
        city_json = json.loads(json_output)
        with open("outputs\\city_plan.json", "w") as f:
            json.dump(city_json, f, indent=2)
        print("City plan JSON saved to outputs\\city_plan.json")
    except Exception as e:
        print("Error saving JSON:", e)

if __name__ == "__main__":
    main()
