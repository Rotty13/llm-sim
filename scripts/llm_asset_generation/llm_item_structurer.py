"""
llm_item_structurer.py

Script to structure LLM responses according to the item schema defined in configs/yaml/schema/item_schema.yaml.
Uses the LLM Ollama client to request a response and formats it as a Python dict matching the schema.
"""


"""
llm_item_structurer.py

Script to structure LLM responses according to the item schema using Pydantic and Ollama structured outputs.
"""


import json
from sim.llm.llm_ollama import LLM
from item_schema_pydantic import Item
import yaml
from pydantic import BaseModel
from typing import Any, Type

def describe_pydantic_model(model: Type[BaseModel], prefix: str = "") -> str:
    """
    Recursively describe all fields in a Pydantic model for prompt context.
    """
    lines = []
    for field_name, field in model.model_fields.items():
        field_type = field.annotation
        # Handle NoneType
        if field_type is None:
            field_type_str = "None"
        elif hasattr(field_type, "__name__"):
            field_type_str = field_type.__name__
        else:
            field_type_str = str(field_type)
        field_info = f"{prefix}{field_name} ({field_type_str}): "

        # Handle nested Pydantic models
        nested_model = None
        if hasattr(field_type, "__fields__"):
            nested_model = field_type
        elif hasattr(field_type, "__origin__"):
            # Handle generics like Optional[X], List[X], etc.
            args = getattr(field_type, "__args__", [])
            for arg in args:
                if isinstance(arg, type) and issubclass(arg, BaseModel):
                    nested_model = arg
                    break
        if nested_model and isinstance(nested_model, type) and issubclass(nested_model, BaseModel):
            lines.append(field_info + "(object)")
            lines.append(describe_pydantic_model(nested_model, prefix=prefix + "  "))
        else:
            # Example or instruction for each type
            if field_name == "id":
                example = "(unique string, e.g. 'chair-wooden')"
            elif field_name == "name":
                example = "(short descriptive name, e.g. 'Wooden Chair')"
            elif field_name == "description":
                example = "(detailed description, e.g. 'A sturdy wooden chair with a cushioned seat.')"
            elif field_name == "type":
                example = "(category, e.g. 'furniture', 'tool', etc.)"
            elif field_name == "tags":
                example = "(list of relevant tags, e.g. ['furniture', 'wooden'])"
            elif field_name == "location":
                example = "(where the item is found, e.g. 'indoor', 'living room')"
            elif field_name == "size":
                example = "(dimensions, e.g. {'width': 0.5, 'depth': 0.5, 'height': 1.0})"
            elif field_name == "weight":
                example = "(weight in kg, e.g. 20.5)"
            elif field_name == "material":
                example = "(main material, e.g. 'wood', 'metal')"
            elif field_name == "orientation":
                example = "(orientation, e.g. {'yaw': 0, 'pitch': 0, 'roll': 0})"
            elif field_name == "stackable":
                example = "(true/false)"
            elif field_name == "quantity":
                example = "(integer, e.g. 1)"
            elif field_name == "durability":
                example = "(integer or enum, e.g. 100 or 'new')"
            elif field_name == "actions":
                example = "(list of actions, e.g. ['sit', 'stand'])"
            elif field_name == "affordances":
                example = "(list of affordances, e.g. ['seating'])"
            elif field_name == "required_attributes":
                example = "(list of required agent attributes, e.g. ['strength'])"
            elif field_name == "interaction_range":
                example = "(distance or context, e.g. 1.0 or 'adjacent')"
            elif field_name == "interaction_feedback":
                example = "(feedback, e.g. 'You sit down comfortably.')"
            elif field_name == "effects":
                example = "(list of effects, e.g. [{'type': 'restore_energy', 'amount': 5}])"
            elif field_name == "triggers":
                example = "(list of triggers, e.g. ['on_use'])"
            elif field_name == "side_effects":
                example = "(list of side effects, e.g. ['makes noise'])"
            elif field_name == "cooldown":
                example = "(cooldown in seconds, e.g. 10)"
            elif field_name == "creation":
                example = "(creation rule, e.g. 'crafted from wood')"
            elif field_name == "destruction":
                example = "(destruction rule, e.g. 'breaks after 100 uses')"
            elif field_name == "decay":
                example = "(decay/expiration, e.g. 'rots after 30 days')"
            elif field_name == "state":
                example = "(state dict, e.g. {'is_owned': true, 'owner_id': 'player'})"
            elif field_name == "owner":
                example = "(owner id, e.g. 'player')"
            elif field_name == "accessibility":
                example = "(access control, e.g. 'public', 'private')"
            else:
                example = "(fill with a plausible value)"
            lines.append(field_info + example)
    return "\n".join(lines)

def get_structured_item_from_llm(prompt: str, model: str = "llama3.1:8b-instruct-q8_0", max_tokens: int = 512) -> Item:
    llm = LLM(gen_model=model)
    schema = Item.model_json_schema()
    # Build a detailed, field-by-field context for the LLM
    schema_context = describe_pydantic_model(Item)
    system_msg = (
        "You are an expert simulation designer. Respond ONLY with a JSON object matching this item schema. "
        "For each field, provide a realistic, plausible, and non-empty value as described below. "
        "Do not use null, empty objects, or empty lists unless the value is truly unknown or inapplicable. "
        "Here is the schema and field-by-field instructions:\n" + schema_context + "\nDo not include explanations or extra text."
    )
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": 500, "num_ctx": 8192, "num_predict": max_tokens},
        "format": "json",
        "keep_alive": "30m"
    }
    data = llm._post("/api/chat", body, timeout=120)
    txt = (data.get("message") or {}).get("content", "").strip()
    s, e = txt.find("{"), txt.rfind("}")
    if s != -1 and e != -1:
        txt = txt[s:e+1]
    try:
        item = Item.model_validate_json(txt)
    except Exception as e:
        print("Validation error:", e)
        print("Raw response:", txt)
        raise
    return item

if __name__ == "__main__":
    prompt = "Create a new item definition for a wooden chair."
    item = get_structured_item_from_llm(prompt)
    print("Structured item:")
    print(yaml.dump(item.model_dump(), allow_unicode=True, sort_keys=False))
