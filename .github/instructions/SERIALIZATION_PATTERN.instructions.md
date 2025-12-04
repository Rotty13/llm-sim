---
description: Serialization pattern for all modules in llm-sim.
name: SERIALIZATION_PATTERN.instructions.md
applyTo: "**/*.py"
---
# Serialization Pattern for llm-sim Modules

All modules that require serialization of internal state (e.g., agent memory, inventory, relationships) must implement the following pattern:

## Required Methods
- `serialize(self) -> dict`: Returns a serializable copy of the module's internal state as a dictionary. This should be a shallow or deep copy as appropriate for the module.
- `load(self, data: dict)`: Loads the module's internal state from a dictionary. The method must check that `data` is a dictionary and restore all relevant fields.

## Example
```python
class ExampleModule:
    def __init__(self):
        self.state = {}

    def serialize(self) -> dict:
        return self.state.copy()

    def load(self, data: dict):
        if isinstance(data, dict):
            self.state = data.copy()
```

## Additional Notes
- Do not use JSON strings for serialization; always use Python dictionaries.
- Ensure all fields required for restoration are included in the dict returned by `serialize()`.
- If the module contains nested objects, recursively call their `serialize()`/`load()` methods as needed.
- This pattern applies to all agent modules, memory stores, inventories, and any other serializable components.
- Do not use `to_dict`, `from_dict`, `to_json`, or `from_json` methods for serialization; use only `serialize` and `load`.

## Rationale
This pattern ensures consistency, simplicity, and compatibility with the rest of the llm-sim codebase.
