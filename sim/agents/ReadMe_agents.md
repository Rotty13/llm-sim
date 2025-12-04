
# agents.py – Modular Agent System Documentation

This file and its submodules define the agent system for the llm-sim simulation engine. Agents are autonomous entities that interact with the simulated world, make decisions, manage memory, perform actions, and maintain relationships. The agent logic is modular, with each concern encapsulated in its own submodule.

## Overview
- **Purpose:** Implements a modular agent architecture for simulation, including decision-making, memory, inventory, relationships, mood, actions, social logic, serialization, and world interaction.
- **Key Classes & Modules:**
  - `Agent`: Main agent class, composes all agent modules.
  - `Persona`: Agent identity, personality, goals (`persona.py`)
  - `Physio`: Physiological/emotional state (`physio.py`)
  - `AgentMood`: Mood logic (`agent_mood.py`)
  - `AgentInventory`: Inventory logic (`agent_inventory.py`)
  - `AgentMemory`: Memory logic (`agent_memory.py`)
  - `AgentActions`: Action logic (`agent_actions.py`)
  - `AgentSocial`: Social logic (`agent_social.py`)
  - `AgentSerialization`: Serialization logic (`agent_serialization.py`)
  - `AgentRelationships`: Relationship logic (`agent_relationships.py`)
  - Controllers: Logic, memory, inventory, decision, movement controllers
- **LLM Integration:** All agent conversations and decisions use `sim.llm.llm_ollama` (Ollama backend).
- **World Interaction:** Agents interact with places, items, and other agents via modular actions and relationships.

---

## Modular Structure

- Each agent concern (mood, inventory, memory, actions, social, serialization, relationships) is implemented in its own file and composed into the main `Agent` class.
- Controllers manage agent logic, memory, inventory, decision-making, and movement.
- The agent class delegates functionality to these modules for maintainability and extensibility.

---

## Key Constants

- `JOB_SITE`: Maps job names to expected work locations.
- `DEFAULT_AGE_TRANSITIONS`: Default age thresholds for life stages.

---

## Functions & Methods

### Core Agent Methods

- `tick_update(world, tick)`: Update agent state each tick (needs decay, mood, aspirations, plan).
- `decide(world, obs_text, tick, start_dt)`: Modular decision-making logic (rule-based, probabilistic, trait-driven).
- `act(world, decision, tick)`: Perform the decided action using modular action logic.
- `perform_action(action, world, tick)`: Perform a specific action string (e.g., MOVE).
- `step_interact(...)`: Full agent step: converse, decay needs, update moodlets, decide, act.
- `decide_conversation(...)`: Use LLM to decide conversational response.

### Memory & Observation

- `add_observation(text)`: Add an observation to the memory manager.
- `memory_manager.write_memory(item)`: Write a memory item (episodic/autobio).
- `_maybe_write_diary(text, tick)`: Write diary entry if conditions are met.
- `personality_memory_importance(item)`: Adjust memory importance by personality traits.

### Inventory & Item Management

- `deposit_item_to_place(world, item_name, quantity)`: Deposit item from agent to place inventory.
- `withdraw_item_from_place(world, item_name, quantity)`: Withdraw item from place to agent inventory.
- `use_item(item)`: Use an item from inventory, applying effects.
- `add_money(amount)`, `remove_money(amount)`, `money_balance`: Manage money in inventory.
- `receive_income(amount)`: Add income as money.

### Movement

- `move_to(world, destination)`: Move agent to a new location if valid.

### Social & Group Interaction

- `remember_social_interaction(interaction)`: Add a social interaction to social memory.
- `group_conversation_stub(participants, topic)`: Stub for group conversation mechanics.

### Mood & Emotion

- `add_moodlet(moodlet, duration)`, `tick_moodlets()`, `set_emotional_state(state)`, `apply_moodlet_triggers()`: Manage moodlets and emotional state.

### Serialization & State Loading

- `serialize_state()`, `load_state(state)`: Serialize/load agent state for saving.

### Relationship Management

- `set_relationship(other, familiarity=0.5, trust=0.5)`, `get_relationship(other)`, `update_familiarity(other, delta)`, `update_trust(other, delta)`, `update_relationship(other, delta)`: Manage relationships.

### Scheduling

- `enforce_schedule(tick)`, `initialize_schedule(schedule_data)`: Manage agent schedule and appointments.

---

## Usage Notes

- Agents are managed by simulation scripts and world modules.
- All agent/world interactions are routed through the `WorldManager` and agent classes.
- No CLI arguments directly; agents are instantiated and controlled by simulation logic.

---

## See Also

- `persona.py`: Agent identity/personality
- `physio.py`: Agent physiological/emotional state
- `agent_mood.py`, `agent_inventory.py`, `agent_memory.py`, `agent_actions.py`, `agent_social.py`, `agent_serialization.py`, `agent_relationships.py`: Modular agent logic
- `sim/llm/llm_ollama.py`: LLM backend
- `sim/world/world_manager.py`: World management
- `sim/actions/actions.py`: Action DSL and effects

---

## Future Improvements

The following refactoring proposals are planned for future development:

- **Explicit Interfaces/Abstract Base Classes:** Define abstract base classes or interfaces for agent modules (e.g., `AgentMemoryBase`, `AgentInventoryBase`) in a new `sim/agents/interfaces.py` to enforce consistent APIs and support extensibility.
- **Dependency Injection for Controllers:** Refactor the `Agent` class to accept controller and module instances via its constructor, allowing easier testing and customization.
- **Event System:** Introduce an event system (e.g., `AgentEvent`, `AgentEventHandler`) for agent actions, state changes, and interactions to decouple logic and support extensibility.
- **Documentation & Type Hints:** Ensure all modules and controllers have clear docstrings and type hints for public methods, and add usage examples and diagrams to the README for common agent workflows.
