"""
llm_item_structurer.py

Script to structure LLM responses according to the item schema using Pydantic and Ollama structured outputs.
Main functionality:
- Uses the LLM Ollama client to request a response and formats it as a Python dict matching the schema.
- Uses the Item Pydantic model for schema validation.
- CLI usage: Run directly to generate a structured item for a prompt.
"""


import json
from re import M
import yaml
from pydantic import BaseModel
from sim.schemas.items import PhysicalProperties, Ownership, Lifecycle, Interaction, Effects
from sim.llm.ollama_api import ErrorResponse, OllamaAPI
from sim.llm.ollama_schemas import ChatMessage, ChatRequest, ChatResponse, ModelOptions

from typing import Any, Type
from sim.llm.llm_ollama import LLM

# Composite ItemClass model using modular schema fragments
class ItemClass(BaseModel):
    id: str
    name: str
    description: str
    type: str
    tags: list[str] = []
    physical: PhysicalProperties
    lifecycle: Lifecycle
    interaction: Interaction
    effects: Effects


def get_schema_json(model: Type[BaseModel]) -> str:
    """
    Returns the JSON schema of a Pydantic model as a string.
    """
    return json.dumps(model.model_json_schema(), indent=2)

# Replace LLM with OllamaAPI
ollama_api = OllamaAPI()

MODEL_1 = "llama3.1:8b-instruct-q8_0"
MODEL_2 = "qwen3:1.7b"
MODEL_Default = MODEL_2

def get_structured_item_from_llm(prompt: str, model: str = MODEL_Default, max_tokens: int = 2*512) -> ItemClass:
    schema_context = get_schema_json(ItemClass)
    system_msg = (
        "You are an expert simulation designer. Respond ONLY with a JSON object that strictly adheres to the provided item schema. "
        "Ensure all fields are realistic, plausible, and non-empty unless explicitly stated as optional. "
        "Avoid null values, empty objects, or empty lists unless the field is truly inapplicable. "
        "Here is the schema in JSON format:\n" + schema_context + "\nDo not include any explanations, comments, or extra text."
    )

    chat_request = ChatRequest(
        model=model,
        messages=[ChatMessage(role="system", content=system_msg), ChatMessage(role="user", content=prompt)],
        stream=False,
        think=True,
        format=ItemClass.model_json_schema(),
        options=ModelOptions(temperature=0.3, num_ctx=8192, num_predict=max_tokens)
    )

    response = ollama_api.chat(chat_request)

    if isinstance(response, ChatResponse):
        txt = response.message.content.strip()
        think: str = response.message.thinking or ""
        print("LLM Thinking Trace:\n", think)
        s, e = txt.find("{"), txt.rfind("}")
        if s != -1 and e != -1:
            txt = txt[s:e+1]
        try:
            return ItemClass.model_validate_json(txt)
        except Exception as e:
            print("Validation error:", e)
            print("Raw response:", txt)
            raise
    else:
        raise ValueError(f"Error from Ollama API: {response.error}")

def iteratively_compose_item(prompt: str, model: str = MODEL_Default, max_tokens: int = 5*512) -> ItemClass:
    """
    Iteratively composes an item by selecting fragments and populating fields using the LLM.
    """
    schema_context = get_schema_json(ItemClass)
    system_msg = (
        "You are an expert simulation designer. Respond ONLY with JSON objects matching the schema fragments. "
        "Iteratively provide values for each fragment (PhysicalProperties, Ownership, Lifecycle, Interaction, Effects). "
        "Do not use null, empty objects, or empty lists unless the value is truly unknown or inapplicable. "
        "Here is the schema and field-by-field instructions:\n" + schema_context + "\nDo not include explanations or extra text."
    )

    fragments = {
        "physical": PhysicalProperties,
        "ownership": Ownership,
        "lifecycle": Lifecycle,
        "interaction": Interaction,
        "effects": Effects
    }

    item_data = {}

    for fragment_name, fragment_model in fragments.items():
        fragment_prompt = (
            f"{prompt}\n\n"
            f"Now provide the {fragment_name} fragment. "
            f"Use the following schema:\n{get_schema_json(fragment_model)}"
        )

        chat_request = ChatRequest(
            model=model,
            messages=[ChatMessage(role="system", content=system_msg),
                      ChatMessage(role="user", content=fragment_prompt)
            ],
            stream=False,
            think=True,
            options=ModelOptions(temperature=0.6, num_ctx=8192, num_predict=max_tokens)
        )

        response = ollama_api.chat(chat_request)

        if isinstance(response, ChatResponse):
            txt = response.message.content.strip()
            s, e = txt.find("{"), txt.rfind("}")
            if s != -1 and e != -1:
                txt = txt[s:e+1]
            try:
                item_data[fragment_name] = fragment_model.parse_raw(txt)
            except Exception as e:
                print(f"Validation error for {fragment_name}:", e)
                print("Raw response:", txt)
                raise
        else:
            raise ValueError(f"Error from Ollama API while processing {fragment_name}: {response.error}")

    return ItemClass(**item_data)

def get_structured_item_from_llm_streaming(prompt: str, model: str = MODEL_Default, max_tokens: int = 128) -> ItemClass:
    """
    Generates a structured item using the LLM with streaming enabled.
    """
    schema_context = get_schema_json(ItemClass)
    system_msg = (
        "You are an expert simulation designer. Respond ONLY with a JSON object matching this item schema. "
        "For each field, provide a realistic, plausible, and non-empty value as described below. "
        "Do not use null, empty objects, or empty lists unless the value is truly unknown or inapplicable. "
        "Here is the schema in JSON format:\n" + schema_context + "\nDo not include any explanations, comments, or extra text."
    )

    chat_request = ChatRequest(
        model=model,
        messages=[ChatMessage(role="system", content=system_msg), ChatMessage(role="user", content=prompt)],
        stream=True,  # Enable streaming
        format=ItemClass.model_json_schema(),
        options=ModelOptions(temperature=0.3, num_ctx=8192, num_predict=max_tokens)
    )

    response = ollama_api.chat(chat_request, stream=True)

    if  isinstance(response, ChatResponse):
        streamed_content = ""
        in_thinking = False
        thinking = ""
        content = ""
        assert response.message is not None
        assert response.message.content is not None
        for chunk in response:  # Assuming content is streamed in chunks
            assert chunk.thinking is not None
            if chunk.thinking:
                if not in_thinking:
                    in_thinking = True
                    print("Thinking:\n", end="", flush=True)
                print(chunk.thinking, end="", flush=True)
                thinking += chunk.thinking
            elif chunk.content:
                if in_thinking:
                    in_thinking = False
                    print("\n\nAnswer:\n", end="", flush=True)
                print(chunk.content, end="", flush=True)
                content += chunk.content

        s, e = content.find("{"), content.rfind("}")
        if s != -1 and e != -1:
            content = content[s:e+1]
        try:
            return ItemClass.model_validate_json(content)
        except Exception as e:
            print("Validation error:", e)
            print("Raw response:", content)
            raise
    else:
        raise ValueError(f"Error from Ollama API: {response.error}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Create a new item definition for a record player."
    item = get_structured_item_from_llm(prompt, max_tokens=128)
    print("Structured item:")
    print(yaml.dump(item.model_dump(), allow_unicode=True, sort_keys=False))
