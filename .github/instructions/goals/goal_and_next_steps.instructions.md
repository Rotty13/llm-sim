## ✅ Recent Completed Goals
- Added YAML/JSON schema validation utilities for configs
- Implemented agent learning/adaptation stubs
- Added simulation metrics and logging utilities

## ⬜ Next Steps & Future Goals
- Expand agent learning/adaptation into full feature (track experience, update strategies)
- Expand metrics/logging to support analytics and reporting
- Expand schema validation to enforce config integrity and error reporting
- Plan and begin LLM/Agent Behavior Layering (advanced reasoning, centralized LLM calls)
# Hierarchical Goals and Tasks (2025-11-26, Updated)
#Ordered by priority and dependencies


## ⬜ Simulation Logic & Relationships
- Establish relationships and state tracking:
  - Who/what is where
  - Who owns what
- Implement agent decision logic:
  - Rule-based
  - Optional probabilistic choices
- Outline and build the simulation loop and scheduler (Appointment, enforce_schedule)
- Expand item/place relationship logic and agent-object interaction rules
- Integrate CLI and planning scripts for world/agent setup and simulation runs

## ✅ Evaluation & Testing
- Developed scenario/test framework for simulation stability and agent performance
- Added monitoring hooks for agent behavior, resource flows, and world events
- Added visualization scripts for city/people graphs
- Next: Documentation & Architecture (system architecture, agent logic, evaluation criteria, docstrings)

## ⬜ Documentation & Architecture
- Maintain clear documentation of:
  - System architecture
  - Agent logic
  - Evaluation criteria
- Ensure all scripts have proper docstrings and usage notes

## ⬜ LLM/Agent Behavior Layering (Future)
- Integrate LLMs for advanced agent reasoning and interaction only after hardcoded foundation is stable
- Centralize LLM calls in sim/llm/llm_ollama.py

## ✅ Recent Development Steps
- (2025-11-26) Began implementation of state tracking and relationships in the simulation system:
  - Added tracking for "who/what is where" and "who owns what."
  - Next: Implement agent decision logic (rule-based and probabilistic choices).
  - Next: Expand the simulation loop and scheduler to enforce appointments and schedules.
- (2025-11-26) Reviewed `agents.py` for pending tasks:
  - Enhanced `decide` method to include rule-based and probabilistic decision-making.
  - Integrated `busy_until` attribute with the scheduler to enforce appointments and schedules.
  - Expanded item/place relationship logic to track ownership and state changes.

## ✅ Simulation System Foundation
- Formalize and implement core data structures for:
  - Agent (Persona, Physio, Agent)
  - Item (Item, ItemStack, Inventory)
  - Place (Place, Vendor)
  - World (World, WorldManager)
- Ensure each class supports:
  - State tracking
  - Relationships
  - Basic interaction logic
- Review and refactor obsolete modules for compatibility or removal

## ⬜ Current Progress (2025-11-26)
- Enhanced decision logic in `DecisionController` to include contextual actions like moving to food locations or home before eating or sleeping.
- Reviewed `enforce_schedule` in `scheduler.py` for integration into the simulation loop.
- Next: Integrate `enforce_schedule` into the simulation loop to ensure agents adhere to their schedules.

## ⬜ Refactoring Agent Module
- Identify functions in `Agent` that can be grouped or decoupled.
- Ensure the `Agent` class is modular and easy to extend/modify.
- Refactor `Agent` to:
  - Separate concerns (e.g., decision-making, memory management, inventory handling).
  - Delegate responsibilities to specialized components or controllers.
  - Simplify the class interface for better maintainability.
- Document the refactored structure and update relevant tests.
- Remove outdated goals and ensure all goals reference current code, systems, and classes.