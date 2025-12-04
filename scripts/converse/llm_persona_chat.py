"""
llm_persona_chat.py

Purpose: Agent for direct LLM-based conversation with protopersonas loaded from city.yaml.
Key Classes:
- LLMPersonaChat: Loads people and enables persona chat via Ollama LLM.
LLM Usage: Uses Ollama backend via sim.llm.llm_ollama.llm. No fallback; raises error if not configured.
CLI Args: None (class-based usage).
"""

import yaml
import os
from sim.llm.llm_ollama import LLM

class LLMPersonaChat:
    def __init__(self, city_yaml_path, model_path=None):
        self.city_yaml_path = city_yaml_path
        self.model_path = model_path
        self.people = self._load_people()
        self.llm = LLM()

    def _load_people(self):
        with open(self.city_yaml_path, 'r', encoding='utf-8') as f:
            city_data = yaml.safe_load(f)
        return city_data.get('people', [])

    def converse_with_persona(self, persona, prompt, **llm_kwargs):
        persona_context = self._build_persona_context(persona)
        full_prompt = f"{persona_context}\n\n{prompt}"
        response = self.llm.chat(full_prompt, **llm_kwargs)
        return response

    def _build_persona_context(self, persona):
        context = [
            f"Name: {persona.get('name')}",
            f"Age: {persona.get('age')}",
            f"Job: {persona.get('job')}",
            f"Bio: {persona.get('bio')}",
            f"Values: {', '.join(persona.get('values', []))}",
            f"Goals: {', '.join(persona.get('goals', []))}",
            f"Residence: {persona.get('residence_address')}",
            f"Workplace: {persona.get('workplace')}",
            f"Job Title: {persona.get('job_title')}",
        ]
        return "\n".join(context)

if __name__ == "__main__":
    city_yaml_path = os.path.join(os.path.dirname(__file__), "..", "configs", "city.yaml")
    model_path = "./onnx_model/Llama-3.2-3B-Instruct-ONNX/cpu_and_mobile/model.onnx"  # Update as needed
    agent = LLMPersonaChat(city_yaml_path, model_path)
    persona = agent.people[0]  # Example: first persona
    prompt = "Describe your typical day at work."
    response = agent.converse_with_persona(persona, prompt)
    print(f"Persona: {persona.get('name')}")
    print(f"Response: {response}")
