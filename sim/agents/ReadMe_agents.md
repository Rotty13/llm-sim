
# agents.py – Modular Agent System Documentation

This file and its submodules define the agent system for the llm-sim simulation engine. Agents are autonomous entities that interact with the simulated world, make decisions, manage memory, perform actions, and maintain relationships. The agent logic is modular, with each concern encapsulated in its own submodule.


## Overview
- **Purpose:** Implements a modular agent architecture for simulation, with each concern encapsulated in its own module and composed into the main `Agent` class.
- **Key Classes & Modules:**
  - `Agent`: Main agent class. Composes all agent modules and controllers, delegating functionality for maintainability and extensibility.
  - `Persona`: Agent identity, personality, goals (`persona.py`).
  - `Physio`: Physiological/emotional state (`physio.py`).
  - `AgentMood`: Manages moodlets and emotional state (`modules/agent_mood.py`).
  - `AgentInventory`: Handles inventory logic and item management (`modules/agent_inventory.py`).
  - `AgentMemory`: Episodic and semantic memory management (`modules/agent_memory.py`).
  - `AgentActions`: Action logic and execution (`modules/agent_actions.py`).
  - `AgentSocial`: Social interaction and memory (`modules/agent_social.py`).
  - `AgentSerialization`: State serialization and loading (`modules/agent_serialization.py`).
  - `AgentRelationships`: Relationship management (`modules/agent_relationships.py`).
  - `MemoryManager`: Episodic/autobio memory writing and retrieval (`memory_manager.py`).
  - `InventoryHandler`: Inventory operations and item transfer (`inventory_handler.py`).
  - `LogicController`: Main logic controller for agent behavior (`controllers.py`).
  - `DecisionController`: Modular decision-making logic (`decision_controller.py`).
  - `MovementController`: Handles agent movement and location changes (`movement_controller.py`).
  - Additional modules: `AgentPhysio`, `AgentObservation`, `AgentInventoryPlace`, `AgentLLM`, `AgentSchedule`, `AgentStubs`, `AgentPlanLogic` for specialized logic and delegation.
- **LLM Integration:** All agent conversations and decisions use `sim.llm.llm_ollama` (Ollama backend). No fallback; errors if not configured.
- **World Interaction:** Agents interact with places, items, and other agents via modular actions, inventory, and relationships. All interactions are routed through the `WorldManager` and agent classes.

---


## Modular Structure & Relationships

The `Agent` class composes and delegates to the following modules:
- **Persona**: Identity, personality traits, values, goals.
- **Physio**: Physiological and emotional state (hunger, energy, stress, mood, etc.).
- **AgentMood**: Moodlet management and emotional state transitions.
- **AgentInventory**: Inventory logic, item management, money handling.
- **AgentMemory**: Episodic and semantic memory storage and retrieval.
- **AgentActions**: Action parsing, execution, and effects.
- **AgentSocial**: Social memory and interaction tracking.
- **AgentSerialization**: State serialization and loading for persistence.
- **AgentRelationships**: Familiarity, trust, and relationship management.
- **MemoryManager**: Handles writing and retrieving memory items.
- **InventoryHandler**: Manages inventory operations and item transfers.
- **LogicController**: Main logic controller for agent behavior.
- **DecisionController**: Modular decision-making logic.
- **MovementController**: Handles agent movement and location changes.
- **AgentPhysio, AgentObservation, AgentInventoryPlace, AgentLLM, AgentSchedule, AgentStubs, AgentPlanLogic**: Specialized modules for physiologic logic, observation, place inventory, LLM interaction, scheduling, stubs, and plan logic.

Each module is responsible for a distinct aspect of agent behavior. The agent class delegates to these modules, enabling maintainable, extensible, and testable agent logic.

---

## Key Constants

- `JOB_SITE`: Maps job names to expected work locations.
- `DEFAULT_AGE_TRANSITIONS`: Default age thresholds for life stages.

---


## Core Agent Methods & Module Delegation

The `Agent` class exposes methods for simulation, each delegating to its respective module:
- `tick_update(world, tick)`: Delegates needs decay, mood, and plan logic to `AgentPhysio` and `AgentPlanLogic`.
- `decide(world, obs_text, tick, start_dt)`: Uses `DecisionController` for modular, trait-driven decision-making.
- `act(world, decision, tick)`: Delegates action execution and effects to `AgentActions`, `MovementController`, and other modules.
- `perform_action(action, world, tick)`: Parses and executes a specific action string.
- `step_interact(...)`: Full agent step: conversation (LLM), needs decay, moodlet update, decision, and action.
- `decide_conversation(...)`: Uses LLM backend for conversational response, updating mood and memory.
- `serialize_state()`, `load_state(state)`: Delegates state serialization/loading to `AgentSerialization`.
- `add_moodlet(moodlet, duration)`, `tick_moodlets()`, `set_emotional_state(state)`, `apply_moodlet_triggers()`: Moodlet and emotion management via `AgentMood` and `Physio`.
- `get_relationship(other)`, `update_familiarity(other, delta)`, `update_trust(other, delta)`, `update_relationship(other, delta)`: Relationship management via `AgentRelationships`.
- `use_item(item)`, `add_money(amount)`, `remove_money(amount)`, `money_balance`, `receive_income(amount)`: Inventory and money management via `AgentInventory`.
- `move_to(world, destination)`: Movement logic via `MovementController`.
- `remember_social_interaction(interaction)`: Social memory via `AgentSocial`.
- `initialize_schedule(schedule_data)`, `enforce_schedule(tick)`: Scheduling via `AgentSchedule` and calendar.
- `personality_memory_importance(item)`: Memory importance adjustment by personality traits.

---


## Usage Notes

- Agents are instantiated and managed by simulation scripts and world modules.
- All agent/world interactions are routed through the `WorldManager` and agent classes.
- No CLI arguments directly; agents are controlled by simulation logic.

---


## See Also

- `persona.py`: Agent identity/personality
- `physio.py`: Agent physiological/emotional state
- `modules/agent_mood.py`, `modules/agent_inventory.py`, `modules/agent_memory.py`, `modules/agent_actions.py`, `modules/agent_social.py`, `modules/agent_serialization.py`, `modules/agent_relationships.py`: Modular agent logic
- `memory_manager.py`, `inventory_handler.py`, `controllers.py`, `decision_controller.py`, `movement_controller.py`: Agent controllers and handlers
- `sim/llm/llm_ollama.py`: LLM backend
- `sim/world/world_manager.py`: World management
- `sim/actions/actions.py`: Action DSL and effects

---



---

## Additional Delegation Opportunities

The following logic in the `Agent` class could be further delegated to specialized modules for improved modularity and maintainability:

- **Life Stage Updates:** The method `update_life_stage` is currently handled directly in `Agent`. It could be moved to a persona or life-stage module.
- **Money Management:** Methods like `add_money`, `remove_money`, and `money_balance` could be fully delegated to `AgentInventory`.
- **Moodlet Logic:** Methods such as `add_moodlet`, `tick_moodlets`, and `apply_moodlet_triggers` interact with `Physio` directly. These could be managed by an `AgentMood` module.
- **Schedule Enforcement:** The method `enforce_schedule` could be delegated to a dedicated scheduling module.
- **Action Effects:** Modulation of action effects by personality traits in `act` could be moved to a traits or effects module.
- **Serialization:** Methods `serialize_state` and `load_state` could be fully delegated to `AgentSerialization`.
- **Social Memory:** The method `remember_social_interaction` could be managed by `AgentSocial` instead of appending directly to a list.

Further refactoring in these areas will enhance extensibility, clarity, and testability of the agent system.
