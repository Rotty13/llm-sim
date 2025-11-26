"""
protopersona_interrogator_agent.py
Agent to interrogate every protopersona in the city about their workplace and home.
"""
from datetime import datetime
import yaml
import os
from typing import Optional

from sim.llm.llm_ollama import LLM

class ProtopersonaInterrogator:
    def __init__(self, city_yaml_path):
        self.city_yaml_path = city_yaml_path
        self.results = []
        self.people = self._load_people()

    def _load_people(self):
        with open(self.city_yaml_path, 'r', encoding='utf-8') as f:
            city_data = yaml.safe_load(f)
        return city_data.get('people', [])

    def interrogate(self, llm_agent:Optional[LLM]=None, max_retries=2):
        for persona in self.people:
            prompt = self._build_prompt(persona)
            response: dict
            retries = 0
            while retries <= max_retries:
                if llm_agent:
                    response = llm_agent.chat_json(prompt, max_tokens=1024)
                if self._is_valid_response(response):
                    break
                prompt = self._build_followup_prompt(persona, response)
                retries += 1
            result = {
                "name": persona.get("name"),
                "response": response
            }
            #print result
            print(f"Interrogated {persona.get('name')}: {response}")
            self.results.append(result)
        return self.results

    def _build_prompt(self, persona):
        return (
            f"You are {persona.get('name')}, working as a {persona.get('job_title')} at {persona.get('workplace')}.\n"
            "I am gathering information about your daily life for city planning.\n"
            "Please reply in JSON format with the following keys: 'workplace', 'home'.\n"
            "For 'workplace', include: rooms (names and purposes), items (type, minimal number, locality in room), and how your workplace fits into the local neighborhood.\n"
            "For 'home', include: rooms (count and category), household members (name, age, employment status), and a general visual description of the outside and interior of your house.\n"
            "If you don't know, make reasonable assumptions based on your role and address.\n"
            "If any information is missing, state your assumptions.\n"
        )

    def _is_valid_response(self, response:dict|str):
        if not response:
            return False
        import json
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                return False
        if isinstance(response, dict) and 'failedjson' not in response:
            return True
        return False


    def _build_followup_prompt(self, persona, prev_response):
        return (
            f"Your previous response was incomplete or unclear: {prev_response}.\n"
            "Please provide a more detailed and structured JSON answer as described before.\n"
            "Remember to make reasonable assumptions if needed, and include local context.\n"
        )

    def _interrogate_workplace(self, persona):
        # Only basic info available from YAML
        workplace = persona.get("workplace")
        job_title = persona.get("job_title")
        # Placeholder for workplace details, as rooms/items are not in YAML
        return {
            "workplace": workplace,
            "job_title": job_title,
            "rooms": [],
            "items": []
        }

    def _interrogate_home(self, persona):
        # Only basic info available from YAML
        address = persona.get("residence_address")
        # Placeholder for home details, as rooms/members/visuals are not in YAML
        return {
            "address": address,
            "rooms": [],
            "members": [],
            "visual_description": {}
        }

if __name__ == "__main__":
    # Example usage
    city_yaml_path = os.path.join(os.path.dirname(__file__), "..", "configs", "city.yaml")
    interrogator = ProtopersonaInterrogator(city_yaml_path)
    from sim.llm.llm_ollama import llm
    results = interrogator.interrogate(llm_agent=llm)
    # Save results to a timestamped YAML file   

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(os.path.dirname(__file__), "..", "outputs", f"employee_interrogation_results_{timestamp}.yaml")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(interrogator.results, f, allow_unicode=True)
