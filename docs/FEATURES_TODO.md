
# Features & Mechanics To Be Implemented

This document catalogs all features and mechanics that need to be implemented or further defined for the llm-sim project. Items are organized by category and priority.

---

## Feature-File Pairing Policy

For every feature marked as "in progress" (including skeleton or stub implementations), the feature entry must be explicitly paired with its main implementation file(s) in this document. This ensures traceability and clarity for ongoing work. Example:

- **Status**: In Progress
- **Main File(s)**: `sim/agents/needs.py`, `sim/agents/agents.py`

Update the feature entry as soon as work begins, and keep the file references current as the implementation evolves.

---

## 🚩 Top 10 Highest Priority Features (Recommended Order)

The following features are prioritized for efficient development, with foundational systems first and dependent features following:

1. **Needs System**
2. **Memory System Enhancement**
3. **Personality Modeling**
4. **Mood and Emotions**
5. **Agent Social Interaction**
6. **Social Memory and Relationships**
7. **Aging and Life Stages**
8. **Careers and Economy**
9. **Death and Consequences**
10. **World State Persistence**

See detailed descriptions in the sections below.

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
  - [ ] Add action duration/cost modeling
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
- **Status**: Completed (ToM deferred)
- **Main File(s)**: `sim/memory/memory.py`, `sim/agents/agents.py`
- **Current State**: 
  - MemoryStore supports episodic, semantic, autobio kinds (ToM removed)
  - Rule-based importance calculation, forgetting curve, and search/filter by kind implemented
  - Memory consolidation (compress_nightly) and semantic extraction from episodic implemented
  - ToM memory usage deferred to future LLM integration
- **Completed**:
  - [x] Implement proper memory consolidation (compress_nightly)
  - [x] Add memory importance calculation from context
  - [x] Add memory forgetting curve
  - [x] Implement semantic memory extraction from episodic memories
  - [x] Add memory search/filtering by kind
- **Deferred**:
  - [ ] Implement Theory of Mind (ToM) memory usage (defer to LLM)

### 24. Needs System
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/needs.py`, `sim/agents/agents.py`
- **Description**: System to manage agent needs such as hunger, energy, fun, social, etc., to drive behavior. (Skeleton: core data structures, decay, and rule-based logic implemented.)
- **TODO**:
  - [ ] Expand need types and effects
  - [ ] Add advanced need-driven behaviors
  - [ ] Integrate with more complex decision logic

### 25. Personality Modeling
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/personality.py`, `sim/agents/agents.py`
- **Description**: Traits, aspirations, and emotional modifiers added to differentiate agent behavior. (Skeleton: Big Five, aspirations, and modifiers present; basic integration in decision logic.)
- **TODO**:
  - [ ] Expand trait effects
  - [ ] Add more nuanced aspiration/emotion logic
  - [ ] Integrate with advanced decision-making

### 26. Mood and Emotions
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/mood.py`, `sim/agents/agents.py`
- **Description**: Moodlets and emotional states influence agent behavior. (Skeleton: moodlet/emotion structure and update logic present.)
- **TODO**:
  - [ ] Expand moodlet types and triggers
  - [ ] Integrate mood/emotion with more behaviors

### 27. Aging and Life Stages
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/aging.py`, `sim/agents/agents.py`
- **Description**: Agents progress through life stages (child, teen, adult, elder). (Skeleton: life stage and transition logic present.)
- **TODO**:
  - [ ] Add age-based effects and transitions
  - [ ] Integrate with agent decision logic

### 28. Death and Consequences
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/death.py`, `sim/agents/agents.py`
- **Description**: Mechanics for agent death and consequences (e.g., mourning). (Skeleton: alive/dead status, time of death, and stubs for mourning/legacy.)
- **TODO**:
  - [ ] Implement death conditions and triggers
  - [ ] Add mourning/legacy logic
  - [ ] Add effect duration (temporary vs permanent effects)

### 29. Careers and Economy
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/careers.py`, `sim/agents/agents.py`, `sim/inventory/economy.py`
- **Description**: Job system, income mechanics, and economic interactions. (Skeleton: job role, income, and stubs for job logic present.)
- **TODO**:
  - [ ] Implement job/career logic
  - [ ] Expand economic interactions
  - `interact_with_inventory()`, `interact_with_place()`, `interact_with_vendor()` are empty stubs

### 30. Social Memory and Relationships
- **Status**: Skeleton Implemented
- **Main File(s)**: `sim/agents/social.py`, `sim/agents/agents.py`
- **Description**: Track relationships between agents, including familiarity and trust. (Skeleton: relationship/social memory structures and stubs present.)
- **TODO**:
  - [ ] Expand relationship types and effects
  - [ ] Integrate with agent decision logic

### 31. Dynamic Weather System
- **Status**: Proposed
- **Description**: Introduce weather effects (e.g., rain, snow) that influence agent behavior and place capabilities.
- **TODO**:
  - [ ] Implement weather states and transitions.
  - [ ] Add weather effects on agent behavior.
  - [ ] Integrate weather with place capabilities.

### 32. World Events
- **Status**: Minimal
- **Description**: Add random and scheduled world events with effects on agents and places.
- **TODO**:
  - [ ] Implement random world events (e.g., weather, accidents, festivals).
  - [ ] Add event triggers (time-based, action-based).
  - [ ] Implement event effects on agents/places.

### 33. World State Persistence
- **Status**: Not Implemented
- **Description**: Enable saving and loading of the simulation state.
- **TODO**:
  - [ ] Implement world state serialization.
  - [ ] Add checkpoint/resume capability.
  - [ ] Save agent states (memory, inventory, position).
  - [ ] Save world events log.

### 34. Simulation Metrics Dashboard
- **Status**: Proposed
- **Description**: Create a real-time dashboard to monitor simulation metrics such as agent activity, place usage, and event frequency.
- **TODO**:
  - [ ] Design a dashboard interface.
  - [ ] Implement real-time data collection.
  - [ ] Add visualization for key metrics.

---

## 🟡 Lower Priority (World & Economy)


### 8. Vendor/Commerce System
- **Status**: Completed
- **Current State**: 
  - Vendor-related logic, agent BUY/SELL actions, money tracking, stock replenishment, price fluctuation, and agent-to-agent trading are fully implemented and integrated.

---

## 🟢 Proposed Feature Expansions (Commerce & Economy)

### 35. Dynamic Supply & Demand Economy
- **Status**: Proposed
- **Description**: Prices fluctuate based on local/global supply and demand for goods. Vendors and agents adjust prices and trading behavior in response to scarcity, surplus, or trends.
- **TODO**:
  - [ ] Track item quantities and recent transaction volumes
  - [ ] Adjust prices algorithmically

### 36. Agent Specialization & Professions
- **Status**: Proposed
- **Description**: Assign agents roles (e.g., farmer, blacksmith, merchant) with unique production, consumption, and trading patterns. Professions influence what agents buy, sell, and produce, creating interdependencies.
- **TODO**:
  - [ ] Extend agent attributes and schedules
  - [ ] Add profession-based production/consumption logic

### 37. Production Chains & Resource Transformation
- **Status**: Proposed
- **Description**: Enable agents or vendors to convert raw materials into finished goods (e.g., wheat → bread). Multi-step production chains encourage complex trading and cooperation.
- **TODO**:
  - [ ] Define recipes and production actions
  - [ ] Allow agents to seek required inputs

### 38. Barter System & Currency Alternatives
- **Status**: Proposed
- **Description**: Allow agents to negotiate trades without currency if mutually beneficial (barter). Introduce alternative currencies or trade tokens for certain regions or groups.
- **TODO**:
  - [ ] Expand TRADE action logic to support item-for-item deals and negotiation

### 39. Agent Reputation & Trust
### 24. Needs System
- **Status**: Skeleton Implemented
- **Description**: System to manage agent needs such as hunger, energy, fun, social, etc., to drive behavior. (Skeleton: core data structures, decay, and rule-based logic implemented.)
- **TODO**:
  - [ ] Expand need types and effects
  - [ ] Add advanced need-driven behaviors
  - [ ] Integrate with more complex decision logic
### 40. Black Market & Illicit Trade
### 25. Personality Modeling
- **Status**: Skeleton Implemented
- **Description**: Traits, aspirations, and emotional modifiers added to differentiate agent behavior. (Skeleton: Big Five, aspirations, and modifiers present; basic integration in decision logic.)
- **TODO**:
  - [ ] Expand trait effects
  - [ ] Add more nuanced aspiration/emotion logic
  - [ ] Integrate with advanced decision-making
### 41. Economic Events & Shocks
### 26. Mood and Emotions
- **Status**: Skeleton Implemented
- **Description**: Moodlets and emotional states influence agent behavior. (Skeleton: moodlet/emotion structure and update logic present.)
- **TODO**:
  - [ ] Expand moodlet types and triggers
  - [ ] Integrate mood/emotion with more behaviors
### 42. Vendor/Shop Upgrades & Expansion
### 27. Aging and Life Stages
- **Status**: Skeleton Implemented
- **Description**: Agents progress through life stages (child, teen, adult, elder). (Skeleton: life stage and transition logic present.)
- **TODO**:
  - [ ] Add age-based effects and transitions
  - [ ] Integrate with agent decision logic
### 9. Item Effects System
### 28. Death and Consequences
- **Status**: Skeleton Implemented
- **Description**: Mechanics for agent death and consequences (e.g., mourning). (Skeleton: alive/dead status, time of death, and stubs for mourning/legacy.)
- **TODO**:
  - [ ] Implement death conditions and triggers
  - [ ] Add mourning/legacy logic
  - [ ] Add effect duration (temporary vs permanent effects)
### 29. Careers and Economy
- **Status**: Skeleton Implemented
- **Description**: Job system, income mechanics, and economic interactions. (Skeleton: job role, income, and stubs for job logic present.)
- **TODO**:
  - [ ] Implement job/career logic
  - [ ] Expand economic interactions
  - `interact_with_inventory()`, `interact_with_place()`, `interact_with_vendor()` are empty stubs
### 30. Social Memory and Relationships
- **Status**: Skeleton Implemented
- **Description**: Track relationships between agents, including familiarity and trust. (Skeleton: relationship/social memory structures and stubs present.)
- **TODO**:
  - [ ] Expand relationship types and effects
  - [ ] Integrate with agent decision logic
- **Status**: Not implemented
### 33. World State Persistence
- **Status**: Skeleton Implemented
- **Description**: Enable saving and loading of the simulation state. (Skeleton: agent state serialization/loading/checkpoint stubs present.)
- **TODO**:
  - [ ] Implement full world/agent serialization
  - [ ] Add checkpoint/resume logic
  - [ ] Save/load world events log

### 7. Memory System Enhancement
- **Status**: Skipped
- **Current State**: 
  - Skipped for now; revisit after other skeletons are complete.
- **TODO**:
  - [ ] Resume work on memory system after core skeletons
  - [x] Integrate validation into WorldManager load methods
  - [x] Add helpful error messages for validation failures

### 13. Metrics & Logging Integration
- **Status**: Completed
- **Current State**: 
  - SimulationMetrics fully integrated into simulation loop
  - Monitor hooks called during simulation with configurable logging
  - Metrics export available in JSON and CSV formats
- **Implementation Details**:
  - [x] Integrate SimulationMetrics into simulation loop
  - [x] Call monitor hooks during simulation
  - [x] Add configurable logging levels
  - [x] Implement metrics export (JSON/CSV)

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

1. **Needs System**
2. **Memory System Enhancement**
3. **Personality Modeling**
4. **Mood and Emotions**
5. **Agent Social Interaction**
6. **Social Memory and Relationships**
7. **Aging and Life Stages**
8. **Careers and Economy**
9. **Death and Consequences**
10. **World State Persistence**

---

*Last updated: 2025-11-30*
