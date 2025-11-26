---
description: Project-wide Copilot custom instructions for llm-sim workspace.
name: llm-sim_Copilot_Instructions
description: Project-wide Copilot custom instructions for llm-sim workspace.
name: llm-sim_Copilot_Instructions
# General Coding Guidelines

# llm-sim Copilot Instructions

#always refer to PROJECT_GOAL.md for overall project goals and vision.
#next refer to goals/goal_and_next_steps.instructions.md for current goal task and upcoming features or changes with their priorities.
# Always update goal_and_next_steps.instructions.md with current goal and new features or changes.

## Big Picture Architecture

- **Modular Simulation Engine:** Core logic is split across `sim/` submodules: `agents`, `actions`, `memory`, `scheduler`, `inventory`, `llm`, and `world`. Each module encapsulates a distinct simulation concern.
- **World Management:** Worlds are compartmentalized in `worlds/`, each with its own YAML configs (`city.yaml`, `personas.yaml`, `names.yaml`, `world.yaml`) and logs. The `WorldManager` (`sim/world/world_manager.py`) handles all file I/O and data loading for worlds.
- **Agents:** Defined in `sim/agents/agents.py` as `Agent`, `Persona`, and `Physio` classes. Agents interact with the world, make decisions, and store episodic/semantic memories (`sim/memory/memory.py`).
- **LLM Integration:** All LLM calls use the Ollama backend via `sim/llm/llm_ollama.py`. No fallback to other LLMs; raise errors if not configured.
- **Actions:** Canonical agent/system actions are normalized via `sim/actions/actions.py` using a DSL string format (e.g., `SAY()`, `MOVE({"to":"place"})`).
- **Scheduling:** Agent schedules and time-based movement are managed by `sim/scheduler/scheduler.py`.

## Developer Workflows

- **Setup:** Use `python -m venv .venv && .venv\Scripts\activate` (Windows) and `pip install -r requirements.txt`.
- **Run Simulation:** `python scripts/run_sim.py` or use CLI: `python scripts/world_cli.py run World_0 --ticks 100`.
- **World Management:** Use `scripts/world_cli.py` for creating, listing, info, deleting, and running worlds. Example: `python scripts/world_cli.py create World_1 --city "New City" --year 2025`.
- **Testing:** Automated tests are planned for all core modules in `sim/` and user-facing scripts in `scripts/`. (See `.github/goals/next_steps.instructions.md` for progress.)
- **Data Validation:** All config/data files (YAML/JSON) should have schemas enforced via logic in `WorldManager` and data loaders.

## Project-Specific Conventions

- **Docstrings:** All Python scripts must start with a multi-line docstring describing purpose, key functions/classes, LLM usage, and CLI arguments.
- **No LLM Fallback:** Do not implement or inject LLM fallback behavior; raise clear errors if no LLM is configured.
- **File Operations:** Always prompt for confirmation before moving or deleting files.
- **Ignore Outputs:** Do not read or write to `outputs/` unless explicitly instructed.
- **PEP 8:** Use PEP 8 style guide for all Python code.
- **Descriptive Naming:** Prioritize clarity and descriptive names for all functions, classes, and variables.

## Integration Points & Patterns

- **External Dependencies:** Only `requests` and `PyYAML` are required (see `requirements.txt`).
- **Cross-Component Communication:** All agent/world interactions are routed through the `WorldManager` and agent classes. LLM calls are centralized in `sim/llm/llm_ollama.py`.
- **Logging & Metrics:** Logging for simulation runs, agent actions, and world events is planned but not yet implemented.

## Key Files & Directories

- `sim/`: Core simulation modules.
- `scripts/`: CLI tools and utilities.
- `worlds/`: Example worlds and scenario templates.
- `configs/`: Data schemas and config files.
- `.github/goals/next_steps.instructions.md`: Roadmap and feature progress.

---

**Example Workflow:**
1. Create a world: `python scripts/world_cli.py create World_1 --city "New City" --year 2025`
2. Run simulation: `python scripts/world_cli.py run World_1 --ticks 100`
3. Inspect agent memories: See `sim/memory/memory.py` for API.

---

Please review and suggest any missing or unclear sections for further iteration.

# Autonomous Copilot Instructions Update

- Always keep `.github/instructions/goals/goal_and_next_steps.instructions.md` updated and relevant at every development step.
- After each change to simulation internals, data structures, or logic, append the new goal, next step, or architectural decision to the goals file (do not remove previous content).
- Use the goals file as the authoritative source for current development focus and priorities.
- Continue development autonomously, referring to the goals file for direction and updating it as progress is made.

- The global outline/roadmap file is `.github/roadmap.md`. All current, future, and completed features, goals, and tasks must be tracked here with their creation and/or completion dates.
- Update `.github/roadmap.md` at every major development step, ensuring it reflects the latest project state and priorities.

# Hierarchical Goals and Tasks Organization

- Organize all goals and tasks in `.github/instructions/goals/goal_and_next_steps.instructions.md` hierarchically, using nested lists and headings for main goals, subgoals, and actionable steps.
- Each major goal should have clearly defined subgoals and tasks beneath it, with indentation or bullet points to show structure.
- When updating, always append new steps or changes under the appropriate section, maintaining the hierarchy.
- Use the hierarchical structure to clarify dependencies, priorities, and progress.
- Each major goal should have an emoji prefix to enhance visual scanning and organization. Checkmarks (✅) for completed goals, empty boxes (⬜) for current goals, and other relevant emojis for future or suspended goals.
- Completed goals should be moved to a "Completed Development Tasks/Goals" section at the bottom, with dates and brief descriptions of what was accomplished.
- NEVER remove data from this file; always append new information or reorder/update current information to maintain a full history of development progress and decisions.

- Always ensure goal hygiene by removing outdated goals and modifying them to reference and use current code, systems, and classes.

- ONLY if an error cannot be resolved within 5 steps, document it in `.github/instructions/problems.md` and move on to the next task or goal. Apply the same hygiene rules to the problems file (remove outdated problems, modify them to reflect current systems/code).
- Periodically review documented problems to check if they have become more tractable or solvable due to recent development progress.
