- ⬜ **Feature**: Place inventory system

- ✅ **Feature**: CLI/planning script integration
  - **Status**: completed
  - **Reason**: Simulation loop now invoked via CLI; planning scripts connected to simulation logic
  - **Created**: 2025-11-26
  - **Completed**: 2025-11-26
  - **Notes**: CLI 'run' command executes simulation loop for world/agent setup and runs
# llm-sim Project Roadmap

This file tracks all current, future, and completed features, goals, and tasks, along with their creation and/or completion dates.

## Format
- Each entry should include:
  - **Feature/Goal/Task**
  - **Status**: current, future, completed, suspended
  - **Reason**: (if status is not completed, provide context for current status, blockers, or next steps)
  - **Creation Date**
  - **Completion Date** (if applicable)
  - **Description/Notes**

## Example Entry
- ✅ **Feature**: Place inventory system
  - **Status**: current
  - **Reason**: Implementation in progress; agent-item-place transfer logic next.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Enables item storage and transfer in places.

---

## Roadmap Entries

- ✅ **Feature**: Modular core engine and scripts
  - **Status**: completed
  - **Reason**: (none)
  - **Created**: (pre-2025)
  - **Completed**: 2025-11-01
  - **Notes**: Initial modular architecture for simulation logic.

- ✅ **Feature**: WorldManager and compartmentalized worlds
  - **Status**: completed
  - **Reason**: (none)
  - **Created**: (pre-2025)
  - **Completed**: 2025-11-01
  - **Notes**: Handles world file I/O and data loading.

- ✅ **Feature**: LLM integration (Ollama only)
  - **Status**: completed
  - **Reason**: (none)
  - **Created**: 2025-11-01
  - **Completed**: 2025-11-10
  - **Notes**: All LLM calls routed through Ollama backend.

- ✅ **Feature**: CLI tools (create, list, info, run, delete)
  - **Status**: completed
  - **Reason**: (none)
  - **Created**: 2025-11-01
  - **Completed**: 2025-11-20
  - **Notes**: World management via CLI.

- ⬜ **Feature**: Example worlds/scenarios (historical focus)
  - **Status**: current
  - **Reason**: Expanding onboarding and scenario templates for pre-1900 worlds.
  - **Created**: 2025-11-25
  - **Completed**: (pending)
  - **Notes**: Pre-1900 onboarding world and templates.

- ⬜ **Feature**: Place inventory system

- ✅ **Feature**: Simulation System Foundation and cross-system logic stubs
  - **Status**: completed
  - **Reason**: All major systems (Agent, Item, Place, World, Vendor) have foundational stubs and cross-system logic
  - **Created**: 2025-11-26
  - **Completed**: 2025-11-26
  - **Notes**: Enables future development of state tracking, relationships, and interaction logic for all core systems
  - **Status**: current
  - **Reason**: Implementation in progress; agent-item-place transfer logic next.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Enables item storage and transfer in places.

- ⬜ **Feature**: Agent-item-place transfer logic
  - **Status**: current
  - **Reason**: Agent methods for depositing/withdrawing items to/from place inventories implemented; interaction rules expansion next.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Enables realistic agent-object-place interactions and state tracking.

- ⬜ **Feature**: Formalize core data structures (Agent, Item, Inventory, Place, World)
  - **Status**: current
  - **Reason**: Expanding class definitions and relationships for simulation stability.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Foundation for stable, hardcoded agent-based simulation.

- ⬜ **Feature**: Relationships and state tracking
  - **Status**: future
  - **Reason**: Will require unified logic for agent, item, and object locations and ownership.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Track agent, item, and object locations and ownership.

- ⬜ **Feature**: Agent decision logic (rule-based, probabilistic)
  - **Status**: future
  - **Reason**: Pending completion of core agent and item interaction logic.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Hardcoded agent actions and choices.

- ⬜ **Feature**: Simulation loop and scheduler
  - **Status**: future
  - **Reason**: Will be implemented after agent logic and state tracking are stable.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Tick-based simulation and event sequencing.

- ⬜ **Feature**: Scenario/test framework
  - **Status**: future
  - **Reason**: Will be designed to systematically evaluate simulation stability and agent performance.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Systematic evaluation of simulation stability and agent performance.

- ⬜ **Feature**: LLM/agent behavior layering
  - **Status**: future
  - **Reason**: Suspended until hardcoded foundation is stable.
  - **Created**: 2025-11-26
  - **Completed**: (pending)
  - **Notes**: Integrate LLMs after hardcoded foundation is stable.

- ✅ **Documentation**: Comprehensive Features/Mechanics TODO List
  - **Status**: completed
  - **Reason**: Created detailed audit of all features and mechanics needing implementation
  - **Created**: 2025-11-26
  - **Completed**: 2025-11-26
  - **Notes**: See `docs/FEATURES_TODO.md` for full list of 20 categorized items with priorities
  - **Categories covered**: Core Simulation (3), Agent Behavior (4), World/Economy (4), Infrastructure (4), Advanced/Future (5)

