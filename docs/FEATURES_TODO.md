# Features & Mechanics To Be Implemented

This document catalogs all features and mechanics that need to be implemented or further defined for the llm-sim project. Items are organized by category and priority.

---

## 🔴 High Priority (Core Simulation Foundation)

### 1. Simulation Loop & Scheduler Integration
- **Status**: Completed
- **Current State**: 
  - `World.simulation_loop()` enhanced with tick-based event sequencing.
  - Dynamic event management added.
  - Agents now adhere to schedules with enforced movements.
- **Notes**:
  - Added placeholder for dynamic world events.
  - Improved modularity and clarity of the simulation loop.

### 2. Agent Loading from World Config
- **Status**: Completed
- **Current State**: 
  - Agents are loaded from `personas.yaml` with full schedule parsing.
  - Positions are fully initialized.
  - Agents are linked to the world via `WorldManager.load_agents_with_schedules()`.
- **Completed**:
  - [x] Complete schedule parsing and application.
  - [x] Ensure positions are fully initialized.
  - [x] Finalize linking agents to the world.

### 3. Place Configuration Loading
- **Status**: Completed
- **Current State**: 
  - Place configuration schema defined in `schema_validation.py`.
  - Proper place loading implemented with capabilities, vendors, and neighbors.
  - Place connectivity validation implemented.
- **Completed**:
  - [x] Define and document place configuration schema
  - [x] Implement proper place loading with capabilities, vendors, and neighbors
  - [x] Validate place connectivity (neighbor relationships)

---

## 🟠 Medium Priority (Agent Behavior & Interaction)

### 4. Agent Decision Logic Enhancement
- **Status**: Completed
- **Current State**: 
  - `DecisionController` now consolidates all decision logic.
  - Includes rule-based, probabilistic, goal-driven, and context-aware decisions.
  - Time-of-day, location context, and social context are considered.
- **Completed**:
  - [x] Consolidate decision logic (merged `LogicController` and `DecisionController`)
  - [x] Add more nuanced rule-based triggers (time of day, location context, social context)
  - [x] Implement goal-driven decision making based on `persona.goals`
  - [x] Add personality-based decision modifiers using `persona.values`
- **TODO**:
  - [ ] Implement energy/hunger/stress decay over time

### 5. Action System Expansion
- **Status**: Completed
- **Current State**: 
  - Actions `WORK`, `SAY`, `INTERACT` fully implemented.
  - Action duration/cost modeling added via `ACTION_DURATIONS` and `ACTION_COSTS`.
  - Job-site validation for WORK action.
- **Completed**:
  - [x] Implement WORK action (with job-site validation)
  - [x] Implement SAY action (with audience targeting)
  - [x] Implement INTERACT action (object/agent interaction)
  - [x] Add action duration/cost modeling
- **TODO**:
  - [ ] Add action prerequisites (location, item requirements)

### 6. Agent Social Interaction
- **Status**: Stub
- **Current State**: 
  - `interaction.py` has `preference_to_interact()` model but it's not integrated
  - Conversation system exists but social relationship tracking is minimal
- **TODO**:
  - [ ] Integrate `preference_to_interact()` into agent decision-making
  - [ ] Implement relationship tracking (familiarity, trust, etc.)
  - [ ] Add social memory (remember past conversations/interactions)
  - [ ] Implement group conversation mechanics
  - [ ] Add conversation topic tracking
  - [ ] Implement social influence on agent decisions

### 7. Memory System Enhancement
- **Status**: Basic implementation
- **Current State**: 
  - MemoryStore supports episodic, semantic, autobio, tom kinds
  - Recall uses embedding similarity + recency decay
  - `compress_nightly()` is a stub
- **TODO**:
  - [ ] Implement proper memory consolidation (compress_nightly)
  - [ ] Add memory importance calculation from context
  - [ ] Implement Theory of Mind (ToM) memory usage
  - [ ] Add memory forgetting curve
  - [ ] Implement semantic memory extraction from episodic memories
  - [ ] Add memory search/filtering by kind

### 21. Dynamic Weather System
- **Status**: Proposed
- **Description**: Introduce weather effects (e.g., rain, snow) that influence agent behavior and place capabilities. For example, rain might reduce outdoor activities, while snow could increase indoor interactions.
- **TODO**:
  - [ ] Implement weather states and transitions.
  - [ ] Add weather effects on agent behavior.
  - [ ] Integrate weather with place capabilities.

### 22. Agent Relationships
- **Status**: Proposed
- **Description**: Track relationships between agents, including trust and familiarity. Relationships should influence interactions and decision-making.
- **TODO**:
  - [ ] Implement relationship tracking (e.g., familiarity, trust).
  - [ ] Add relationship-based decision modifiers.
  - [ ] Create events that influence relationships (e.g., arguments, collaborations).

---

## 🟡 Lower Priority (World & Economy)

### 8. Vendor/Commerce System
- **Status**: Partially Implemented
- **Current State**: 
  - Vendor-related logic exists, but `BUY` and `SELL` actions are not implemented.
  - Money tracking and stock replenishment are partially implemented.
- **TODO**:
  - [ ] Implement BUY action for agents
  - [ ] Implement SELL action for agents
  - [ ] Add money tracking (agents start with money item)
  - [ ] Implement vendor stock replenishment
  - [ ] Add price fluctuation mechanics
  - [ ] Implement agent-to-agent trading

### 9. Item Effects System
- **Status**: Stub
- **Current State**: 
  - Items have `effects` dict (e.g., coffee: energy +0.15, hunger -0.2)
  - Effects not automatically applied on use
- **TODO**:
  - [ ] Auto-apply item effects when used
  - [ ] Add effect duration (temporary vs permanent effects)
  - [ ] Implement compound effect interactions
  - [ ] Add skill/stat requirements for item usage

### 10. Inventory Stubs in inventory.py
- **Status**: Stub functions exist
- **Current State**: 
  - `interact_with_inventory()`, `interact_with_place()`, `interact_with_vendor()` are empty stubs
- **TODO**:
  - [ ] Implement or remove stub functions
  - [ ] Add inventory UI/display methods
  - [ ] Add inventory weight warnings

### 11. World State Persistence
- **Status**: Not implemented
- **Current State**: 
  - No save/load of world state during or after simulation
- **TODO**:
  - [ ] Implement world state serialization
  - [ ] Add checkpoint/resume capability
  - [ ] Save agent states (memory, inventory, position)
  - [ ] Save world events log

### 23. Simulation Metrics Dashboard
- **Status**: Proposed
- **Description**: Create a real-time dashboard to monitor simulation metrics such as agent activity, place usage, and event frequency.
- **TODO**:
  - [ ] Design a dashboard interface.
  - [ ] Implement real-time data collection.
  - [ ] Add visualization for key metrics.

---

## 🔵 Infrastructure & Quality

### 12. Schema Validation
- **Status**: Completed
- **Current State**: 
  - Complete schema definitions for city.yaml, personas.yaml, world.yaml, names.yaml
  - Validation integrated into WorldManager via `validate_config()` method
  - Helpful error messages with context for validation failures
- **Completed**:
  - [x] Define complete schemas for city.yaml, personas.yaml, world.yaml, names.yaml
  - [x] Integrate validation into WorldManager load methods
  - [x] Add helpful error messages for validation failures

### 13. Metrics & Logging Integration
- **Status**: Partial
- **Current State**: 
  - `SimulationMetrics` class exists but not integrated
  - `monitor.py` has logging hooks but they're not used
- **TODO**:
  - [ ] Integrate SimulationMetrics into simulation loop
  - [ ] Call monitor hooks during simulation
  - [ ] Add configurable logging levels
  - [ ] Implement metrics export (JSON/CSV)

### 14. Test Coverage
- **Status**: Improved
- **Current State**: 
  - Tests added for schema validation, actions, and decision controller
  - 42 tests total, all passing
- **Completed**:
  - [x] Add tests for schema validation
  - [x] Add tests for actions module
  - [x] Add tests for decision controller
- **TODO**:
  - [ ] Add tests for scheduler module
  - [ ] Add tests for memory recall/write
  - [ ] Add tests for inventory operations
  - [ ] Add integration tests for full simulation runs
  - [ ] Add LLM mocking for offline tests

### 15. Error Handling & Validation
- **Status**: Minimal
- **Current State**: 
  - Some ValueError raises exist
  - No comprehensive input validation
- **TODO**:
  - [ ] Add input validation to all public APIs
  - [ ] Improve error messages with context
  - [ ] Add graceful degradation for LLM failures
  - [ ] Implement retry logic for transient failures

---

## 🟣 Future/Advanced Features

### 16. LLM/Agent Behavior Layering
- **Status**: Future/Deferred
- **Current State**: 
  - Basic LLM conversation support exists
  - Hardcoded foundation still being built
- **TODO**:
  - [ ] Complete hardcoded foundation first
  - [ ] Design LLM intervention points (decision override, memory generation)
  - [ ] Implement configurable LLM vs rule-based ratio
  - [ ] Add LLM-generated goals/plans

### 17. Agent Learning/Adaptation
- **Status**: Stub mentioned in goals
- **Current State**: Goals mention "agent learning/adaptation stubs" as completed
- **TODO**:
  - [ ] Implement experience tracking
  - [ ] Add strategy updates based on outcomes
  - [ ] Implement skill progression

### 18. Multi-Agent Communication
- **Status**: Partial
- **Current State**: 
  - Broadcast exists but limited
  - No direct agent-to-agent messaging
- **TODO**:
  - [ ] Implement targeted messaging between agents
  - [ ] Add message queuing/history
  - [ ] Implement conversation threading

### 19. Time System
- **Status**: Basic
- **Current State**: 
  - Tick-based time exists
  - `TICK_MINUTES = 5` constant
  - `now_str()` for formatting
- **TODO**:
  - [ ] Add day/night cycle effects
  - [ ] Implement time-based capability changes (stores open/close)
  - [ ] Add weather/seasonal effects

### 20. World Events
- **Status**: Minimal
- **Current State**: 
  - `world.events` deque exists for logging
  - No random/scheduled world events
- **TODO**:
  - [ ] Implement random world events (weather, accidents, festivals)
  - [ ] Add event triggers (time-based, action-based)
  - [ ] Implement event effects on agents/places

---

## Active Tasks

This section tracks the current active tasks being worked on. Update this section whenever a new task is started or completed.

- **Task Name**: [Description of the task]
- **Status**: [In Progress/Completed]
- **Notes**: [Any additional notes or context]

---

## Summary by Category

| Category | Items | Priority |
|----------|-------|----------|
| Core Simulation | 3 | High |
| Agent Behavior | 6 | Medium |
| World/Economy | 4 | Lower |
| Infrastructure | 4 | Medium |
| Advanced | 5 | Future |

---

## Next Steps (Recommended Order)

1. **Agent Loading** - Complete WorldManager agent loading from config
2. **Simulation Loop Integration** - Wire up enforce_schedule properly
3. **Action System** - Implement missing actions (WORK, SAY, INTERACT)
4. **Decision Logic Consolidation** - Merge LogicController/DecisionController
5. **Schema Validation** - Add proper config validation
6. **Vendor System** - Enable commerce mechanics
7. **Metrics Integration** - Enable simulation analytics
8. **Test Coverage** - Add comprehensive tests

---

*Last updated: 2025-11-26*
*Generated from codebase analysis*
