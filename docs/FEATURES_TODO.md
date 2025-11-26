# Features & Mechanics To Be Implemented

This document catalogs all features and mechanics that need to be implemented or further defined for the llm-sim project. Items are organized by category and priority.

---

## 🔴 High Priority (Core Simulation Foundation)

### 1. Simulation Loop & Scheduler Integration
- **Status**: Partially implemented
- **Current State**: 
  - `World.simulation_loop()` exists but is basic
  - `enforce_schedule()` in `scheduler.py` is implemented but not fully integrated
  - `Agent.enforce_schedule()` exists but is not called in main simulation loop
- **TODO**:
  - [ ] Integrate `enforce_schedule` into the simulation loop so agents adhere to calendars
  - [ ] Add proper tick-based event sequencing
  - [ ] Implement appointment creation and management workflow
  - [ ] Handle conflicts between scheduled activities and agent decisions

### 2. Agent Loading from World Config
- **Status**: Stub/incomplete
- **Current State**: `WorldManager.run_world()` has `# TODO: Load agents and add to world._agents`
- **TODO**:
  - [ ] Implement proper agent instantiation from `personas.yaml`
  - [ ] Parse and apply agent schedules/calendars from config
  - [ ] Initialize agent positions from config
  - [ ] Link agents to world on load

### 3. Place Configuration Loading
- **Status**: Incomplete
- **Current State**: World loading doesn't properly parse places from city.yaml
- **TODO**:
  - [ ] Define and document place configuration schema
  - [ ] Implement proper place loading with capabilities, vendors, and neighbors
  - [ ] Validate place connectivity (neighbor relationships)

---

## 🟠 Medium Priority (Agent Behavior & Interaction)

### 4. Agent Decision Logic Enhancement
- **Status**: Basic implementation
- **Current State**: 
  - `DecisionController` has basic rule-based and probabilistic decisions
  - `LogicController` has similar logic but separate implementation
- **TODO**:
  - [ ] Consolidate decision logic (currently split between `LogicController` and `DecisionController`)
  - [ ] Add more nuanced rule-based triggers (time of day, location context, social context)
  - [ ] Implement goal-driven decision making based on `persona.goals`
  - [ ] Add personality-based decision modifiers using `persona.values`
  - [ ] Implement energy/hunger/stress decay over time

### 5. Action System Expansion
- **Status**: Partial
- **Current State**: 
  - `actions.py` defines ACTION_RE pattern for: SAY, MOVE, INTERACT, THINK, PLAN, SLEEP, EAT, WORK, CONTINUE
  - `Agent.act()` only handles: MOVE, EAT, SLEEP, RELAX, EXPLORE
- **TODO**:
  - [ ] Implement WORK action (with job-site validation)
  - [ ] Implement SAY action (with audience targeting)
  - [ ] Implement INTERACT action (object/agent interaction)
  - [ ] Implement PLAN action (schedule modification)
  - [ ] Implement THINK action (internal state update)
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

---

## 🟡 Lower Priority (World & Economy)

### 8. Vendor/Commerce System
- **Status**: Stub
- **Current State**: 
  - `Vendor` class exists with prices, stock, buyback
  - `has()` and `take()` methods exist
  - No purchase/sale agent actions implemented
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

---

## 🔵 Infrastructure & Quality

### 12. Schema Validation
- **Status**: Basic
- **Current State**: 
  - `schema_validation.py` has simple key/type validation
  - No schema definitions for config files
- **TODO**:
  - [ ] Define complete schemas for city.yaml, personas.yaml, world.yaml, names.yaml
  - [ ] Integrate validation into WorldManager load methods
  - [ ] Add helpful error messages for validation failures

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
- **Status**: Minimal
- **Current State**: 
  - Basic tests exist for agent behavior and scenarios
  - Many modules have no tests
- **TODO**:
  - [ ] Add tests for scheduler module
  - [ ] Add tests for memory recall/write
  - [ ] Add tests for inventory operations
  - [ ] Add tests for WorldManager
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

## Summary by Category

| Category | Items | Priority |
|----------|-------|----------|
| Core Simulation | 3 | High |
| Agent Behavior | 4 | Medium |
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
