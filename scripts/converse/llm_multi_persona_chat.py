"""
llm_multi_persona_chat.py

Facilitates a multi-persona chat session using LLM-based personas. Each persona is loaded and interacts in a turn-based chat loop. Used for simulating group conversations and persona interactions.

"""

import sys
import os
import importlib
from typing import List
import argparse

# Adjust the path if llm_persona_chat.py is in a different directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from llm_persona_chat import LLMPersonaChat

def load_persona(persona_id: int):
    # Loads LLMPersonaChat with city.yaml path
    city_yaml_path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "yaml", "city.yaml")
    return LLMPersonaChat(city_yaml_path)

def multi_persona_chat(n_personas: int, n_turns: int = 5):
    # Load LLMPersonaChat and personas
    chat_agent = load_persona(0)
    personas = chat_agent.people[:n_personas]
    messages = ["Hello!"] * n_personas

    for turn in range(n_turns):
        print(f"\n--- Turn {turn + 1} ---")
        for i, persona in enumerate(personas):
            prev_msg = messages[i - 1] if i > 0 else messages[-1]
            response = chat_agent.converse_with_persona(persona, prev_msg)
            print(f"{persona.get('name', f'Persona_{i}')}: {response}")
            messages[i] = response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-persona chat simulation")
    parser.add_argument("--n_personas", type=int, default=3, help="Number of personas")
    parser.add_argument("--n_turns", type=int, default=5, help="Number of conversation turns")
    args = parser.parse_args()

    multi_persona_chat(args.n_personas, args.n_turns)