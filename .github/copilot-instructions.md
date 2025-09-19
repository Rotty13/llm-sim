# Copilot Instructions for llm-sim

## Project Overview
- **llm-sim** is a sandbox for simulating LLM-driven agents in a configurable city environment. Agents make decisions, interact, and write memories each tick.
- The simulation is configured via YAML files in `configs/` (e.g., `world.yaml`, `personas.yaml`).
- Main entry point: `scripts/run_sim.py`.

## Architecture & Key Components
- **Agents** (`sim/agents/agents.py`): Each agent has a persona, memory, physiological state, and decision logic. Actions include MOVE, INTERACT, SAY, EAT, WORK, PLAN, SLEEP.
- **World** (`sim/world/world.py`): Contains places, events, and manages broadcasts. Places have capabilities and optional vendors.
- **Memory** (`sim/memory/`): Agents store memories of different types (autobio, episodic, semantic, tom).
- **Actions** (`sim/actions/`): Defines and normalizes agent actions.
- **LLM Integration** (`sim/llm/`): Agents use LLMs for decision-making and conversation.
- **Scheduler, Inventory**: Support agent planning and item management.

## Developer Workflows
- **Setup**: `python -m venv .venv` (Windows: `.venv\Scripts\activate`), then `pip install -r requirements.txt`.
- **Run Simulation**: `python scripts/run_sim.py` (accepts `--world`, `--personas`, `--ticks`, `--logdir` args).
- **Logs**: Output logs and memory summaries are written to `data/logs/`.
- **Testing**: Unit tests are in `sim/tests/` (e.g., `test_agents.py`, `test_llm.py`).

## Project-Specific Patterns
- **Agent Actions**: All speech must use `SAY({"to":..., "text":...})`. Non-verbal actions use `INTERACT`. Movement uses `MOVE({"to":...})`.
- **Memory Writes**: Agents record memories after actions and conversations.
- **Event Broadcasts**: All agent actions are broadcast to the world and logged as events.
- **YAML Configs**: City, places, personas, and roles are defined in YAML files under `configs/`.
- **Tick-Based Simulation**: Each tick represents 5 minutes; agent states update per tick.

## Integration Points
- **LLM Calls**: Decision and conversation logic use LLMs via `llm.chat_json`.
- **External Dependencies**: Only `requests` and `PyYAML` are required (see `requirements.txt`).

## Example Patterns
- To add a new agent type, extend `Agent` in `sim/agents/agents.py` and update YAML configs.
- To add new place capabilities, update `ALLOWED_CAPS` in `sim/world/world.py` and relevant YAML.
- To change agent decision logic, modify `decide` and `act` methods in `Agent`.

## References
- Main simulation: `scripts/run_sim.py`
- Agent logic: `sim/agents/agents.py`
- World logic: `sim/world/world.py`
- Configs: `configs/`
- Tests: `sim/tests/`

---
_Review and update these instructions as the codebase evolves. For questions, see the README or key source files._
