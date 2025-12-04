# Features & Mechanics To Be Implemented

This document catalogs all features and mechanics that need to be implemented or further defined for the llm-sim project. Items are organized by category and priority.

---

## Feature-File Pairing Policy

For every feature marked as "in progress" (including skeleton or stub implementations), the feature entry must be explicitly paired with its main implementation file(s) in this document. This ensures traceability and clarity for ongoing work. Example:

- **Status**: In Progress
- **Main File(s)**: `sim/agents/needs.py`, `sim/agents/agents.py`

Update the feature entry as soon as work begins, and keep the file references current as the implementation evolves.

---

## 🚩 Top Priority Features (Recommended Order)

The following features are prioritized for efficient development, with foundational systems and dependencies first:

1. **Aging and Life Stages** - Skeleton exists, needs integration
2. **Death and Consequences** - Skeleton exists, needs triggers and effects
3. **Careers and Economy** - Skeleton exists, needs job/income logic
4. **Social Memory and Relationships** - Skeleton exists, needs expansion
5. **World State Persistence** - Not yet implemented
6. **Agent Social Interaction** - Partially complete, needs group mechanics
7. **World Events** - Minimal implementation
8. **Dynamic Weather System** - Proposed

See detailed descriptions in the sections below.

---

## ✅ Completed Features

### 1. Simulation Loop & Scheduler Integration
- **Status**: Completed
- **Main File(s)**: `sim/world/world.py`, `sim/scheduler/scheduler.py`
- **Current State**: 
  - `World.simulation_loop()` enhanced with tick-based event sequencing
  - Dynamic event management added
  - Agents adhere to schedules with enforced movements

### 2. Agent Loading from World Config
- **Status**: Completed
- **Main File(s)**: `sim/world/world_manager.py`, `sim/agents/agent_loader.py`
- **Current State**: 
  - Agents loaded from `personas.yaml` with full schedule parsing
  - Positions fully initialized
  - Agents linked to world via `WorldManager.load_agents_with_schedules()`

### 3. Place Configuration Loading
- **Status**: Completed
- **Main File(s)**: `sim/utils/schema_validation.py`, `sim/world/world_manager.py`
- **Current State**: 
  - Place configuration schema defined
  - Proper place loading with capabilities, vendors, and neighbors
  - Place connectivity validation implemented

### 4. Agent Decision Logic Enhancement
- **Status**: Completed
- **Main File(s)**: `sim/agents/decision_controller.py`, `sim/agents/controllers.py`
- **Current State**: 
  - `DecisionController` consolidates all decision logic
  - Includes rule-based, probabilistic, goal-driven, and context-aware decisions
  - Time-of-day, location context, and social context considered

### 5. Action System Expansion
- **Status**: Completed
- **Main File(s)**: `sim/actions/actions.py`, `sim/agents/modules/agent_actions.py`
- **Current State**: 
  - Actions `WORK`, `SAY`, `INTERACT` fully implemented
  - Action duration/cost modeling via `ACTION_DURATIONS` and `ACTION_COSTS`
  - Job-site validation for WORK action

### 7. Memory System Enhancement
- **Status**: Completed
- **Main File(s)**: `sim/memory/memory.py`, `sim/agents/modules/agent_memory.py`
- **Current State**: 
  - MemoryStore supports episodic, semantic, autobio kinds
  - Rule-based importance calculation, forgetting curve, search/filter by kind
  - Memory consolidation (`compress_nightly`) and semantic extraction implemented
- **Deferred**: Theory of Mind (ToM) memory usage (defer to LLM integration)

### 8. Vendor/Commerce System
- **Status**: Completed
- **Main File(s)**: `sim/world/world.py`, `sim/inventory/inventory.py`
- **Current State**: 
  - Vendor logic, BUY/SELL actions, money tracking
  - Stock replenishment, price fluctuation, agent-to-agent trading

### 13. Metrics & Logging Integration
- **Status**: Completed
- **Main File(s)**: `sim/utils/metrics.py`, `sim/utils/monitor.py`
- **Current State**: 
  - SimulationMetrics fully integrated into simulation loop
  - Monitor hooks called during simulation with configurable logging
  - Metrics export available in JSON and CSV formats

### 24. Needs System
- **Status**: Completed
- **Main File(s)**: `sim/agents/physio.py`, `sim/agents/modules/agent_physio.py`
- **Description**: System to manage agent needs (hunger, energy, fun, social, hygiene, comfort, bladder). Advanced need-driven behaviors and decision logic implemented. All related tests pass.

### 25. Personality Modeling
- **Status**: Completed
- **Main File(s)**: `sim/agents/personality.py`, `sim/agents/persona.py`
- **Description**: Big Five traits, aspirations, and emotional modifiers added to differentiate agent behavior. All tests pass.

### 26. Mood and Emotions
- **Status**: Completed
- **Main File(s)**: `sim/agents/modules/agent_mood.py`, `sim/agents/modules/agent_physio.py`
- **Description**: Moodlets and emotional states influence agent behavior. Moodlet/emotion structure, triggers, and integration fully implemented. All related tests pass.

---

## 🔧 In Progress / Skeleton Features

### 6. Agent Social Interaction
- **Status**: In Progress
- **Main File(s)**: `sim/agents/interaction.py`, `sim/agents/modules/agent_social.py`
- **Current State**:
  - `preference_to_interact()` integrated into agent decision-making
  - Relationship tracking (familiarity, trust) implemented
  - Social memory (past conversations/interactions) implemented
- **TODO**:
  - [ ] Implement group conversation mechanics
  - [ ] Add conversation topic tracking
  - [ ] Implement social influence on agent decisions

### 27. Aging and Life Stages
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/agents.py` (contains `update_life_stage()`)
- **Description**: Agents progress through life stages (child, teen, adult, elder).
- **TODO**:
  - [ ] Add age-based behavioral effects and transitions
  - [ ] Integrate life stage with agent decision logic

### 28. Death and Consequences
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/agents.py` (contains `die()`, `alive`, `time_of_death`)
- **Description**: Mechanics for agent death and consequences.
- **TODO**:
  - [ ] Implement death conditions and triggers
  - [ ] Add mourning/legacy logic
  - [ ] Add effect duration (temporary vs permanent effects)

### 29. Careers and Economy
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/persona.py`, `sim/configs/constants.py`
- **Description**: Job system, income mechanics, and economic interactions.
- **TODO**:
  - [ ] Implement job/career progression logic
  - [ ] Expand economic interactions
  - [ ] Implement `interact_with_inventory()`, `interact_with_place()`, `interact_with_vendor()` stubs

### 30. Social Memory and Relationships
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/modules/agent_relationships.py`, `sim/agents/agents.py`
- **Description**: Track relationships between agents, including familiarity and trust.
- **TODO**:
  - [ ] Expand relationship types and effects
  - [ ] Integrate relationships with agent decision logic

### 33. World State Persistence
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/agents.py` (contains `serialize_state()`, `load_state()`)
- **Description**: Enable saving and loading of the simulation state.
- **TODO**:
  - [ ] Implement full world serialization
  - [ ] Add checkpoint/resume capability
  - [ ] Save/load world events log

---

## 📋 Proposed / Not Yet Implemented

### 14. Test Coverage
- **Status**: Improved (91 tests passing)
- **Main File(s)**: `tests/`
- **TODO**:
  - [ ] Add tests for scheduler module
  - [ ] Add tests for memory recall/write
  - [ ] Add tests for inventory operations
  - [ ] Add integration tests for full simulation runs
  - [ ] Add LLM mocking for offline tests

### 15. Error Handling & Validation
- **Status**: Minimal
- **TODO**:
  - [ ] Add input validation to all public APIs
  - [ ] Improve error messages with context
  - [ ] Add graceful degradation for LLM failures
  - [ ] Implement retry logic for transient failures

### 31. Dynamic Weather System
- **Status**: Proposed
- **Description**: Introduce weather effects that influence agent behavior and place capabilities.
- **TODO**:
  - [ ] Implement weather states and transitions
  - [ ] Add weather effects on agent behavior
  - [ ] Integrate weather with place capabilities

### 32. World Events
- **Status**: Minimal
- **Description**: Add random and scheduled world events.
- **TODO**:
  - [ ] Implement random world events (weather, accidents, festivals)
  - [ ] Add event triggers (time-based, action-based)
  - [ ] Implement event effects on agents/places

### 34. Simulation Metrics Dashboard
- **Status**: Proposed
- **Description**: Create a real-time dashboard to monitor simulation metrics.
- **TODO**:
  - [ ] Design a dashboard interface
  - [ ] Implement real-time data collection
  - [ ] Add visualization for key metrics

### 35. Dynamic Supply & Demand Economy
- **Status**: Proposed
- **Description**: Prices fluctuate based on local/global supply and demand.
- **TODO**:
  - [ ] Track item quantities and recent transaction volumes
  - [ ] Adjust prices algorithmically

### 36. Agent Specialization & Professions
- **Status**: Proposed
- **Description**: Assign agents roles with unique production, consumption, and trading patterns.
- **TODO**:
  - [ ] Extend agent attributes and schedules
  - [ ] Add profession-based production/consumption logic

### 37. Production Chains & Resource Transformation
- **Status**: Proposed
- **Description**: Enable agents/vendors to convert raw materials into finished goods.
- **TODO**:
  - [ ] Define recipes and production actions
  - [ ] Allow agents to seek required inputs

### 38. Barter System & Currency Alternatives
- **Status**: Proposed
- **Description**: Allow agents to negotiate trades without currency (barter).
- **TODO**:
  - [ ] Expand TRADE action logic to support item-for-item deals

### 39. Agent Reputation & Trust Economy
- **Status**: Proposed
- **Description**: Track agent reputation based on past transactions and interactions.
- **TODO**:
  - [ ] Implement reputation tracking
  - [ ] Add trust-based pricing/transaction modifiers

### 40. Black Market & Illicit Trade
- **Status**: Proposed
- **Description**: Hidden economy with risk/reward mechanics.
- **TODO**:
  - [ ] Define illicit item types
  - [ ] Add detection/consequence mechanics

### 41. Economic Events & Shocks
- **Status**: Proposed
- **Description**: Random economic events affecting markets.
- **TODO**:
  - [ ] Define event types and triggers
  - [ ] Implement market response mechanics

### 42. Vendor/Shop Upgrades & Expansion
- **Status**: Proposed
- **Description**: Vendors can upgrade stock capacity, add new items.
- **TODO**:
  - [ ] Implement upgrade mechanics
  - [ ] Add expansion prerequisites

### 9. Item Effects System
- **Status**: Not Implemented
- **Description**: Items apply effects to agents (buffs, debuffs, stat changes).
- **TODO**:
  - [ ] Define effect types and durations
  - [ ] Integrate with agent physio/mood systems

---

## 🟣 Future/Advanced Features

### 16. LLM/Agent Behavior Layering
- **Status**: Future/Deferred
- **Current State**: Basic LLM conversation support exists
- **TODO**:
  - [ ] Complete hardcoded foundation first
  - [ ] Design LLM intervention points (decision override, memory generation)
  - [ ] Implement configurable LLM vs rule-based ratio
  - [ ] Add LLM-generated goals/plans

### 17. Agent Learning/Adaptation
- **Status**: Stub mentioned in goals
- **TODO**:
  - [ ] Implement experience tracking
  - [ ] Add strategy updates based on outcomes
  - [ ] Implement skill progression

### 18. Multi-Agent Communication
- **Status**: Partial
- **Current State**: Broadcast exists but limited
- **TODO**:
  - [ ] Implement targeted messaging between agents
  - [ ] Add message queuing/history
  - [ ] Implement conversation threading

### 19. Time System
- **Status**: Basic
- **Main File(s)**: `sim/utils/utils.py`
- **Current State**: Tick-based time with `TICK_MINUTES = 5`
- **TODO**:
  - [ ] Add day/night cycle effects
  - [ ] Implement time-based capability changes (stores open/close)
  - [ ] Add weather/seasonal effects

---

## Summary by Category

| Category | Completed | In Progress | Proposed |
|----------|-----------|-------------|----------|
| Core Simulation | 3 | 0 | 0 |
| Agent Behavior | 6 | 1 | 2 |
| World/Economy | 2 | 1 | 8 |
| Infrastructure | 1 | 0 | 2 |
| Advanced | 0 | 0 | 4 |

---

## Active Tasks

_No active tasks currently. Refer to CURRENT_TASK.md for the next task to work on._

---

*Last updated: 2025-12-04*
