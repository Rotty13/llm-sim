"""
Functional Purpose: Generates object instances from JSON schema using LLM.
Description: Loads schema, uses LLM to fill properties, and creates example objects.
Replaced by: entity_creation.py (consolidated)
"""
#load object.json and feed it to llm to create an object instance
from urllib import response
from click import prompt
from sim.llm.llm_ollama import LLM
import json

with open("data\\schemas\\entity_base.json", "r") as f:
    object_data = json.load(f)

llm = LLM(gen_model="llama3.1:8b-instruct-q4_0")

#uses llm to fill out the properties of a json object based on its schema
def filljsonproperty(property):
    prop_type = property.get("type")
    # Use LLM to generate a value for this property
    prompt = f"Generate a valid example value for this property schema: {json.dumps(property)}. Return only the value, no explanation."
    value = llm.chat_json(prompt, max_tokens=128)
    # Try to extract the value from the LLM response
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    # fallback: if the LLM returns a raw value
    if isinstance(value, (str, int, float, bool, list, dict)):
        return value
    # fallback: use static values if LLM fails
    if prop_type == "string":
        return "example string"
    elif prop_type == "number":
        return 42
    elif prop_type == "boolean":
        return True
    elif prop_type == "array":
        item_schema = property.get("items", {})
        return [filljsonproperty(item_schema)]
    elif prop_type == "object":
        props = property.get("properties", {})
        return {k: filljsonproperty(v) for k, v in props.items()}
    return None


def create_object_instance(schema):
    properties = schema.get("properties", {})
    obj_instance = {}
    for prop, details in properties.items():
        obj_instance[prop] = filljsonproperty(details)
    return obj_instance

response = create_object_instance(object_data)
print("Generated Object Instance:", response)
