

# Copilot Instructions for llm-sim

## Overview
**llm-sim** is a sandbox for simulating LLM-driven agents in a configurable city. Agents act, interact, and record memories each tick. Simulation is configured via YAML in `configs/`. Main entry: `scripts/run_sim.py`.

## Key Components
- **Agents**: See `sim/agents/agents.py`. Each agent has a persona, memory, physiological state, and decision logic. Actions: `SAY`, `INTERACT`, `MOVE`, etc.
- **World**: See `sim/world/world.py`. Places, events, and broadcasts. Places have capabilities and optional vendors.
- **Memory**: See `sim/memory/`. Agents store memories (`autobio`, `episodic`, `semantic`, `tom`).
- **LLM Integration**: See `sim/llm/`. Agents use LLMs for decision and conversation via `llm.chat_json`.

## Usage
- Setup: `python -m venv .venv` (Windows: `.venv\Scripts\activate`), then `pip install -r requirements.txt`.
- Run: `python scripts/run_sim.py` (see script for args).
- Logs: Output in `data/logs/`.
- Tests: In `tests/`.

## Patterns
- All speech: `SAY({"to":..., "text":...})`. Non-verbal: `INTERACT`. Movement: `MOVE({"to":...})`.
- Agents record memories after actions/conversations (`MemoryStore.write`).
- All actions are broadcast to the world (`World.broadcast`).
- YAML configs define city, places, personas, roles.
- Each tick = 5 minutes; agent states update per tick.
- Use `llm.chat_json` for structured LLM output.

## Extending
- Add agent: extend `Agent` and update YAML.
- Add place capability: update `ALLOWED_CAPS` and YAML.
- Change agent logic: modify `decide`/`act` in `Agent`.
- Add memory type: extend `MemoryItem`/`MemoryStore`.

## References
- Main: `scripts/run_sim.py`
- Agents: `sim/agents/agents.py`
- World: `sim/world/world.py`
- Configs: `configs/`
- Tests: `tests/`

_Update as codebase evolves. For questions, see README or key files._
