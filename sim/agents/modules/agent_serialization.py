"""
AgentSerialization module for managing agent serialization and deserialization.
Handles saving and loading agent state to/from dicts or files.
"""
import json
from dataclasses import asdict, is_dataclass

class AgentSerialization:
    def serialize(self, agent):
        # Recursively convert dataclass objects and replace non-serializable objects with class name
        def convert(obj):
            if is_dataclass(obj):
                # Convert dataclass to dict, then recursively process fields
                return convert(asdict(obj))
            elif isinstance(obj, dict):
                result = {}
                for k, v in obj.items():
                    try:
                        result[k] = convert(v)
                    except Exception:
                        result[k] = f"<{type(v).__name__}>"
                return result
            elif isinstance(obj, list):
                return [convert(v) for v in obj]
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                # For non-serializable objects, use their class name as a placeholder
                return f"<{obj.__class__.__name__}>"
        # Convert the agent's __dict__ recursively
        return json.dumps(convert(agent.__dict__))

    def deserialize(self, agent_json, agent_class):
        data = json.loads(agent_json)
        agent = agent_class()
        agent.__dict__.update(data)
        return agent
