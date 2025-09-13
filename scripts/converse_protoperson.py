# interrogate_protoperson.py
"""
Spin up an agent instance as a protopersona and set up a chat loop with the user.
Uses the decide_conversation function.
"""

from hmac import new
import sys
import test
import yaml
from datetime import datetime
from sim.agents.agents import Agent, Persona
from sim.world.world import World, Place

# Example protopersona YAML snippet:
"""
Example protopersona YAML snippet:
name: Abraham Massingberd
sex: male
age: 26
job: City Clerk
bio: Dedicated public servant; values order, precision.
values:
- integrity
- efficiency
- public service
goals:
- improve record-keeping
- increase civic engagement
- support local economy
start_place: Lumière City Hall
workplace: Lumière City Hall
job_title: City Clerk
residence_address: 10 La Forêt Street
"""

def CreatePersonaFromProto(proto):
    newPersona = Persona(
        name=proto.get("name", "Helper"),
        age=proto.get("age", 30),
        job=proto.get("job", "Unemployed"),
        city="infer from workplace",
        bio="a knowledgeable and helpful individual.",
        values=["completeness", "helpfulness"],
        goals=["Be helpful, informative, and forthcoming."]
    )
    extraInfo=[proto.get("start_place",""),proto.get("workplace",""),proto.get("job_title",""),proto.get("residence_address")]
    return newPersona, extraInfo


def load_people(city_path="configs/city.yaml"):
    with open(city_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("people", [])

def main():
    protopersonas = load_people()
    proto=None
    if len(sys.argv) > 1:
        test_protopersona_name = sys.argv[1]
        if test_protopersona_name in protopersonas:
            proto = protopersonas[test_protopersona_name]
    else:
        proto=protopersonas[0]

    if not proto:
        print("personas name not found or no protopersonas available.")
        return

    persona, extraInfo = CreatePersonaFromProto(proto)
    persona_workplace, persona_job_title, persona_residence = extraInfo[1], extraInfo[2], extraInfo[3]


    agent = Agent(persona=persona, place=persona_workplace)

    participants = [agent]
    tick = 0
    print(f"Agent '{persona.name}' is ready for interrogation at '{agent.place}'.")
    print("Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat loop.")
            break
        incoming_message = {"to": agent.persona.name, "from": "User", "text": user_input}
        response = agent.decide_conversation(participants, "", tick, incoming_message, start_dt=datetime(1900, 1, 1))
        print(f"{agent.persona.name}: {response.get('reply', '[No reply]')}")
        tick += 1
        tick += 1

if __name__ == "__main__":
    main()
