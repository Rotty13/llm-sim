"""
protopersona_recall_day.py

Purpose: Spins up a persona LLM, prompts it to recall its day. If the LLM outputs 'Recall(subject)', extract the subject, generate a vivid memory via a second LLM, and inject it into the persona prompt as 'I remember...'.

Key Functions:
- extract_recall_subject: Extracts recall subject from LLM output.
- generate_vivid_memory: Uses Ollama LLM to generate vivid memory.
- persona_recall_day: Orchestrates recall and memory injection.

LLM Usage: Uses Ollama backend via sim.llm.llm_ollama.LLM. No fallback; raises error if not configured.
CLI Args: None (function-based usage).
"""

import re
import yaml
import random
from sim.llm.llm_ollama import LLM
from sim.agents.agents import Agent

llm = LLM(caller="protopersona_recall_day")
llm.temperature = 0.3


def extract_recall_subject(output):
    match = re.search(r'Recall\((.*?)\)', output)
    return match.group(1) if match else None

def generate_vivid_memory(subject,persona):
    # Use LLM to generate a vivid memory for the subject
    memory_prompt = f"Create a (1 sentence) memory with appropriate detail/vividness about: {subject}\n Format it like 'I remember...'"
    system_prompt = f"Your task is to generate a vivid memory for {persona['name']}, a {persona['age']} year old {persona['job']}. Here is some information about you: Bio: {persona['bio']}, Values: {', '.join(persona['values'])}, Goals: {', '.join(persona['goals'])}, Start Place: {persona['start_place']}. When generating memories, ensure they align with your background and personality."
    memory = llm.chat(memory_prompt, system=system_prompt, max_tokens=250, timeout=3000)
    # If LLM returns dict, get 'text'; else, return as string
    if isinstance(memory, dict) and 'text' in memory:
        return memory.get('text')
    return str(memory)

def persona_recall_subject(subject,persona):
    vivid_memory = generate_vivid_memory(subject, persona)
    return f"I remember {vivid_memory}"

def persona_recall_day(persona):
    persona_desc = f"Name: {persona['name']}\nAge: {persona['age']}\nJob: {persona['job']}\nBio: {persona['bio']}\nValues: {', '.join(persona['values'])}\nGoals: {', '.join(persona['goals'])}\nStart Place: {persona['start_place']}"
    agent = Agent(persona['name'], place=persona.get('start_place', None))
    prompt = f"{persona_desc}\nCreate a set of Recalls representing your day. Output only 'Recall(subject/event/fact)'."
    output = llm.chat(prompt, system="Output only Recall(subject/event/fact). Break down Recalls into multiple if needed.")
    output_text = output.get('text') if isinstance(output, dict) and 'text' in output else str(output)
    #iterate through recalls, generate vivid memories and re-prompt
    memories_prompt = ""
    if output_text:
        for recall in output_text.split("Recall(")[1:]:
            recall = recall[:recall.rindex(")")+1]  # Extract up to the closing parenthesis
            recall_subject = extract_recall_subject("Recall(" + recall)
            if recall_subject:
                vivid_memory = generate_vivid_memory(recall_subject, persona)
                print(f"Generated vivid memory for {recall_subject}:\n {vivid_memory}")
                if vivid_memory:
                    memories_prompt += "\n" + vivid_memory
                else:
                    memories_prompt += "\n" + f"I vaguely remember {recall_subject}."

    messages=[]
    memory_message = {"role": "user", "content": memories_prompt}
    messages.append(memory_message)
    prompt = f"{persona_desc}\nDescribe your day based on your memories."+"\n"+memories_prompt
    output = llm.chat(prompt, system="I am " + persona_desc + "\n answer in natural language.",messages=messages)
    print(f"Final persona output for {persona['name']}:", output)
    #combine memories with the output and the persona reflection questions
    messages=[]
    memory_message = {"role": "user", "content": memories_prompt}   
    messages.append(memory_message)
    prompt = f"{persona_desc}\nDescribe your day based on your memories."+"\n"+memories_prompt
    output = llm.chat(prompt, system="I am " + persona_desc + "\n answer in natural language.",messages=messages, timeout=3000,max_tokens=1000)
    print(f"Final persona output for {persona['name']}:", output)
    #combine memories with the output and the persona reflection questions
    messages=[]
    memory_message = {"role": "user", "content": memories_prompt}
    messages.append(memory_message)
    prompt = f"{persona_desc}\nDescribe your day based on your memories."+"\n"+memories_prompt
    output = llm.chat(prompt, system="I am " + persona_desc + "\n answer in natural language.",messages=messages, timeout=3000,max_tokens=1000)
    output = "My day was as follows: " + str(output)
    output = llm.chat(output +"\nDo you feel your memories are real?\nDo you trust them?\nHow do you feel about your memories?\nDoes anything feel wrong about them?", system="You are " + persona_desc,max_tokens=1000, timeout=3000,messages=messages)
    print(f"Persona reflection for {persona['name']}:", output)

if __name__ == "__main__":
    # Load personas from YAML
    with open("configs/World_0/personas.yaml", "r", encoding="utf-8") as f:
        personas = yaml.safe_load(f)["people"]
    persona = random.choice(personas)
    persona_recall_day(persona)
